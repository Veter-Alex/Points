import os
import shutil
import urllib.request
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional

import geopandas as gpd
from shapely.geometry import Point

from models.city import CityData, CityRecord
from models.points import PointRecord, PointsData
from src.logger import logger

_WORLD_GDF = None  # Кэш для GeoDataFrame

def find_folders_missing_data_csv(rootFolder: str) -> List[str]:
    """
    Ищет во всех поддиректориях rootFolder папки, в которых есть хотя бы один xml или json файл,
    но нет файла data.csv. Папки с именем 'bad' игнорируются.
    Возвращает список абсолютных путей к таким папкам.
    """
    result = []
    for dirpath, dirnames, filenames in os.walk(rootFolder):
        # Пропустить саму папку bad (только если текущая папка называется bad)
        if os.path.basename(dirpath).lower() == "bad":
            continue
        has_xml_or_json = any(f.lower().endswith((".xml", ".json")) for f in filenames)
        has_data_csv = any(f.lower() == "data.csv" for f in filenames)
        if has_xml_or_json and not has_data_csv:
            result.append(dirpath)
    return result


def parse_xml(xml_path: str) -> Optional[PointRecord]:
    """
    Универсальный парсер xml-файла с точкой.
    Возвращает PointRecord (или None, если невалидно).
    """
    logger.info(f"Начинаем обработку XML файла: {xml_path}")
    try:
        with open(xml_path, encoding="utf-8") as f_xml:
            xml_text = f_xml.read()
        tree = ET.ElementTree(ET.fromstring(xml_text))
        root = tree.getroot()
        # --- Формат 1: <root><point>...
        point = root.find(".//point")
        if point is not None:
            lat = point.find("latitude")
            lat_val = lat.attrib.get("Value") if lat is not None else None
            lon = point.find("longitude")
            lon_val = lon.attrib.get("Value") if lon is not None else None
            dt = point.find("datetime")
            dt_val = dt.attrib.get("Value") if dt is not None else None
            city = point.find("City")
            if city is not None:
                city_val = city.attrib.get("Value")
            else:
                name = point.find("name")
                city_val = name.attrib.get("Value") if name is not None else None
            country = point.find("Country")
            country_val = country.attrib.get("Value") if country is not None else None
            # Разделить дату и время
            date_val, time_val = None, None
            if dt_val and " " in dt_val:
                date_val, time_val = dt_val.split(" ", 1)
            elif dt_val:
                date_val = dt_val
            # Проверка обязательных
            if not (lat_val and lon_val and date_val and time_val):
                raise ValueError("Нет обязательных данных (lat/lon/date/time)")
            return PointRecord(
                date=date_val,
                time=time_val,
                latitude=float(lat_val),
                longitude=float(lon_val),
                x_sk42=None,
                y_sk42=None,
                country=country_val,
                city=city_val,
                area_desc=None,
                region_desc=None,
                original_text=xml_text,
            )
        # --- Формат 2: <weather><loc ...><obs .../></loc></weather>
        if root.tag == "weather":
            loc = root.find(".//loc")
            if loc is None:
                raise ValueError("Нет тега <loc>")
            city_val = loc.attrib.get("name")
            country_val = loc.attrib.get("country")
            lat_val = loc.attrib.get("lat")
            lon_val = loc.attrib.get("lon")
            # Найти первую подходящую запись с датой и временем
            dt_val = None
            for tag in ["obs", "latest", "fcd", "fch"]:
                node = loc.find(tag)
                if node is not None and "dt" in node.attrib:
                    dt_val = node.attrib["dt"]
                    break
            if not dt_val:
                raise ValueError("Нет даты и времени (dt)")
            # Разделить дату и время
            date_val, time_val = None, None
            if "T" in dt_val:
                date_val, time_val = dt_val.split("T", 1)
                time_val = time_val.split("Z")[0]  # убрать Z, если есть
            elif " " in dt_val:
                date_val, time_val = dt_val.split(" ", 1)
            else:
                date_val = dt_val
            if not (lat_val and lon_val and date_val and time_val):
                raise ValueError("Нет обязательных данных (lat/lon/date/time)")
            return PointRecord(
                date=date_val,
                time=time_val,
                latitude=float(lat_val),
                longitude=float(lon_val),
                x_sk42=None,
                y_sk42=None,
                country=country_val,
                city=city_val,
                area_desc=None,
                region_desc=None,
                original_text=xml_text,
            )
        # --- Формат 3: <document><GetHHForecastResult ...>
        if root.tag == "document":
            hh = root.find(".//GetHHForecastResult")
            if hh is not None:
                city_val = hh.attrib.get("cityName")
                country_val = hh.attrib.get("country_name")
                lat_val = hh.attrib.get("lat")
                lon_val = hh.attrib.get("lng")
                # Найти первую дату/время: <forecastData><HHWeather><time>...</time>
                dt_val = None
                # 1. <forecastData><HHWeather><time>
                hhweather = hh.find("forecastData/HHWeather/time")
                if hhweather is not None and hhweather.text:
                    dt_val = hhweather.text.strip()
                # 2. <forecastData><HHForecasts><HHForecast><time>
                if not dt_val:
                    hhforecast = hh.find("forecastData/HHForecasts/HHForecast/time")
                    if hhforecast is not None and hhforecast.text:
                        dt_val = hhforecast.text.strip()
                # Разделить дату и время
                date_val, time_val = None, None
                if dt_val and " " in dt_val:
                    date_val, time_val = dt_val.split(" ", 1)
                elif dt_val:
                    date_val = dt_val
                if not (lat_val and lon_val and date_val and time_val):
                    raise ValueError("Нет обязательных данных (lat/lon/date/time)")
                return PointRecord(
                    date=date_val,
                    time=time_val,
                    latitude=float(lat_val),
                    longitude=float(lon_val),
                    x_sk42=None,
                    y_sk42=None,
                    country=country_val,
                    city=city_val,
                    area_desc=None,
                    region_desc=None,
                    original_text=xml_text,
                )
        # --- Неизвестный формат
        raise ValueError("Неизвестный формат XML")
    except Exception as e:
        # Переместить файл в bad
        bad_dir = os.path.join(os.path.dirname(xml_path), "bad")
        os.makedirs(bad_dir, exist_ok=True)
        shutil.move(xml_path, os.path.join(bad_dir, os.path.basename(xml_path)))
        return None
    finally:
        logger.info(f"Файл успешно обработан: {xml_path}")


