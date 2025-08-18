
"""
Модуль для парсинга XML и JSON файлов.

Содержит классы и функции для безопасного парсинга с обработкой ошибок и нормализацией данных.
Рефакторинг с использованием ООП принципов для улучшения поддерживаемости и расширяемости.
"""

import json
import os
import shutil
import xml.etree.ElementTree as ET
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union

from models.points import PointRecord


class DateTimeExtractor:
    """Утилитарный класс для извлечен        return latitude, longitude, city, country, date_val, time_val

    def _extract_additional_datetime(self, data: Dict, current_date: Optional[str],
                                   current_time: Optional[str]) -> Tuple[Optional[str], Optional[str]]: и нормализации даты/времени."""

    @staticmethod
    def extract_from_file_metadata(file_path: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Извлекает дату и время из метаданных файла.

        Args:
            file_path (str): Путь к файлу.

        Returns:
            Tuple[Optional[str], Optional[str]]: Дата и время или (None, None).
        """
        try:
            file_ctime = os.path.getctime(file_path)
            dt_obj = datetime.fromtimestamp(file_ctime)
            return dt_obj.strftime("%Y-%m-%d"), dt_obj.strftime("%H:%M:%S")
        except (OSError, ValueError):
            return None, None

    @staticmethod
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

    @staticmethod
    def extract_datetime_with_fallback(parsed_date: Optional[str], parsed_time: Optional[str],
                                     file_path: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Извлекает дату/время с fallback на метаданные файла.

        Args:
            parsed_date: Дата из содержимого файла.
            parsed_time: Время из содержимого файла.
            file_path: Путь к файлу для fallback.

        Returns:
            Tuple[Optional[str], Optional[str]]: Финальные дата и время.
        """
        date_val, time_val = parsed_date, parsed_time

        # Fallback на время создания файла если что-то отсутствует
        if not date_val or not time_val:
            file_date, file_time = DateTimeExtractor.extract_from_file_metadata(file_path)
            if not date_val:
                date_val = file_date
            if not time_val:
                time_val = file_time

        return date_val, time_val


class CoordinateExtractor:
    """Утилитарный класс для извлечения координат."""

    @staticmethod
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


class FileHandler:
    """Утилитарный класс для работы с файлами."""

    @staticmethod
    def move_to_bad_folder(file_path: str, log_message=None) -> None:
        """
        Перемещает файл в папку 'bad' при ошибке парсинга.

        Args:
            file_path (str): Путь к файлу.
            log_message (callable, optional): Функция для логирования.
        """
        bad_dir = os.path.join(os.path.dirname(file_path), "bad")
        os.makedirs(bad_dir, exist_ok=True)

        # Перемещаем основной файл
        shutil.move(file_path, os.path.join(bad_dir, os.path.basename(file_path)))

        # Перемещаем соответствующий .spr файл, если он существует
        spr_path = os.path.splitext(file_path)[0] + ".spr"
        if os.path.exists(spr_path):
            shutil.move(spr_path, os.path.join(bad_dir, os.path.basename(spr_path)))


class BaseParser(ABC):
    """Абстрактный базовый класс для всех парсеров."""

    def __init__(self, file_path: str, log_message=None):
        self.file_path = file_path
        self.log_message = log_message
        self.original_text = ""

    def log(self, message: str, color: Optional[str] = None, logger_level: str = "info") -> None:
        """Логирование с проверкой наличия функции."""
        if self.log_message:
            self.log_message(message, color=color, logger_level=logger_level)

    @abstractmethod
    def _extract_data(self) -> Dict[str, Any]:
        """Извлекает данные из файла. Должно быть переопределено в наследниках."""
        pass

    def _validate_required_data(self, latitude: Optional[float], longitude: Optional[float],
                              date_val: Optional[str], time_val: Optional[str]) -> None:
        """
        Валидация обязательных данных.

        Args:
            latitude: Широта.
            longitude: Долгота.
            date_val: Дата.
            time_val: Время.

        Raises:
            ValueError: Если отсутствуют обязательные данные.
        """
        if not (latitude is not None and longitude is not None and date_val and time_val):
            raise ValueError("Нет обязательных данных (lat/lon/date/time)")

    def _create_point_record(self, data: Dict[str, Any]) -> PointRecord:
        """
        Создает объект PointRecord из извлеченных данных.

        Args:
            data: Словарь с данными точки.

        Returns:
            PointRecord: Объект записи точки.
        """
        return PointRecord(
            date=data.get('date', ''),
            time=data.get('time', ''),
            latitude=data['latitude'],
            longitude=data['longitude'],
            x_sk42=None,
            y_sk42=None,
            country=data.get('country'),
            city=data.get('city'),
            area_desc=None,
            region_desc=None,
            original_text=self.original_text,
            file_path=self.file_path,
        )

    def parse(self) -> Optional[PointRecord]:
        """
        Основной метод парсинга с обработкой ошибок.

        Returns:
            Optional[PointRecord]: Объект точки или None при ошибке.
        """
        self.log(f"Начинаем обработку файла: {self.file_path}")

        try:
            # Извлекаем данные из файла
            data = self._extract_data()

            # Обрабатываем дату/время с fallback
            date_val, time_val = DateTimeExtractor.extract_datetime_with_fallback(
                data.get('date'), data.get('time'), self.file_path
            )

            # Нормализуем дату и время
            if date_val and time_val:
                date_val, time_val = DateTimeExtractor.normalize_datetime(date_val, time_val)

            # Валидируем обязательные данные
            self._validate_required_data(data['latitude'], data['longitude'], date_val, time_val)

            # Обновляем данные
            data['date'] = date_val
            data['time'] = time_val

            return self._create_point_record(data)

        except Exception as e:
            self.log(f"Ошибка парсинга: {e}", color="red", logger_level="error")
            FileHandler.move_to_bad_folder(self.file_path, self.log_message)
            return None
        finally:
            self.log(f"Файл обработан: {self.file_path}", color="blue")


class XMLParser(BaseParser):
    """Парсер XML файлов с поддержкой различных форматов."""

    def _extract_data(self) -> Dict[str, Any]:
        """Извлекает данные из XML файла."""
        with open(self.file_path, encoding="utf-8") as f_xml:
            self.original_text = f_xml.read()

        tree = ET.ElementTree(ET.fromstring(self.original_text))
        root = tree.getroot()

        # Пробуем различные форматы XML
        parsers = [
            self._parse_point_format,
            self._parse_devexpert_format,
            self._parse_openweathermap_format,
            self._parse_openweathermap_forecast_format,
            self._parse_settings_client_format,
            self._parse_document_items_format,
            self._parse_hhforecast_format
        ]

        for parser in parsers:
            try:
                data = parser(root)
                if data:
                    return data
            except Exception:
                continue

        raise ValueError("Неизвестный формат XML")

    def _parse_point_format(self, root) -> Optional[Dict[str, Any]]:
        """Парсинг стандартного формата <point>."""
        point = root.find(".//point")
        if point is None:
            return None

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

        # Обработка даты/времени
        date_val, time_val = None, None
        if dt_val and " " in dt_val:
            date_val, time_val = dt_val.split(" ", 1)
        elif dt_val:
            date_val = dt_val

        return {
            'latitude': CoordinateExtractor.safe_float(lat_val),
            'longitude': CoordinateExtractor.safe_float(lon_val),
            'date': date_val,
            'time': time_val,
            'city': city_val,
            'country': country_val
        }

    def _parse_devexpert_format(self, root) -> Optional[Dict[str, Any]]:
        """Парсинг формата DevExpert weather."""
        loc = root.find(".//loc")
        if loc is None:
            return None

        lat_val = loc.attrib.get("lat")
        lon_val = loc.attrib.get("lon")
        city_val = loc.attrib.get("name")
        country_val = loc.attrib.get("country")

        # Ищем <obs> или <latest> для даты/времени
        obs = loc.find("obs")
        latest = loc.find("latest")
        date_val, time_val = None, None

        if obs is not None and obs.attrib.get("dt"):
            date_val, time_val = self._parse_iso_datetime(obs.attrib["dt"])
        elif latest is not None and latest.attrib.get("dt"):
            date_val, time_val = self._parse_iso_datetime(latest.attrib["dt"])

        return {
            'latitude': CoordinateExtractor.safe_float(lat_val),
            'longitude': CoordinateExtractor.safe_float(lon_val),
            'date': date_val,
            'time': time_val,
            'city': city_val,
            'country': country_val
        }

    def _parse_openweathermap_format(self, root) -> Optional[Dict[str, Any]]:
        """Парсинг формата OpenWeatherMap <current>."""
        # Если корневой элемент сам является current
        current = root if root.tag == "current" else root.find(".//current")
        if current is None:
            return None

        city_elem = current.find("city")
        coord_elem = city_elem.find("coord") if city_elem is not None else None
        lastupdate_elem = current.find("lastupdate")

        lat_val = coord_elem.attrib.get("lat") if coord_elem is not None else None
        lon_val = coord_elem.attrib.get("lon") if coord_elem is not None else None
        city_val = city_elem.attrib.get("name") if city_elem is not None else None

        # Ищем country сначала в city, потом в current
        country_val = None
        if city_elem is not None:
            country_elem_in_city = city_elem.find("country")
            if country_elem_in_city is not None:
                country_val = country_elem_in_city.text

        # Если не найдено в city, ищем в current
        if country_val is None:
            country_elem = current.find("country")
            if country_elem is not None:
                country_val = country_elem.text

        date_val, time_val = None, None
        if lastupdate_elem is not None:
            lastupdate_val = lastupdate_elem.attrib.get("value")
            if lastupdate_val and "T" in lastupdate_val:
                date_val, time_val = lastupdate_val.split("T", 1)

        return {
            'latitude': CoordinateExtractor.safe_float(lat_val),
            'longitude': CoordinateExtractor.safe_float(lon_val),
            'date': date_val,
            'time': time_val,
            'city': city_val,
            'country': country_val
        }

    def _parse_openweathermap_forecast_format(self, root) -> Optional[Dict[str, Any]]:
        """Парсинг формата OpenWeatherMap forecast <weatherdata>."""
        # Проверяем, что это формат weatherdata с forecast
        if root.tag != "weatherdata" and not root.find(".//weatherdata"):
            return None

        # Если корневой элемент не weatherdata, найдем его
        weatherdata = root if root.tag == "weatherdata" else root.find(".//weatherdata")
        if weatherdata is None:
            return None

        # Получаем координаты из location element
        location_elem = weatherdata.find('.//location[@latitude]')
        if location_elem is None:
            return None

        lat_val = location_elem.get('latitude')
        lon_val = location_elem.get('longitude')

        # Получаем название города
        name_elem = weatherdata.find('.//location/name')
        city_val = name_elem.text.strip() if name_elem is not None and name_elem.text else None

        # Получаем страну
        country_elem = weatherdata.find('.//location/country')
        country_val = country_elem.text.strip() if country_elem is not None and country_elem.text else None

        # Получаем дату/время из атрибутов файла (метаданных) вместо XML содержимого
        date_val, time_val = DateTimeExtractor.extract_from_file_metadata(self.file_path)

        return {
            'latitude': CoordinateExtractor.safe_float(lat_val),
            'longitude': CoordinateExtractor.safe_float(lon_val),
            'date': date_val,
            'time': time_val,
            'city': city_val,
            'country': country_val
        }

    def _parse_settings_client_format(self, root) -> Optional[Dict[str, Any]]:
        """Парсинг формата <settings> с элементом <client>."""
        if root.tag != "settings":
            return None
            
        client = root.find(".//client")
        if client is None:
            return None

        lat_val = client.attrib.get("lat")
        lon_val = client.attrib.get("lon")
        country_val = client.attrib.get("country")
        
        # В этом формате нет информации о городе, дате и времени
        city_val = None
        date_val = None
        time_val = None

        return {
            'latitude': CoordinateExtractor.safe_float(lat_val),
            'longitude': CoordinateExtractor.safe_float(lon_val),
            'date': date_val,
            'time': time_val,
            'city': city_val,
            'country': country_val
        }

    def _parse_document_items_format(self, root) -> Optional[Dict[str, Any]]:
        """
        Парсинг формата <document> с элементами <item>.
        Поддерживает файлы с одной или несколькими точками.
        Возвращает первую найденную точку для совместимости с текущей архитектурой.
        """
        if root.tag != "document":
            return None
        
        # Находим все элементы item
        items = root.findall(".//item")
        if not items:
            return None
        
        # Берем первый элемент (можно потом расширить для обработки всех)
        first_item = items[0]
        
        # Извлекаем данные из атрибутов
        lat_val = first_item.attrib.get("lat")
        lon_val = first_item.attrib.get("lng")  # Обратите внимание: lng, а не lon
        city_val = first_item.attrib.get("n")   # n = название/имя места
        country_val = first_item.attrib.get("country_name")
        
        # Дата и время не указаны в этом формате
        date_val = None
        time_val = None
        
        # Логируем информацию о количестве точек, если их несколько
        if len(items) > 1 and hasattr(self, 'log_message') and self.log_message:
            self.log_message(
                f"Файл содержит {len(items)} точек. Обрабатывается только первая.",
                color="orange",
                logger_level="info"
            )

        return {
            'latitude': CoordinateExtractor.safe_float(lat_val),
            'longitude': CoordinateExtractor.safe_float(lon_val),
            'date': date_val,
            'time': time_val,
            'city': city_val,
            'country': country_val
        }

    def _parse_hhforecast_format(self, root) -> Optional[Dict[str, Any]]:
        """
        Парсинг формата <document> с элементом <GetHHForecastResult>.
        Извлекает данные о местоположении из прогноза погоды.
        """
        if root.tag != "document":
            return None
        
        # Ищем элемент GetHHForecastResult
        forecast_result = root.find(".//GetHHForecastResult")
        if forecast_result is None:
            return None
        
        # Извлекаем данные из атрибутов GetHHForecastResult
        lat_val = forecast_result.attrib.get("lat")
        lon_val = forecast_result.attrib.get("lng")
        city_val = forecast_result.attrib.get("cityName")
        country_val = forecast_result.attrib.get("country_name")
        
        # Получаем дату и время из метаданных файла, а не из XML
        date_val = None
        time_val = None

        return {
            'latitude': CoordinateExtractor.safe_float(lat_val),
            'longitude': CoordinateExtractor.safe_float(lon_val),
            'date': date_val,
            'time': time_val,
            'city': city_val,
            'country': country_val
        }

    def _parse_iso_datetime(self, dt_str: str) -> Tuple[Optional[str], Optional[str]]:
        """Парсинг ISO формата даты/времени."""
        if "T" in dt_str:
            date_val, time_val = dt_str.split("T", 1)
            # Нормализация времени
            if time_val and ":" in time_val:
                time_parts = time_val.split(":")
                if len(time_parts) >= 3:
                    time_val = f"{time_parts[0]}:{time_parts[1]}:{time_parts[2]}"
                elif len(time_parts) == 2:
                    time_val = f"{time_parts[0]}:{time_parts[1]}:00"
            return date_val, time_val
        else:
            return dt_str, None


class JSONParser(BaseParser):
    """Парсер JSON файлов с поддержкой различных форматов."""

    def _extract_data(self) -> Dict[str, Any]:
        """Извлекает данные из JSON файла."""
        with open(self.file_path, encoding="utf-8") as f:
            self.original_text = f.read()
            data = json.loads(self.original_text)

        # Инициализация переменных
        latitude = None
        longitude = None
        city = None
        country = None
        date_val = None
        time_val = None

        # Пробуем различные форматы JSON
        result = (self._parse_worldweatheronline_format(data) or
                 self._parse_ipapi_format(data) or
                 self._parse_geoip_format(data) or
                 self._parse_openweathermap_format(data) or
                 self._parse_cityinfo_format(data) or
                 self._parse_accuweather_format(data) or
                 self._parse_geoplugin_format(data))

        if result:
            latitude, longitude, city, country, date_val, time_val = result

        # Дополнительная обработка времени из различных полей
        if date_val is None or time_val is None:
            date_val, time_val = self._extract_additional_datetime(data, date_val, time_val)

        return {
            'latitude': latitude,
            'longitude': longitude,
            'date': date_val,
            'time': time_val,
            'city': city,
            'country': country
        }

    def _parse_worldweatheronline_format(self, data: Dict) -> Optional[Tuple]:
        """Парсинг формата WorldWeatherOnline."""
        if "data" not in data or not isinstance(data["data"], dict):
            return None

        try:
            wwo_data = data["data"]
            area = wwo_data["nearest_area"][0]
            tz = wwo_data["time_zone"][0]

            latitude = CoordinateExtractor.safe_float(area["latitude"])
            longitude = CoordinateExtractor.safe_float(area["longitude"])
            city = area["areaName"][0]["value"]
            country = area["country"][0]["value"]

            localtime = tz["localtime"]  # "2024-08-26 10:27"
            if " " in localtime:
                date_val, time_val = localtime.split(" ", 1)
            else:
                date_val, time_val = localtime, None

            return latitude, longitude, city, country, date_val, time_val
        except (KeyError, IndexError, TypeError):
            return None

    def _parse_ipapi_format(self, data: Dict) -> Optional[Tuple]:
        """Парсинг формата IP-API (lat, lon)."""
        if "lat" not in data or "lon" not in data:
            return None

        latitude = CoordinateExtractor.safe_float(str(data["lat"]))
        longitude = CoordinateExtractor.safe_float(str(data["lon"]))
        city = data.get("city")
        country = data.get("country")

        # OpenWeatherMap One Call API: дата/время в current["dt"]
        date_val, time_val = None, None
        if ("current" in data and isinstance(data["current"], dict) and "dt" in data["current"]):
            try:
                dt_obj = datetime.fromtimestamp(data["current"]["dt"])
                date_val = dt_obj.strftime("%Y-%m-%d")
                time_val = dt_obj.strftime("%H:%M:%S")
            except (ValueError, TypeError):
                pass

        return latitude, longitude, city, country, date_val, time_val

    def _parse_geoip_format(self, data: Dict) -> Optional[Tuple]:
        """Парсинг формата GeoIP (latitude, longitude)."""
        if "latitude" not in data or "longitude" not in data:
            return None

        latitude = CoordinateExtractor.safe_float(str(data["latitude"]))
        longitude = CoordinateExtractor.safe_float(str(data["longitude"]))
        city = data.get("city")
        country = data.get("countryName") or data.get("country")

        return latitude, longitude, city, country, None, None

    def _parse_openweathermap_format(self, data: Dict) -> Optional[Tuple]:
        """Парсинг формата OpenWeatherMap (coord.lat, coord.lon)."""
        if "coord" not in data or not isinstance(data["coord"], dict):
            return None

        coord = data["coord"]
        if "lat" not in coord or "lon" not in coord:
            return None

        latitude = CoordinateExtractor.safe_float(str(coord["lat"]))
        longitude = CoordinateExtractor.safe_float(str(coord["lon"]))
        city = data.get("name")

        # Для OpenWeatherMap, страна может быть в sys.country
        country = None
        if "sys" in data and isinstance(data["sys"], dict):
            country = data["sys"].get("country")

        return latitude, longitude, city, country, None, None

    def _parse_cityinfo_format(self, data: Dict) -> Optional[Tuple]:
        """Парсинг формата CityInfo (cityInfo.lat, cityInfo.lon)."""
        if "cityInfo" not in data or not isinstance(data["cityInfo"], dict):
            return None

        city_info = data["cityInfo"]
        if "lat" not in city_info or "lon" not in city_info:
            return None

        latitude = CoordinateExtractor.safe_float(str(city_info["lat"]))
        longitude = CoordinateExtractor.safe_float(str(city_info["lon"]))

        # Извлекаем город и страну
        city = None
        country = None

        if "cityName" in city_info and isinstance(city_info["cityName"], dict):
            # Попробуем разные языки для названия города
            for lang in ["ru", "en", "ua"]:
                if lang in city_info["cityName"]:
                    city = city_info["cityName"][lang]
                    break

        if "country" in city_info and isinstance(city_info["country"], dict):
            # Попробуем разные языки для названия страны
            for lang in ["ru", "en", "ua"]:
                if lang in city_info["country"]:
                    country = city_info["country"][lang]
                    break

        # Для формата cityInfo не извлекаем дату/время из JSON - используем атрибуты файла
        return latitude, longitude, city, country, None, None

    def _parse_accuweather_format(self, data: Dict) -> Optional[Tuple]:
        """Парсинг формата AccuWeather (GeoPosition.Latitude, GeoPosition.Longitude)."""
        if "GeoPosition" not in data or not isinstance(data["GeoPosition"], dict):
            return None

        geo_pos = data["GeoPosition"]
        if "Latitude" not in geo_pos or "Longitude" not in geo_pos:
            return None

        latitude = CoordinateExtractor.safe_float(str(geo_pos["Latitude"]))
        longitude = CoordinateExtractor.safe_float(str(geo_pos["Longitude"]))

        # Извлекаем название города
        city = None
        if "LocalizedName" in data:
            city = data["LocalizedName"]
        elif "EnglishName" in data:
            city = data["EnglishName"]

        # Извлекаем страну
        country = None
        if "Country" in data and isinstance(data["Country"], dict):
            if "LocalizedName" in data["Country"]:
                country = data["Country"]["LocalizedName"]
            elif "EnglishName" in data["Country"]:
                country = data["Country"]["EnglishName"]

        # Для формата AccuWeather не извлекаем дату/время из JSON - используем атрибуты файла
        return latitude, longitude, city, country, None, None

    def _parse_geoplugin_format(self, data: Dict) -> Optional[Tuple]:
        """Парсинг формата GeoPlugin (geoplugin_latitude, geoplugin_longitude)."""
        if "geoplugin_latitude" not in data or "geoplugin_longitude" not in data:
            return None

        latitude = CoordinateExtractor.safe_float(str(data["geoplugin_latitude"]))
        longitude = CoordinateExtractor.safe_float(str(data["geoplugin_longitude"]))

        if latitude is None or longitude is None:
            return None

        # Извлекаем город и страну
        city = data.get("geoplugin_city")
        country = data.get("geoplugin_countryName")

        # Для формата GeoPlugin не извлекаем дату/время из JSON - используем атрибуты файла
        return latitude, longitude, city, country, None, None

    def _extract_additional_datetime(self, data: Dict, current_date: Optional[str],
                                   current_time: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
        """Извлечение даты/времени из дополнительных полей."""
        date_val, time_val = current_date, current_time

        # Попытка извлечь из timestamp полей
        if date_val is None or time_val is None:
            if "dt" in data:
                try:
                    dt_obj = datetime.fromtimestamp(data["dt"])
                    date_val = dt_obj.strftime("%Y-%m-%d")
                    time_val = dt_obj.strftime("%H:%M:%S")
                except (ValueError, TypeError):
                    pass

        # Проверка других полей
        if not date_val or not time_val:
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

        return date_val, time_val


# Публичные функции для обратной совместимости
def parse_xml(xml_path: str, log_message=None) -> Optional[PointRecord]:
    """
    Универсальный парсер XML-файла с точкой.

    Args:
        xml_path (str): Путь к XML файлу.
        log_message (callable, optional): Функция для логирования.

    Returns:
        Optional[PointRecord]: Объект PointRecord или None, если данные невалидны.
    """
    parser = XMLParser(xml_path, log_message)
    return parser.parse()


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
    parser = JSONParser(json_path, log_message)
    return parser.parse()


# Обратная совместимость для утилитарных функций
def safe_float(val: Optional[str]) -> Optional[float]:
    """Обратная совместимость."""
    return CoordinateExtractor.safe_float(val)


def normalize_datetime(date_val: str, time_val: str) -> Tuple[str, str]:
    """Обратная совместимость."""
    return DateTimeExtractor.normalize_datetime(date_val, time_val)


def parse_xml_multiple_points(xml_path: str, log_message=None) -> List[PointRecord]:
    """
    Специальная функция для парсинга XML файлов с множественными точками.
    Поддерживает формат <document> с элементами <item>.
    
    Args:
        xml_path (str): Путь к XML файлу.
        log_message (callable, optional): Функция для логирования.
        
    Returns:
        List[PointRecord]: Список объектов PointRecord или пустой список.
    """
    try:
        with open(xml_path, encoding="utf-8") as f:
            content = f.read()
            
        tree = ET.ElementTree(ET.fromstring(content))
        root = tree.getroot()
        
        # Проверяем, что это формат document с items или HHForecast
        if root.tag != "document":
            # Если не document формат, возвращаем результат обычного парсера
            result = parse_xml(xml_path, log_message)
            return [result] if result else []
        
        # Проверяем наличие items (множественные точки)
        items = root.findall(".//item")
        if items:
            # Обрабатываем формат с items
            points = []
            for item in items:
                # Извлекаем данные из каждого item
                lat_val = item.attrib.get("lat")
                lon_val = item.attrib.get("lng")
                city_val = item.attrib.get("n")
                country_val = item.attrib.get("country_name")
                
                # Проверяем обязательные поля
                latitude = CoordinateExtractor.safe_float(lat_val)
                longitude = CoordinateExtractor.safe_float(lon_val)
                
                if latitude is None or longitude is None:
                    if log_message:
                        log_message(f"Пропущен item с невалидными координатами: lat={lat_val}, lng={lon_val}", 
                                  color="orange", logger_level="warning")
                    continue
                
                # Получаем дату и время из метаданных файла
                date_val, time_val = DateTimeExtractor.extract_from_file_metadata(xml_path)
                if date_val and time_val:
                    date_val, time_val = DateTimeExtractor.normalize_datetime(date_val, time_val)
                
                # Создаем PointRecord
                try:
                    point = PointRecord(
                        date=date_val or "",
                        time=time_val or "",
                        latitude=latitude,
                        longitude=longitude,
                        x_sk42=None,
                        y_sk42=None,
                        country=country_val or "",
                        city=city_val or "",
                        area_desc="",
                        region_desc="",
                        original_text=content,
                        file_path=xml_path,
                    )
                    points.append(point)
                    
                except Exception as e:
                    if log_message:
                        log_message(f"Ошибка создания точки: {e}", color="red", logger_level="error")
                    continue
            
            if log_message and points:
                log_message(f"Извлечено {len(points)} точек из {len(items)} элементов", 
                           color="blue", logger_level="info")
            
            return points
        
        # Если нет items, возвращаем результат обычного парсера (включая HHForecast)
        result = parse_xml(xml_path, log_message)
        return [result] if result else []
        
    except Exception as e:
        if log_message:
            log_message(f"Ошибка парсинга файла с множественными точками: {e}", 
                       color="red", logger_level="error")
        return []


def parse_json_multiple_points(json_path: str, log_message=None) -> List[PointRecord]:
    """
    Универсальный парсер JSON-файла с поддержкой множественных точек.
    
    Args:
        json_path (str): Путь к JSON файлу.
        log_message: Функция для логирования сообщений.
        
    Returns:
        List[PointRecord]: Список извлеченных точек.
    """
    try:
        # Для JSON чаще всего одна точка на файл, но поддерживаем множественные
        result = parse_json(json_path, log_message)
        return [result] if result else []
        
    except Exception as e:
        if log_message:
            log_message(f"Ошибка парсинга JSON файла с множественными точками: {e}", 
                       color="red", logger_level="error")
        return []

