
"""
Модуль для парсинга XML и JSON файлов.

Содержит функции для безопасного парсинга с обработкой ошибок и нормализацией данных.
Все функции снабжены подробными комментариями и докстрингами согласно лучшим практикам.
"""

import json
import os
import shutil
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Optional, Tuple

from models.points import PointRecord


def safe_float(val: Optional[str]) -> Optional[float]:
    """
    Безопасное преобразование строки в float.

    Args:
        val (Optional[str]): Строка для преобразования.

    Returns:
        Optional[float]: Число или None, если преобразование невозможно.
    """
    try:
        return float(val) if val is not None else None
    except (TypeError, ValueError):
        return None



def normalize_datetime(date_val: str, time_val: str) -> Tuple[str, str]:
    """
    Приводит дату и время к формату DD.MM.YYYY и HH:MM:SS.

    Args:
        date_val (str): Исходная строка даты.
        time_val (str): Исходная строка времени.

    Returns:
        Tuple[str, str]: Кортеж нормализованных (дата, время).
    """
    try:
        # Дата: YYYY-MM-DD -> DD.MM.YYYY, иначе как есть
        if "-" in date_val:
            parts = date_val.split("-")
            normalized_date = f"{parts[2]}.{parts[1]}.{parts[0]}" if len(parts) == 3 else date_val
        else:
            normalized_date = date_val
        # Время: HH:MM -> HH:MM:00, HH:MM:SS -> как есть
        if time_val and ":" in time_val:
            time_parts = time_val.split(":")
            normalized_time = f"{time_parts[0]}:{time_parts[1]}:00" if len(time_parts) == 2 else time_val
        else:
            normalized_time = time_val if time_val else "00:00:00"
        return normalized_date, normalized_time
    except Exception:
        return date_val, time_val


