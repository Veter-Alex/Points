import logging
import math
from typing import Any, Dict, List, Optional, Tuple

from pyproj import CRS, Transformer

from src.logger import logger


class CoordinateTransformer:
    """Преобразование координат между системами (SK42 <-> WGS84)."""

    def __init__(self, system: str = "SK42_GAUSS_KRUGER", zone: str = "AUTO"):
        self.system = system
        self.zone = zone
        self._transformer: Any = None
        self.current_zone: Optional[int] = None
        self._init_transformer()

    def _detect_zone_from_coordinates(self, y_coord: float) -> int:
        """Определяет зону СК-42 по Y-координате."""
        # Y-координата в СК-42 содержит номер зоны в первой цифре
        # Например: 6480536 -> зона 6, 7480536 -> зона 7
        if y_coord > 1000000:
            zone = int(str(int(y_coord))[0])
            return zone
        return 7  # По умолчанию зона 7

    def _get_epsg_for_zone(self, zone: int) -> int:
        """Возвращает EPSG код для указанной зоны СК-42."""
        # EPSG коды для зон СК-42
        zone_epsg = {
            1: 28401,  # СК-42 / Gauss-Kruger zone 1
            2: 28402,  # СК-42 / Gauss-Kruger zone 2
            3: 28403,  # СК-42 / Gauss-Kruger zone 3
            4: 28404,  # СК-42 / Gauss-Kruger zone 4
            5: 28405,  # СК-42 / Gauss-Kruger zone 5
            6: 28406,  # СК-42 / Gauss-Kruger zone 6
            7: 28407,  # СК-42 / Gauss-Kruger zone 7
            8: 28408,  # СК-42 / Gauss-Kruger zone 8
            9: 28409,  # СК-42 / Gauss-Kruger zone 9
            10: 28410,  # СК-42 / Gauss-Kruger zone 10
        }
        return zone_epsg.get(zone, 28407)  # По умолчанию зона 7

    def _init_transformer(self):
        """Инициализация трансформера."""
        if self.system == "WGS84":
            self._transformer = None
        else:
            # Определяем зону автоматически или используем указанную
            if self.zone == "AUTO":
                # Будем определять зону при первом преобразовании
                self.detected_zone = None
                self._transformer = None
            else:
                zone_num = int(self.zone) if self.zone.isdigit() else 7
                self._setup_transformer_for_zone(zone_num)

    def _setup_transformer_for_zone(self, zone: int):
        """Настраивает трансформер для указанной зоны."""
        try:
            epsg_code = self._get_epsg_for_zone(zone)
            sk42_crs = CRS.from_epsg(epsg_code)
            wgs84_crs = CRS.from_epsg(4326)

            self._transformer = Transformer.from_crs(
                sk42_crs, wgs84_crs, always_xy=True
            )
            logger.debug(f"Создан трансформер для СК-42 зона {zone} (EPSG:{epsg_code})")

        except Exception as e:
            logger.debug(f"Ошибка создания трансформера для зоны {zone}: {e}")
            # Fallback к proj4 строке для зоны 7
            sk42_proj4 = "+proj=tmerc +lat_0=0 +lon_0=39 +k=1 +x_0=7500000 +y_0=0 +ellps=krass +towgs84=23.57,-140.95,-79.8,0,0.35,0.79,-0.22 +units=m +no_defs"

            self._transformer = Transformer.from_crs(
                CRS.from_proj4(sk42_proj4), CRS.from_epsg(4326), always_xy=True
            )
            logger.debug("Создан трансформер через proj4 (зона 7 по умолчанию)")

    def transform(self, x: float, y: float, to_wgs: bool = True) -> Tuple[float, float]:
        """Преобразование координат с автоопределением зоны для каждой точки."""
        if self.system == "WGS84":
            return (x, y)

        # Определяем зону для каждой точки отдельно
        if self.zone == "AUTO":
            current_zone = self._detect_zone_from_coordinates(y)

            # Проверяем, нужно ли создать новый трансформер для этой зоны
            if (
                not hasattr(self, "current_zone")
                or self.current_zone != current_zone
                or self._transformer is None
            ):

                logger.debug(f"Переключаемся на зону СК-42: {current_zone} (по Y={y})")
                self._setup_transformer_for_zone(current_zone)
                self.current_zone = current_zone

        if not self._transformer:
            raise ValueError("Трансформер не инициализирован")

        if to_wgs:
            # Преобразование из СК-42 в WGS-84
            # В СК-42: x - это север (широта), y - это восток (долгота)
            # Поэтому передаем y, x в трансформер
            try:
                lon, lat = self._transformer.transform(y, x)
                return (lon, lat)
            except Exception as e:
                logger.debug(f"Ошибка преобразования {x}, {y}: {e}")
                raise
        else:
            # Преобразование из WGS-84 в СК-42 (обратное)
            try:
                y_sk42, x_sk42 = self._transformer.transform(x, y, direction="INVERSE")
                return (x_sk42, y_sk42)
            except Exception as e:
                logger.debug(f"Ошибка обратного преобразования {x}, {y}: {e}")
                raise
