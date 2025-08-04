"""
Модуль для работы с точками.
Содержит функции создания и поиска точек по различным критериям.
"""

from typing import Callable, List, Optional

from models.city import CityRecord
from models.points import PointRecord


def find_point_by_lat_lon(
    points_data: List[PointRecord], latitude: float, longitude: float, tol: float = 1e-6
) -> Optional[PointRecord]:
    """
    Найти точку в списке points_data по координатам с учетом допуска tol.

    Args:
        points_data (List[PointRecord]): Список точек для поиска
        latitude (float): Широта для поиска
        longitude (float): Долгота для поиска
        tol (float): Допуск для сравнения координат

    Returns:
        Optional[PointRecord]: Найденная точка или None
    """
    for point in points_data:
        if (
            abs(point.latitude - latitude) <= tol
            and abs(point.longitude - longitude) <= tol
        ):
            return point
    return None


def new_point_from_city_data(
    found_city: CityRecord,
    result_parse_xml: PointRecord,
    get_country_by_lat_lon: Callable[[float, float], tuple],
    get_sk42_coordinates: Callable[[float, float], tuple],
) -> PointRecord:
    """
    Создать новый PointRecord на основе найденного города и результата парсинга XML.

    Args:
        found_city (object): Найденный город
        result_parse_xml (PointRecord): Результат парсинга XML
        get_country_by_lat_lon (Callable): Функция определения страны по координатам
        get_sk42_coordinates (Callable): Функция преобразования в СК-42

    Returns:
        PointRecord: Новый объект точки
    """
    country_eng, country_rus = get_country_by_lat_lon(
        result_parse_xml.latitude, result_parse_xml.longitude
    )
    x_sk42, y_sk42 = get_sk42_coordinates(
        result_parse_xml.latitude, result_parse_xml.longitude
    )
    from src.city_manager import get_area_desc

    area_desc = get_area_desc(found_city, result_parse_xml, x_sk42, y_sk42)
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
    get_sk42_coordinates: Callable[[float, float], tuple],
) -> Optional[PointRecord]:
    """
    Создать новый PointRecord, если город не найден из имеющихся данных.

    Args:
        result_parse_xml (PointRecord): Результат парсинга XML
        get_country_by_lat_lon (Callable): Функция определения страны по координатам
        get_sk42_coordinates (Callable): Функция преобразования в СК-42

    Returns:
        Optional[PointRecord]: Новый объект точки или None

    Note:
        Сейчас возвращает None. Можно реализовать создание точки, если потребуется.
    """
    country_eng, country_rus = get_country_by_lat_lon(
        result_parse_file.latitude, result_parse_file.longitude
    )
    x_sk42, y_sk42 = get_sk42_coordinates(
        result_parse_file.latitude, result_parse_file.longitude
    )
    return PointRecord(
        date=result_parse_file.date,
        time=result_parse_file.time,
        latitude=result_parse_file.latitude,
        longitude=result_parse_file.longitude,
        x_sk42=x_sk42,
        y_sk42=y_sk42,
        country=country_eng,
        city=None,  # Город не указан
        area_desc=None,  # Описание района не указано
        region_desc=f"на территории {country_rus}",
        original_text=result_parse_file.original_text,
        file_path=result_parse_file.file_path,
    )