def parse_xml(xml_path: str, log_message=None) -> Optional[PointRecord]:
    """
    Универсальный парсер XML-файла с точкой.

    Args:
        xml_path (str): Путь к XML файлу.
        log_message (callable, optional): Функция для логирования.

    Returns:
        Optional[PointRecord]: Объект PointRecord или None, если данные невалидны.
    """
    if log_message:
        log_message(f"Начинаем обработку XML файла: {xml_path}")
    try:
        with open(xml_path, encoding="utf-8") as f_xml:
            xml_text = f_xml.read()
        tree = ET.ElementTree(ET.fromstring(xml_text))
        root = tree.getroot()
        point = root.find(".//point")
        if point is not None:
            # ...старая логика...
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
            date_val, time_val = None, None
            if dt_val and " " in dt_val:
                date_val, time_val = dt_val.split(" ", 1)
            elif dt_val:
                date_val = dt_val

            # Если дата/время не найдены в файле, используем время создания файла
            if not date_val or not time_val:
                try:
                    file_ctime = os.path.getctime(xml_path)
                    dt_obj = datetime.fromtimestamp(file_ctime)
                    if not date_val:
                        date_val = dt_obj.strftime("%Y-%m-%d")
                    if not time_val:
                        time_val = dt_obj.strftime("%H:%M:%S")
                except (OSError, ValueError):
                    # Если не удалось получить время файла, оставляем пустые значения
                    pass

            # Нормализуем дату и время к единому формату
            if date_val and time_val:
                date_val, time_val = normalize_datetime(date_val, time_val)

            latitude = safe_float(lat_val)
            longitude = safe_float(lon_val)
            if not (
                latitude is not None and longitude is not None and date_val and time_val
            ):
                raise ValueError("Нет обязательных данных (lat/lon/date/time)")
            return PointRecord(
                date=date_val if date_val is not None else "",
                time=time_val if time_val is not None else "",
                latitude=latitude,
                longitude=longitude,
                x_sk42=None,
                y_sk42=None,
                country=country_val,
                city=city_val,
                area_desc=None,
                region_desc=None,
                original_text=xml_text,
                file_path=xml_path,
            )
        # --- DevExpert weather format ---
        loc = root.find(".//loc")
        if loc is not None:
            lat_val = loc.attrib.get("lat")
            lon_val = loc.attrib.get("lon")
            city_val = loc.attrib.get("name")
            country_val = loc.attrib.get("country")
            # Ищем <obs> или <latest> для даты/времени
            obs = loc.find("obs")
            latest = loc.find("latest")
            dt_val = None
            time_val = None
            if obs is not None and obs.attrib.get("dt"):
                # dt формат: 2025-06-27T06:00:00
                dt_str = obs.attrib["dt"]
                if "T" in dt_str:
                    date_val, time_val = dt_str.split("T", 1)
                    time_val = (
                        time_val.split(":")[0]
                        + ":"
                        + time_val.split(":")[1]
                        + ":"
                        + time_val.split(":")[2]
                        if ":" in time_val
                        else time_val
                    )
                else:
                    date_val = dt_str
            elif latest is not None and latest.attrib.get("dt"):
                dt_str = latest.attrib["dt"]
                if "T" in dt_str:
                    date_val, time_val = dt_str.split("T", 1)
                    # Если время без секунд, добавим :00
                    if time_val.count(":") == 1:
                        time_val += ":00"
                else:
                    date_val = dt_str
            else:
                date_val = None
                time_val = None

            # Если дата/время не найдены в файле, используем время создания файла
            if not date_val or not time_val:
                try:
                    file_ctime = os.path.getctime(xml_path)
                    dt_obj = datetime.fromtimestamp(file_ctime)
                    if not date_val:
                        date_val = dt_obj.strftime("%Y-%m-%d")
                    if not time_val:
                        time_val = dt_obj.strftime("%H:%M:%S")
                except (OSError, ValueError):
                    # Если не удалось получить время файла, оставляем пустые значения
                    pass

            # Нормализуем дату и время к единому формату
            if date_val and time_val:
                date_val, time_val = normalize_datetime(date_val, time_val)

            latitude = safe_float(lat_val)
            longitude = safe_float(lon_val)
            if not (
                latitude is not None and longitude is not None and date_val and time_val
            ):
                raise ValueError("Нет обязательных данных (lat/lon/date/time)")
            return PointRecord(
                date=date_val if date_val is not None else "",
                time=time_val if time_val is not None else "",
                latitude=latitude,
                longitude=longitude,
                x_sk42=None,
                y_sk42=None,
                country=country_val,
                city=city_val,
                area_desc=None,
                region_desc=None,
                original_text=xml_text,
                file_path=xml_path,
            )
        # --- OpenWeatherMap <current> format ---
        current = root.find(".//current")
        if current is not None:
            city_elem = current.find("city")
            coord_elem = city_elem.find("coord") if city_elem is not None else None
            country_elem = current.find("country")
            lastupdate_elem = current.find("lastupdate")
            lat_val = coord_elem.attrib.get("lat") if coord_elem is not None else None
            lon_val = coord_elem.attrib.get("lon") if coord_elem is not None else None
            city_val = city_elem.attrib.get("name") if city_elem is not None else None
            country_val = country_elem.text if country_elem is not None else None
            lastupdate_val = (
                lastupdate_elem.attrib.get("value")
                if lastupdate_elem is not None
                else None
            )
            date_val, time_val = None, None
            if lastupdate_val and "T" in lastupdate_val:
                date_val, time_val = lastupdate_val.split("T", 1)

            # Если дата/время не найдены в файле, используем время создания файла
            if not date_val or not time_val:
                try:
                    file_ctime = os.path.getctime(xml_path)
                    dt_obj = datetime.fromtimestamp(file_ctime)
                    if not date_val:
                        date_val = dt_obj.strftime("%Y-%m-%d")
                    if not time_val:
                        time_val = dt_obj.strftime("%H:%M:%S")
                except (OSError, ValueError):
                    # Если не удалось получить время файла, оставляем пустые значения
                    pass

            # Нормализуем дату и время к единому формату
            if date_val and time_val:
                date_val, time_val = normalize_datetime(date_val, time_val)

            latitude = safe_float(lat_val)
            longitude = safe_float(lon_val)
            if not (
                latitude is not None and longitude is not None and date_val and time_val
            ):
                raise ValueError("Нет обязательных данных (lat/lon/date/time)")
            return PointRecord(
                date=date_val if date_val is not None else "",
                time=time_val if time_val is not None else "",
                latitude=latitude,
                longitude=longitude,
                x_sk42=None,
                y_sk42=None,
                country=country_val,
                city=city_val,
                area_desc=None,
                region_desc=None,
                original_text=xml_text,
                file_path=xml_path,
            )
        raise ValueError("Неизвестный формат XML")
    except Exception as e:
        if log_message:
            log_message(f"Ошибка парсинга XML: {e}", color="red", logger_level="error")
        bad_dir = os.path.join(os.path.dirname(xml_path), "bad")
        os.makedirs(bad_dir, exist_ok=True)
        shutil.move(xml_path, os.path.join(bad_dir, os.path.basename(xml_path)))
        spr_path = os.path.splitext(xml_path)[0] + ".spr"
        if os.path.exists(spr_path):
            shutil.move(spr_path, os.path.join(bad_dir, os.path.basename(spr_path)))
        return None
    finally:
        if log_message:
            log_message(f"Файл успешно обработан: {xml_path}", color="blue")


