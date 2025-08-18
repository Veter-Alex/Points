

"""
Модуль для работы с городами.

Содержит функции поиска города по названию и формирования описания района по координатам.
Все функции снабжены подробными комментариями и докстрингами согласно лучшим практикам.
"""


import math
from typing import List, Optional, Any
from models.city import CityRecord




def find_city_by_name(records: List[CityRecord], city_name: Optional[str]) -> Optional[CityRecord]:
    """
    Поиск города по названию (русское или оригинальное) без учёта регистра.

    Args:
        records (List[CityRecord]): Список записей городов.
        city_name (Optional[str]): Название города для поиска.

    Returns:
        Optional[CityRecord]: Найденная запись города или None, если не найдено.
    """
    if not city_name:
        return None
    city_name = city_name.lower()
    # Перебираем все записи и сравниваем название города без учета регистра
    for record in records:
        if record.name_original and record.name_original.lower() == city_name:
            return record
    return None




def get_area_desc(
    found_city: CityRecord,
    result_parse_xml: Any,
    x_sk42: Optional[int],
    y_sk42: Optional[int],
) -> str:
    """
    Формирует описание района на основе найденного города и координат точки.

    Args:
        found_city (CityRecord): Найденный город.
        result_parse_xml (Any): Результат парсинга файла с координатами точки.
        x_sk42 (Optional[int]): Координата X в системе СК-42.
        y_sk42 (Optional[int]): Координата Y в системе СК-42.

    Returns:
        str: Описание района для отчета.
    """
    def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Вычисляет расстояние между двумя точками по координатам (км).
        """
        R = 6371.0
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)
        a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
        return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    def get_direction(lat1: float, lon1: float, lat2: float, lon2: float) -> str:
        """
        Определяет направление от города к точке по азимуту.
        """
        angle = (math.degrees(math.atan2(lon2 - lon1, lat2 - lat1)) + 360) % 360
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
        for bound, name in dirs:
            if angle < bound:
                return name
        return "севернее"

    # Получаем координаты точки
    latitude = getattr(result_parse_xml, "latitude", None)
    longitude = getattr(result_parse_xml, "longitude", None)
    if latitude is None or longitude is None:
        return "error: result_parse_xml missing latitude/longitude"

    # Вычисляем расстояние и направление от города к точке
    distance = haversine(found_city.latitude, found_city.longitude, latitude, longitude)
    direction = get_direction(found_city.latitude, found_city.longitude, latitude, longitude)
    
    # Форматируем координаты X и Y как целые числа
    x_str = f"{int(x_sk42)}" if x_sk42 is not None else 'N/A'
    y_str = f"{int(y_sk42)}" if y_sk42 is not None else 'N/A'
    coord_str = f"координаты: X={x_str} Y={y_str}"

    # Формируем описание района в зависимости от расстояния
    if distance <= 2:
        desc = found_city.description
        if desc:
            return f"район {found_city.name_ru} ({desc}, {coord_str})"
        return f"район {found_city.name_ru} ({coord_str})"
    else:
        desc = found_city.description
        if desc:
            return f"район {distance:.1f} км {direction} {found_city.name_ru} ({desc}, {coord_str})"
        return f"район {distance:.1f} км {direction} {found_city.name_ru} ({coord_str})"
