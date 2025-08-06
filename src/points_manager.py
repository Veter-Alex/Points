
"""
Модуль для работы с точками.

Содержит функции для создания и поиска точек по различным критериям.
Все функции снабжены подробными комментариями и докстрингами согласно лучшим практикам.
"""

from typing import Any, Callable, List, Optional

from models.city import CityRecord
from models.points import PointRecord




def find_point_by_lat_lon(points: List[PointRecord], latitude: float, longitude: float, tol: float = 1e-6) -> Optional[PointRecord]:
    """
    Поиск точки по координатам с учетом допуска.

    Args:
        points (List[PointRecord]): Список точек для поиска.
        latitude (float): Широта искомой точки.
        longitude (float): Долгота искомой точки.
        tol (float): Допустимое отклонение для сравнения координат.

    Returns:
        Optional[PointRecord]: Найденная точка или None, если совпадений нет.
    """
    # Перебираем все точки и сравниваем координаты с учетом допуска
    for point in points:
        if abs(point.latitude - latitude) <= tol and abs(point.longitude - longitude) <= tol:
            return point
    return None




def new_point_from_city_data(
    found_city: CityRecord,
    result_parse_xml: PointRecord,
    get_country_by_lat_lon: Callable[[float, float], tuple],
    get_sk42_coordinates: Callable[[float, float, Any], tuple],
    log_message=None,
) -> PointRecord:
    """
    Создает объект PointRecord на основе найденного города и результата парсинга.

    Args:
        found_city (CityRecord): Найденный город.
        result_parse_xml (PointRecord): Результат парсинга файла.
        get_country_by_lat_lon (Callable): Функция для определения страны по координатам.
        get_sk42_coordinates (Callable): Функция для преобразования координат в систему СК-42.
        log_message: Функция для логирования (опционально).

    Returns:
        PointRecord: Новый объект точки с заполненными полями.
    """
    # Получаем страну по координатам
    country_eng, country_rus = get_country_by_lat_lon(result_parse_xml.latitude, result_parse_xml.longitude)
    # Получаем координаты в системе СК-42
    x_sk42, y_sk42 = get_sk42_coordinates(result_parse_xml.latitude, result_parse_xml.longitude, log_message)
    # Импортируем функцию для формирования описания района
    from src.city_manager import get_area_desc
    area_desc = get_area_desc(found_city, result_parse_xml, x_sk42, y_sk42)
    # Формируем объект PointRecord
    return PointRecord(
        date=result_parse_xml.date,
        time=result_parse_xml.time,
        latitude=result_parse_xml.latitude,
        longitude=result_parse_xml.longitude,
        x_sk42=x_sk42,
        y_sk42=y_sk42,
        country=country_eng,
        city=result_parse_xml.city,
        area_desc=area_desc,
        region_desc=getattr(found_city, "region", None),
        original_text=result_parse_xml.original_text,
        file_path=result_parse_xml.file_path,
    )




def point_without_city(
    result_parse_file: PointRecord,
    get_country_by_lat_lon: Callable[[float, float], tuple],
    get_sk42_coordinates: Callable[[float, float, Any], tuple],
    log_message=None,
) -> Optional[PointRecord]:
    """
    Создает объект PointRecord, если город не найден.

    Args:
        result_parse_file (PointRecord): Результат парсинга файла.
        get_country_by_lat_lon (Callable): Функция для определения страны по координатам.
        get_sk42_coordinates (Callable): Функция для преобразования координат в систему СК-42.
        log_message: Функция для логирования (опционально).

    Returns:
        Optional[PointRecord]: Новый объект точки или None, если не удалось создать.
    """
    # Получаем страну по координатам
    country_eng, country_rus = get_country_by_lat_lon(result_parse_file.latitude, result_parse_file.longitude)
    # Получаем координаты в системе СК-42
    x_sk42, y_sk42 = get_sk42_coordinates(result_parse_file.latitude, result_parse_file.longitude, log_message)
    # Формируем объект PointRecord без города
    return PointRecord(
        date=result_parse_file.date,
        time=result_parse_file.time,
        latitude=result_parse_file.latitude,
        longitude=result_parse_file.longitude,
        x_sk42=x_sk42,
        y_sk42=y_sk42,
        country=country_eng,
        city=None,
        area_desc=None,
        region_desc=f"на территории {country_rus}",
        original_text=result_parse_file.original_text,
        file_path=result_parse_file.file_path,
    )