def parse_json(json_path: str, log_message=None) -> Optional[PointRecord]:
    """
    Универсальный парсер JSON-файла с точкой.
    Поддерживает различные форматы JSON от разных сервисов геолокации.

    Args:
        json_path (str): Путь к JSON файлу.
        log_message (callable, optional): Функция для логирования.

    Returns:
        Optional[PointRecord]: Объект PointRecord или None, если данные невалидны.
    """
    if log_message:
        log_message(f"Начинаем обработку JSON файла: {json_path}")
    try:
        with open(json_path, encoding="utf-8") as f:
            json_text = f.read()
            data = json.loads(json_text)

        # Извлечение координат и даты/времени
        latitude = None
        longitude = None
        city = None
        country = None
        date_val = None
        time_val = None

        # WorldWeatherOnline format
        if "data" in data and isinstance(data["data"], dict):
            wwo_data = data["data"]
            try:
                area = wwo_data["nearest_area"][0]
                tz = wwo_data["time_zone"][0]
                latitude = safe_float(area["latitude"])
                longitude = safe_float(area["longitude"])
                city = area["areaName"][0]["value"]
                country = area["country"][0]["value"]
                localtime = tz["localtime"]  # "2024-08-26 10:27"
                if " " in localtime:
                    date_val, time_val = localtime.split(" ", 1)
                else:
                    date_val = localtime

                # Нормализуем дату и время к единому формату
                if date_val and time_val:
                    date_val, time_val = normalize_datetime(date_val, time_val)

                # Если всё найдено, возвращаем PointRecord
                if latitude is not None and longitude is not None and date_val and time_val:
                    return PointRecord(
                        date=date_val,
                        time=time_val,
                        latitude=latitude,
                        longitude=longitude,
                        x_sk42=None,
                        y_sk42=None,
                        country=country,
                        city=city,
                        area_desc=None,
                        region_desc=None,
                        original_text=json_text,
                        file_path=json_path,
                    )
            except Exception as e:
                if log_message:
                    log_message(f"Ошибка парсинга WorldWeatherOnline: {e}", color="red", logger_level="error")
                # ...existing code...

        # Формат 1: IP-API (lat, lon)
        if "lat" in data and "lon" in data:
            latitude = safe_float(str(data["lat"]))
            longitude = safe_float(str(data["lon"]))
            city = data.get("city")
            country = data.get("country")
            # OpenWeatherMap One Call API: дата/время в current["dt"]
            if (
                "current" in data
                and isinstance(data["current"], dict)
                and "dt" in data["current"]
            ):
                if date_val is None and time_val is None:
                    try:
                        dt_obj = datetime.fromtimestamp(data["current"]["dt"])
                        date_val = dt_obj.strftime("%Y-%m-%d")
                        time_val = dt_obj.strftime("%H:%M:%S")
                    except (ValueError, TypeError):
                        pass
            # Не определяем timezone как город, если city не найден

        # Формат 2: GeoIP (latitude, longitude)
        elif "latitude" in data and "longitude" in data:
            latitude = safe_float(str(data["latitude"]))
            longitude = safe_float(str(data["longitude"]))
            city = data.get("city")
            country = data.get("countryName") or data.get("country")

        # Формат 3: OpenWeatherMap (coord.lat, coord.lon)
        elif "coord" in data and isinstance(data["coord"], dict):
            coord = data["coord"]
            if "lat" in coord and "lon" in coord:
                latitude = safe_float(str(coord["lat"]))
                longitude = safe_float(str(coord["lon"]))
                city = data.get("name")
                # Для OpenWeatherMap, страна может быть в sys.country
                if "sys" in data and isinstance(data["sys"], dict):
                    country = data["sys"].get("country")

        # Извлекаем дату и время из JSON (если ещё не заполнены)
        if date_val is None or time_val is None:
            if "dt" in data:
                # OpenWeatherMap timestamp
                try:
                    dt_obj = datetime.fromtimestamp(data["dt"])
                    date_val = dt_obj.strftime("%Y-%m-%d")
                    time_val = dt_obj.strftime("%H:%M:%S")
                except (ValueError, TypeError):
                    pass

        # Проверяем наличие других полей с датой и временем
        if not date_val or not time_val:
            # Проверяем другие возможные поля с датой/временем
            if "datetime" in data:
                datetime_str = str(data["datetime"])
                if " " in datetime_str:
                    date_val, time_val = datetime_str.split(" ", 1)
                else:
                    date_val = datetime_str
            elif "timestamp" in data:
                try:
                    dt_obj = datetime.fromtimestamp(data["timestamp"])
                    date_val = dt_obj.strftime("%Y-%m-%d")
                    time_val = dt_obj.strftime("%H:%M:%S")
                except (ValueError, TypeError):
                    pass

        # Если дата/время все еще не найдены, используем время создания файла
        if not date_val or not time_val:
            try:
                file_ctime = os.path.getctime(json_path)
                dt_obj = datetime.fromtimestamp(file_ctime)
                if not date_val:
                    date_val = dt_obj.strftime("%Y-%m-%d")
                if not time_val:
                    time_val = dt_obj.strftime("%H:%M:%S")
            except (OSError, ValueError):
                # Если не удалось получить время файла, оставляем пустые значения
                pass

        # Проверяем обязательные данные (координаты, дата, время)
        if not (
            latitude is not None and longitude is not None and date_val and time_val
        ):
            raise ValueError("Нет обязательных данных (lat/lon/date/time)")

        # Нормализуем дату и время к единому формату
        if date_val and time_val:
            date_val, time_val = normalize_datetime(date_val, time_val)

        return PointRecord(
            date=date_val if date_val is not None else "",
            time=time_val if time_val is not None else "",
            latitude=latitude,
            longitude=longitude,
            x_sk42=None,
            y_sk42=None,
            country=country,
            city=city,
            area_desc=None,
            region_desc=None,
            original_text=json_text,
            file_path=json_path,
        )

    except json.JSONDecodeError as e:
        if log_message:
            log_message(
                f"Ошибка парсинга JSON (невалидный JSON): {e}",
                color="red",
                logger_level="error",
            )
        bad_dir = os.path.join(os.path.dirname(json_path), "bad")
        os.makedirs(bad_dir, exist_ok=True)
        shutil.move(json_path, os.path.join(bad_dir, os.path.basename(json_path)))
        # Перемещаем соответствующий .spr файл, если он существует
        spr_path = os.path.splitext(json_path)[0] + ".spr"
        if os.path.exists(spr_path):
            shutil.move(spr_path, os.path.join(bad_dir, os.path.basename(spr_path)))
        return None
    except Exception as e:
        if log_message:
            log_message(f"Ошибка парсинга JSON: {e}", color="red", logger_level="error")
        bad_dir = os.path.join(os.path.dirname(json_path), "bad")
        os.makedirs(bad_dir, exist_ok=True)
        shutil.move(json_path, os.path.join(bad_dir, os.path.basename(json_path)))
        # Перемещаем соответствующий .spr файл, если он существует
        spr_path = os.path.splitext(json_path)[0] + ".spr"
        if os.path.exists(spr_path):
            shutil.move(spr_path, os.path.join(bad_dir, os.path.basename(spr_path)))
        return None
    finally:
        if log_message:
            log_message(f"Файл успешно обработан: {json_path}", color="blue")