def find_point_by_lat_lon(
    points_data: List[PointRecord], latitude: float, longitude: float, tol: float = 1e-6
):
    """
    Найти точку в points_data по координатам (с учетом допуска tol).
    Возвращает PointRecord или None.
    """
    for point in points_data:
        # point.latitude, point.longitude должны быть float
        if (
            abs(point.latitude - latitude) <= tol
            and abs(point.longitude - longitude) <= tol
        ):
            return point
    return None

from typing import Tuple

def get_country_by_lat_lon(lat: float, lon: float) -> Tuple[str, str]:
    """
    Определить страну по координатам (lat, lon) с помощью границ стран (GeoJSON).
    При первом вызове скачивает и кэширует countries.geojson.
    Возвращает название страны или пустую строку.
    """
    global _WORLD_GDF
    if _WORLD_GDF is None:
        geojson_path = os.path.join(
            os.path.dirname(__file__), "countries.geojson"
        )
        _WORLD_GDF = gpd.read_file(geojson_path)

    point = Point(lon, lat)
    matches = _WORLD_GDF[_WORLD_GDF["geometry"].contains(point)]
    country_eng = ""
    country_rus = ""
    if not matches.empty:
        # Попробовать разные возможные поля для имени страны
        possible_fields = ["ADMIN", "name", "NAME", "COUNTRY", "country", "Country"]
        for field in possible_fields:
            if field in matches.columns:
                val = matches.iloc[0][field]
                if isinstance(val, str):
                    country_eng = val
                    break
        if not country_eng:
            # Если ничего не найдено, вернуть строковое представление первой колонки
            country_eng = str(matches.iloc[0][matches.columns[0]])

    # Словарь переводов: Английское название -> Русское в предложном падеже
    country_translate = {
        "Russia": "России",
        "Ukraine": "Украины",
        "Germany": "Германии",
        "France": "Франции",
        "China": "Китая",
        "Belarus": "Белоруссии",
        "Poland": "Польши",
        "Kazakhstan": "Казахстана",
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
        # ... можно добавить другие страны по необходимости ...
    }
    country_rus = country_translate.get(country_eng, country_eng)
    return country_eng, country_rus


