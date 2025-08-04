"""
Модуль для работы с городами.
Содержит функции поиска городов и формирования описаний районов.
"""

import math
from typing import List, Optional

from models.city import CityRecord


def find_city_by_name(
    records: List[CityRecord], city_name: Optional[str]
) -> Optional[CityRecord]:
    """
    Найти город по названию в списке записей.

    Args:
        records (List[CityRecord]): Список записей городов
        city_name (Optional[str]): Название города для поиска

    Returns:
        Optional[CityRecord]: Найденная запись города или None
    """
    if not city_name:
        return None
    for record in records:
        name_ru = record.name_ru if record.name_ru else ""
        name_original = record.name_original if record.name_original else ""
        if (
            name_ru.lower() == city_name.lower()
            or name_original.lower() == city_name.lower()
        ):
            return record
    return None


def get_area_desc(
    found_city: CityRecord,
    result_parse_xml: object,
    x_sk42: Optional[int],
    y_sk42: Optional[int],
) -> str:
    """
    Формирует описание района на основе найденного города и координат точки.

    Args:
        found_city (CityRecord): Найденный город
        result_parse_xml (object): Результат парсинга XML с координатами
        x_sk42 (Optional[int]): Координата X в СК-42
        y_sk42 (Optional[int]): Координата Y в СК-42

    Returns:
        str: Описание района
    """

    def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Вычисляет расстояние между двумя точками на Земле по формуле гаверсинусов.

        Args:
            lat1, lon1 (float): Координаты первой точки
            lat2, lon2 (float): Координаты второй точки

        Returns:
            float: Расстояние в километрах
        """
        R = 6371.0
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)
        a = (
            math.sin(dphi / 2) ** 2
            + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    def get_direction(lat1: float, lon1: float, lat2: float, lon2: float) -> str:
        """
        Определяет направление от первой точки ко второй.

        Args:
            lat1, lon1 (float): Координаты первой точки
            lat2, lon2 (float): Координаты второй точки

        Returns:
            str: Направление на русском языке
        """
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        angle = math.degrees(math.atan2(dlon, dlat))
        dirs = [
            (11.25, "севернее"),
            (33.75, "северо-восточнее"),
            (56.25, "северо-восточнее"),
            (78.75, "северо-восточнее"),
            (101.25, "восточнее"),
            (123.75, "юго-восточнее"),
            (146.25, "юго-восточнее"),
            (168.75, "юго-восточнее"),
            (191.25, "южнее"),
            (213.75, "юго-западнее"),
            (236.25, "юго-западнее"),
            (258.75, "юго-западнее"),
            (281.25, "западнее"),
            (303.75, "северо-западнее"),
            (326.25, "северо-западнее"),
            (348.75, "северо-западнее"),
            (360.0, "севернее"),
        ]
        angle = (angle + 360) % 360
        for bound, name in dirs:
            if angle < bound:
                return name
        return "севернее"

    # Предполагаем, что result_parse_xml содержит атрибуты lat и lon
    latitude = getattr(result_parse_xml, "latitude", None)
    longitude = getattr(result_parse_xml, "longitude", None)
    if latitude is None or longitude is None:
        return "error: result_parse_xml missing latitude/longitude"

    distance = haversine(
        found_city.latitude,
        found_city.longitude,
        latitude,
        longitude,
    )
    direction = get_direction(
        found_city.latitude,
        found_city.longitude,
        latitude,
        longitude,
    )

    # Форматирование координат с проверкой на None
    coord_str = f"координаты: X={x_sk42 or 'N/A'} Y={y_sk42 or 'N/A'}"

    if distance <= 2:
        if found_city.description is None:
            return f"район {found_city.name_ru} ({coord_str})"
        else:
            return f"район {found_city.name_ru} ({found_city.description}, {coord_str})"
    elif distance > 2:
        if found_city.description is None:
            return f"район {distance:.1f} км {direction} {found_city.name_ru} ({coord_str})"
        else:
            return f"район {distance:.1f} км {direction} {found_city.name_ru} ({found_city.description}, {coord_str})"
    return "error in get_area_desc"
