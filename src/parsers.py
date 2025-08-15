
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
from typing import Optional, Tuple, Dict, Any, Union

from models.points import PointRecord


class DateTimeExtractor:
    """Утилитарный класс для извлечения и нормализации даты/времени."""
    
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
            self._parse_openweathermap_format
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
        current = root.find(".//current")
        if current is None:
            return None
            
        city_elem = current.find("city")
        coord_elem = city_elem.find("coord") if city_elem is not None else None
        country_elem = current.find("country")
        lastupdate_elem = current.find("lastupdate")
        
        lat_val = coord_elem.attrib.get("lat") if coord_elem is not None else None
        lon_val = coord_elem.attrib.get("lon") if coord_elem is not None else None
        city_val = city_elem.attrib.get("name") if city_elem is not None else None
        country_val = country_elem.text if country_elem is not None else None
        
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
                 self._parse_openweathermap_format(data))
        
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