def get_sk42_coordinates(lat: float, lon: float):
    """Преобразование координат WGS84 -> СК-42 с автоопределением зоны."""
    import math

    # Проверяем, что координаты в допустимом диапазоне для СК-42
    if lon < 21 or lon > 60:
        logger.warning(f"Координаты вне зоны действия СК-42: {lat}, {lon}")
        x_sk42, y_sk42 = None, None
    else:
        try:
            # Преобразование координат WGS84 -> СК-42
            from src.coordinate_transformer import CoordinateTransformer
            transformer = CoordinateTransformer(system="SK42_GAUSS_KRUGER", zone="AUTO")
            x_sk42, y_sk42 = transformer.transform(lat, lon, to_wgs=False)
            # Проверка на бесконечность и NaN
            if x_sk42 is not None and (math.isinf(x_sk42) or math.isnan(x_sk42)):
                x_sk42 = None
            if y_sk42 is not None and (math.isinf(y_sk42) or math.isnan(y_sk42)):
                y_sk42 = None
        except Exception as e:
            logger.error(f"Ошибка преобразования координат WGS84->СК-42: {e}")
            x_sk42, y_sk42 = None, None
        x_sk42 = int(x_sk42) if x_sk42 is not None else None
        y_sk42 = int(y_sk42) if y_sk42 is not None else None
    # Возвращаем преобразованные координаты
    return x_sk42, y_sk42

def find_city_by_name(records, city_name):
    """
    Найти город в records по имени.
    Возвращает CityRecord или None.
    """
    for record in records:
        if (
            record.name_ru.lower() == city_name.lower()
            or record.name_original.lower() == city_name.lower()
        ):
            return record
    return None

def get_area_desc(found_city: CityRecord, result_parse_xml: PointRecord, x_sk42: int, y_sk42: int) -> str:
    """
    !TODO СДЕЛАТЬ
    Сформироваьть описание района (area_desc) для точки из city_data:
    район 6 км северо-западнее н.п.Суджа (87 км юго-зап. г.Курск, координаты: X=5681162 Y=6655966);
    Использует данные из found_city и result_parse_xml для создания описания.
    """
    return ""

def new_point_from_city_data(found_city: CityRecord, result_parse_xml: PointRecord) -> PointRecord:
    """
    Создать новый PointRecord из результата парсинга XML.
    Использует данные из result_parse_xml и city_data для создания нового объекта.
    """
    country_eng, country_rus = get_country_by_lat_lon(
        result_parse_xml.latitude, result_parse_xml.longitude
    )

    x_sk42, y_sk42 = get_sk42_coordinates(
        result_parse_xml.latitude, result_parse_xml.longitude
    )

    return PointRecord(
        date=result_parse_xml.date,
        time=result_parse_xml.time,
        latitude=result_parse_xml.latitude,
        longitude=result_parse_xml.longitude,
        x_sk42=x_sk42,
        y_sk42=y_sk42,
        country=country_eng,
        city=result_parse_xml.city,
        area_desc=get_area_desc(found_city, result_parse_xml, x_sk42, y_sk42),
        region_desc=f"на территории {country_rus}",
        original_text=result_parse_xml.original_text,
    )

