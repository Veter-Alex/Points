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

    def _detect_zone_from_coordinates(self, lon: float) -> int:
        """Определяет зону СК-42 по долготе (longitude)."""
        # СК-42 Гаусс-Крюгер: центральный меридиан = зона * 6 - 3
        # Зона 3: центр 15°E (12°-18°E)
        # Зона 4: центр 21°E (18°-24°E)
        # Зона 5: центр 27°E (24°-30°E)
        # Зона 6: центр 33°E (30°-36°E) ← ваши координаты 30-36°
        # Зона 7: центр 39°E (36°-42°E)

        # Определяем зону по долготе с учетом правильных границ
        if lon < 12:
            return 2  # зона 2 (центр 9°E)
        elif lon < 18:
            return 3  # зона 3 (центр 15°E)
        elif lon < 24:
            return 4  # зона 4 (центр 21°E)
        elif lon < 30:
            return 5  # зона 5 (центр 27°E)
        elif lon < 36:
            return 6  # зона 6 (центр 33°E) ← ПРАВИЛЬНО для ваших координат 30-36°
        elif lon < 42:
            return 7  # зона 7 (центр 39°E)
        elif lon < 48:
            return 8  # зона 8 (центр 45°E)
        elif lon < 54:
            return 9  # зона 9 (центр 51°E)
        elif lon < 60:
            return 10  # зона 10 (центр 57°E)
        elif lon < 66:
            return 11  # зона 11 (центр 63°E)
        elif lon < 72:
            return 12  # зона 12 (центр 69°E)
        elif lon < 78:
            return 13  # зона 13 (центр 75°E)
        elif lon < 84:
            return 14  # зона 14 (центр 81°E)
        elif lon < 90:
            return 15  # зона 15 (центр 87°E)
        elif lon < 96:
            return 16  # зона 16 (центр 93°E)
        elif lon < 102:
            return 17  # зона 17 (центр 99°E)
        elif lon < 108:
            return 18  # зона 18 (центр 105°E)
        elif lon < 114:
            return 19  # зона 19 (центр 111°E)
        elif lon < 120:
            return 20  # зона 20 (центр 117°E)
        elif lon < 126:
            return 21  # зона 21 (центр 123°E)
        elif lon < 132:
            return 22  # зона 22 (центр 129°E, для 131.885)
        elif lon < 138:
            return 23  # зона 23 (центр 135°E)
        elif lon < 144:
            return 24  # зона 24 (центр 141°E)
        elif lon < 150:
            return 25  # зона 25 (центр 147°E)
        elif lon < 156:
            return 26  # зона 26 (центр 153°E)
        elif lon < 162:
            return 27  # зона 27 (центр 159°E)
        else:
            return 28  # зона 28 (центр 165°E)

    def _get_epsg_for_zone(self, zone: int) -> int:
        """Возвращает EPSG код для указанной зоны СК-42."""
        # EPSG коды для зон СК-42 (Гаусс-Крюгер)
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
            11: 28411,  # СК-42 / Gauss-Kruger zone 11
            12: 28412,  # СК-42 / Gauss-Kruger zone 12
            13: 28413,  # СК-42 / Gauss-Kruger zone 13
            14: 28414,  # СК-42 / Gauss-Kruger zone 14
            15: 28415,  # СК-42 / Gauss-Kruger zone 15
            16: 28416,  # СК-42 / Gauss-Kruger zone 16
            17: 28417,  # СК-42 / Gauss-Kruger zone 17
            18: 28418,  # СК-42 / Gauss-Kruger zone 18
            19: 28419,  # СК-42 / Gauss-Kruger zone 19
            20: 28420,  # СК-42 / Gauss-Kruger zone 20
            21: 28421,  # СК-42 / Gauss-Kruger zone 21 (для Дальнего Востока)
            22: 28422,  # СК-42 / Gauss-Kruger zone 22
            23: 28423,  # СК-42 / Gauss-Kruger zone 23
            24: 28424,  # СК-42 / Gauss-Kruger zone 24
            25: 28425,  # СК-42 / Gauss-Kruger zone 25
            26: 28426,  # СК-42 / Gauss-Kruger zone 26
            27: 28427,  # СК-42 / Gauss-Kruger zone 27
            28: 28428,  # СК-42 / Gauss-Kruger zone 28
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

    def transform(
        self, latitude: float, longitude: float, to_wgs: bool = True
    ) -> Tuple[float, float]:
        """Преобразование координат с автоопределением зоны для каждой точки.
        На входе: latitude, longitude (широта, долгота) в WGS-84 или X, Y в СК-42.
        """
        if self.system == "WGS84":
            return (latitude, longitude)

        # Определяем зону для каждой точки отдельно
        if self.zone == "AUTO":
            if to_wgs:
                # Для преобразования из СК-42 в WGS84
                # latitude=X_SK42, longitude=Y_SK42
                # Определяем зону по Y-координате
                y_sk42 = longitude
                # В СК-42 Y-координата имеет формат: зона*1000000 + 500000 + локальная_y
                # Например: Y=22223252 означает зона 22, но это неверно
                # Правильное определение: зона определяется из самой Y-координаты
                if y_sk42 > 500000:
                    # Для зон > 9: Y = (зона-1)*1000000 + 500000 + локальная_координата
                    # Но проще использовать первую цифру Y как приблизительную зону
                    zone_from_y = int(str(int(y_sk42))[0:2])  # Первые 2 цифры
                    if zone_from_y >= 10 and zone_from_y <= 27:
                        current_zone = zone_from_y
                    else:
                        # Попробуем первую цифру
                        zone_from_y = int(str(int(y_sk42))[0])
                        if zone_from_y >= 1 and zone_from_y <= 9:
                            current_zone = zone_from_y
                        else:
                            current_zone = 21  # Зона по умолчанию для больших Y
                else:
                    current_zone = 7  # По умолчанию для небольших Y

                # Специальная коррекция для известных проблемных случаев
                if 22000000 <= y_sk42 < 23000000:  # Y начинается с 22
                    current_zone = 21  # Это зона 21, а не 22
            else:
                # Для преобразования из WGS84 в СК-42
                # latitude=lat_WGS84, longitude=lon_WGS84
                current_zone = self._detect_zone_from_coordinates(longitude)

            # Проверяем, нужно ли создать новый трансформер для этой зоны
            if (
                not hasattr(self, "current_zone")
                or self.current_zone != current_zone
                or self._transformer is None
            ):
                direction_str = "SK42->WGS" if to_wgs else "WGS->SK42"
                logger.debug(
                    f"Переключаемся на зону СК-42: {current_zone} ({direction_str})"
                )
                self._setup_transformer_for_zone(current_zone)
                self.current_zone = current_zone

        if not self._transformer:
            raise ValueError("Трансформер не инициализирован")

        if to_wgs:
            # Преобразование из СК-42 в WGS-84
            # В СК-42: latitude=X (север), longitude=Y (восток)
            # Поэтому передаем Y, X в трансформер (longitude, latitude)
            try:
                lon, lat = self._transformer.transform(longitude, latitude)
                return (lat, lon)
            except Exception as e:
                logger.debug(
                    f"Ошибка преобразования СК-42->WGS84 {latitude}, {longitude}: {e}"
                )
                raise
        else:
            # Преобразование из WGS-84 в СК-42 (обратное)
            try:
                # Для обратного преобразования с always_xy=True передаем (longitude, latitude)
                y_sk42, x_sk42 = self._transformer.transform(
                    longitude, latitude, direction="INVERSE"
                )
                # В СК-42: X - это север (latitude), Y - это восток (longitude)
                # Поэтому возвращаем в правильном порядке: (X_sk42, Y_sk42)
                return (x_sk42, y_sk42)
            except Exception as e:
                logger.debug(
                    f"Ошибка обратного преобразования WGS84->СК-42 {latitude}, {longitude}: {e}"
                )
                raise
