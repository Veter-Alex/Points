"""
Модуль для работы с географическими данными.
Содержит функции определения стран по координатам и преобразования координат.
"""

import math
import os
from typing import Optional, Tuple

import geopandas as gpd
from shapely.geometry import Point

_WORLD_GDF: Optional[gpd.GeoDataFrame] = None  # Кэш для GeoDataFrame


def get_country_by_lat_lon(lat: float, lon: float) -> Tuple[str, str]:
    """
    Определяет страну по координатам широта/долгота.

    Args:
        lat (float): Широта
        lon (float): Долгота

    Returns:
        Tuple[str, str]: Кортеж (название_страны_на_английском, название_страны_на_русском)
    """
    global _WORLD_GDF
    if _WORLD_GDF is None:
        geojson_path = os.path.join(os.path.dirname(__file__), "countries.geojson")
        _WORLD_GDF = gpd.read_file(geojson_path)
    point = Point(lon, lat)
    matches = _WORLD_GDF[_WORLD_GDF["geometry"].contains(point)]
    country_eng = ""
    country_rus = ""
    if not matches.empty:
        country_eng = matches.iloc[0]["name"]
    else:
        buffer_point = point.buffer(0.02)
        buffer_matches = _WORLD_GDF[_WORLD_GDF["geometry"].intersects(buffer_point)]
        if not buffer_matches.empty:
            country_eng = buffer_matches.iloc[0]["name"]
    country_translate = {
        "Russia": "России",
        "Ukraine": "Украины",
        "Germany": "Германии",
        "France": "Франции",
        "China": "Китая",
        "Belarus": "Белоруссии",
        "Poland": "Польши",
        "Kazakhstan": "Казахстана",
        "United States of America": "США",
        "United States": "США",
        "USA": "США",
        "Turkey": "Турции",
        "Italy": "Италии",
        "Spain": "Испании",
        "United Kingdom": "Великобритании",
        "Czechia": "Чехии",
        "Czech Republic": "Чехии",
        "Estonia": "Эстонии",
        "Latvia": "Латвии",
        "Lithuania": "Литвы",
        "Finland": "Финляндии",
        "Georgia": "Грузии",
        "Armenia": "Армении",
        "Azerbaijan": "Азербайджана",
        "Moldova": "Молдовы",
        "Uzbekistan": "Узбекистана",
        "Kyrgyzstan": "Киргизии",
        "Tajikistan": "Таджикистана",
        "Turkmenistan": "Туркменистана",
        "Romania": "Румынии",
        "Bulgaria": "Болгарии",
        "Serbia": "Сербии",
        "Hungary": "Венгрии",
        "Slovakia": "Словакии",
        "Slovenia": "Словении",
        "Croatia": "Хорватии",
        "Montenegro": "Черногории",
        "Bosnia and Herzegovina": "Боснии и Герцеговины",
        "North Macedonia": "Северной Македонии",
        "Greece": "Греции",
        "Sweden": "Швеции",
        "Norway": "Норвегии",
        "Denmark": "Дании",
        "Iceland": "Исландии",
        "Malta": "Мальты",
        "Liechtenstein": "Лихтенштейна",
        "Monaco": "Монако",
        "San Marino": "Сан-Марино",
        "Vatican City": "Ватикана",
        "Switzerland": "Швейцарии",
        "Luxembourg": "Люксембурга",
        "Singapore": "Сингапура",
        "Japan": "Японии",
        "South Korea": "Южной Кореи",
        "North Korea": "Северной Кореи",
        "Thailand": "Таиланда",
        "Vietnam": "Вьетнама",
        "Malaysia": "Малайзии",
        "Indonesia": "Индонезии",
        "Philippines": "Филиппин",
        "India": "Индии",
        "Pakistan": "Пакистана",
        "Bangladesh": "Бангладеш",
        "Sri Lanka": "Шри-Ланки",
        "Australia": "Австралии",
        "New Zealand": "Новой Зеландии",
        "Canada": "Канады",
        "Mexico": "Мексики",
        "Brazil": "Бразилии",
        "Argentina": "Аргентины",
        "Chile": "Чили",
        "Peru": "Перу",
        "Colombia": "Колумбии",
        "Venezuela": "Венесуэлы",
        "Ecuador": "Эквадора",
        "Bolivia": "Боливии",
        "Paraguay": "Парагвая",
        "Uruguay": "Уругвая",
        "Egypt": "Египта",
        "South Africa": "Южной Африки",
        "Morocco": "Марокко",
        "Algeria": "Алжира",
        "Tunisia": "Туниса",
        "Libya": "Ливии",
        "Sudan": "Судана",
        "Ethiopia": "Эфиопии",
        "Kenya": "Кении",
        "Tanzania": "Танзании",
        "Nigeria": "Нигерии",
        "Ghana": "Ганы",
        "Iran": "Ирана",
        "Iraq": "Ирака",
        "Syria": "Сирии",
        "Lebanon": "Ливана",
        "Jordan": "Иордании",
        "Israel": "Израиля",
        "Saudi Arabia": "Саудовской Аравии",
        "UAE": "ОАЭ",
        "Qatar": "Катара",
        "Kuwait": "Кувейта",
        "Bahrain": "Бахрейна",
        "Oman": "Омана",
        "Yemen": "Йемена",
        "Afghanistan": "Афганистана",
        "Nepal": "Непала",
        "Bhutan": "Бутана",
        "Myanmar": "Мьянмы",
        "Cambodia": "Камбоджи",
        "Laos": "Лаоса",
    }
    country_rus = country_translate.get(country_eng, country_eng)
    return country_eng, country_rus


def get_sk42_coordinates(
    lat: float, lon: float, log_message=None
) -> Tuple[Optional[int], Optional[int]]:
    """
    Преобразует координаты WGS-84 в систему координат СК-42.

    Args:
        lat (float): Широта в WGS-84
        lon (float): Долгота в WGS-84
        log_message: Функция для логирования

    Returns:
        Tuple[Optional[int], Optional[int]]: Кортеж (x_sk42, y_sk42) или (None, None) при ошибке
    """
    from src.coordinate_transformer import CoordinateTransformer

    if lon < 18 or lon > 165:
        if log_message:
            log_message(
                f"Координаты вне зоны действия СК-42: {lat}, {lon}",
                color="yellow",
                logger_level="warning",
            )
        x_sk42, y_sk42 = None, None
    else:
        try:
            transformer = CoordinateTransformer(
                system="SK42_GAUSS_KRUGER", zone="AUTO", log_message=log_message
            )
            x_sk42, y_sk42 = transformer.transform(lat, lon, to_wgs=False)
            if x_sk42 is not None and (math.isinf(x_sk42) or math.isnan(x_sk42)):
                x_sk42 = None
            if y_sk42 is not None and (math.isinf(y_sk42) or math.isnan(y_sk42)):
                y_sk42 = None
        except Exception as e:
            if log_message:
                log_message(
                    f"Ошибка преобразования координат WGS84->СК-42: {e}",
                    color="red",
                    logger_level="error",
                )
            x_sk42, y_sk42 = None, None
    x_sk42 = int(x_sk42) if x_sk42 is not None else None
    y_sk42 = int(y_sk42) if y_sk42 is not None else None
    return x_sk42, y_sk42