def new_point_from_points_data(found_point: PointRecord, result_parse_xml: PointRecord) -> PointRecord:
    """
    Создать новый PointRecord из найденной точки и результата парсинга XML.
    Использует данные из found_point и result_parse_xml для создания нового объекта.
    """
    return PointRecord(
        date=result_parse_xml.date,
        time=result_parse_xml.time,
        latitude=found_point.latitude,
        longitude=found_point.longitude,
        x_sk42=found_point.x_sk42,
        y_sk42=found_point.y_sk42,
        country=found_point.country,
        city=found_point.city,
        area_desc=found_point.area_desc,
        region_desc=found_point.region_desc,
        original_text=result_parse_xml.original_text,
    )

def find_and_parse_files(
    input_folder: str, city_data: CityData, points_data: PointsData
) -> None:
    """
    Основная функция для поиска папок с отсутствующим data.csv и парсинга xml и json файлов.
    """
    # Список для городов, которые не удалось найти в city_data
    wrong_city_data = []

    # Запустить поиск папок с отсутствующим data.csv
    for folder in find_folders_missing_data_csv(input_folder):
        print(f"Папка без data.csv: {folder}")
        # Пройтись по всем файлам в папке
        for file in os.listdir(folder):
            # если файл XML
            if file.endswith(".xml"):
                # Парсинг XML файла
                result_parse_xml = parse_xml(os.path.join(folder, file))
                # если парсинг успешен
                if result_parse_xml is not None:
                    # ищем точку по координатам ранее отмеченных точках
                    found_point = find_point_by_lat_lon(
                        points_data.points,
                        result_parse_xml.latitude,
                        result_parse_xml.longitude,
                    )
                    # Если точка найдена
                    if found_point:
                        # Сформировать новую точку (PointRecord):
                        #  используем данные из result_parse_xml
                        #  (date/time и original_text),
                        #  остальные поля из найденной, ранее отмеченной точки
                        new_point = new_point_from_points_data(found_point, result_parse_xml)

                    else:
                        # ищем город (result_parse_xml.city) в city_data
                        found_city = find_city_by_name(
                            city_data.records, result_parse_xml.city
                        )
                        # Если город найден
                        if found_city:
                            # Сформировать новую точку (PointRecord):
                            #  используем данные из result_parse_xml
                            #  и данные из найденного города
                            #  (широта/долгота, название города и т.д.)
                            new_point = new_point_from_city_data(found_city, result_parse_xml)

                        else:
                            # Если не найдена запись широта/долгота в points_data,
                            # и не найден населенный пункт в city_data, то
                            # создать запись типа CityRecord и добавить в отдельный список
                            new_city = CityRecord(
                                name_original=result_parse_xml.city if result_parse_xml.city is not None else "",
                                name_ru="русское название_города ",
                                latitude=result_parse_xml.latitude,
                                longitude=result_parse_xml.longitude,
                                country=result_parse_xml.country,
                                description=None,  # Здесь можно добавить описание, если нужно
                                region=None,  # Здесь можно добавить регион, если нужно
                            )
                            wrong_city_data.append(new_city)


            # если файл JSON
            elif file.endswith(".json"):
                # parse_json_file(os.path.join(folder, file))
                pass

            points_data.add_point(new_point)
            logger.info(f"Добавлена точка: {new_point}")
        
        # После обработки всех файлов в папке
        # сохранить city_data и points_data в файлы
        points_data.save()

    # После обработки всех папок

    # Обработать список wrong_city_data (не найденные города)
    logger.info("Не найденные города:")
    for city in wrong_city_data:
        logger.info(f" - {city.name_original} ({city.latitude}, {city.longitude})")