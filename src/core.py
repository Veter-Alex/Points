

"""
Основной модуль обработки файлов с точками.

Содержит объектно-ориентированную архитектуру для парсинга XML/JSON файлов,
создания отчетов и сохранения данных. Использует принципы SOLID для лучшей
организации кода и тестируемости.
"""

import csv
import os
from abc import ABC, abstractmethod
from typing import Callable, List, Optional, Tuple, Union

from models.city import CityData, CityRecord
from models.points import PointRecord, PointsData
from models.settings import Settings
from src.city_manager import find_city_by_name, get_area_desc
from src.excel_manager import save_points_to_excel, save_points_without_city_to_csv
from src.file_manager import find_folders_missing_data_csv
from src.geo_manager import get_country_by_lat_lon, get_sk42_coordinates
from src.kml_manager import create_kml_file
from src.parsers import parse_json, parse_xml, parse_xml_multiple_points
from src.points_manager import (
    find_point_by_lat_lon,
    new_point_from_city_data,
    point_without_city,
)
from src.word_report_manager import create_word_report


class LoggingMixin:
    """Миксин для логирования с поддержкой цветов и уровней."""

    def __init__(self, log_message: Optional[Callable] = None):
        self.log_message = log_message

    def log(self, msg: str, color: Optional[str] = None, logger_level: Optional[str] = None) -> None:
        """Логирование сообщения с опциональными параметрами."""
        if self.log_message:
            self.log_message(msg, color=color, logger_level=logger_level)


class CoordinateHelper:
    """Помощник для работы с координатами."""

    def __init__(self, log_message: Optional[Callable] = None):
        self.log_message = log_message

    def get_sk42_with_logging(self, lat: float, lon: float, log_message: Optional[Callable] = None) -> Tuple[float, float]:
        """Получение координат СК-42 с логированием."""
        # Используем переданную функцию логирования или собственную
        if log_message is not None:
            # Оборачиваем переданную функцию, чтобы обработать дополнительные аргументы
            def wrapped_log_message(msg, color=None, logger_level=None):
                try:
                    # Пытаемся вызвать с дополнительными аргументами
                    log_message(msg, color=color, logger_level=logger_level)
                except TypeError:
                    # Если функция не поддерживает дополнительные аргументы, вызываем только с сообщением
                    log_message(msg)
            log_func = wrapped_log_message
        else:
            # Ensure log_func is always a callable with the expected signature
            def default_log_message(msg, color=None, logger_level=None):
                pass
            log_func = self.log_message if self.log_message is not None else default_log_message
        sk42_lat, sk42_lon = get_sk42_coordinates(lat, lon, log_func)
        # Ensure the return values are floats, not None
        lat_result = float(sk42_lat) if sk42_lat is not None else 0.0
        lon_result = float(sk42_lon) if sk42_lon is not None else 0.0
        return lat_result, lon_result


class FolderProcessor(LoggingMixin):
    """Обработчик папок для поиска файлов."""

    def __init__(self, log_message: Optional[Callable] = None):
        super().__init__(log_message)

    def find_target_folders(self, input_folder: str) -> List[str]:
        """Поиск папок без data.xlsx файлов."""
        folders = find_folders_missing_data_csv(input_folder)
        self.log(f"Найдено {len(folders)} папок для обработки")
        return folders

    def get_parseable_files(self, folder: str) -> List[str]:
        """Получение списка файлов для парсинга из папки."""
        files = []
        for file in os.listdir(folder):
            if file.lower().endswith(('.xml', '.json')):
                files.append(os.path.join(folder, file))
        return files


class FileProcessor(LoggingMixin):
    """Обработчик отдельных файлов с поддержкой множественных точек."""

    def __init__(self, log_message: Optional[Callable] = None):
        super().__init__(log_message)

    def parse_file(self, file_path: str) -> List[PointRecord]:
        """
        Парсинг одного файла с возможностью извлечения множественных точек.
        
        Returns:
            List[PointRecord]: Список точек (может быть пустым или содержать одну/несколько точек).
        """
        file_name = os.path.basename(file_path)
        points = []

        if file_path.lower().endswith('.xml'):
            self.log(f"Парсинг XML: {file_name}")
            
            # Сначала пробуем извлечь множественные точки
            multiple_points = parse_xml_multiple_points(file_path, self.log_message)
            
            if len(multiple_points) > 1:
                self.log(f"Найдено {len(multiple_points)} точек в файле", color="green")
                points = multiple_points
            elif len(multiple_points) == 1:
                points = multiple_points
            else:
                # Если функция множественных точек не сработала, используем обычный парсер
                single_point = parse_xml(file_path, self.log_message)
                if single_point:
                    points = [single_point]
                    
        elif file_path.lower().endswith('.json'):
            self.log(f"Парсинг JSON: {file_name}")
            single_point = parse_json(file_path, self.log_message)
            if single_point:
                points = [single_point]

        return points


class PointProcessor(LoggingMixin):
    """Обработчик точек и городов."""

    def __init__(self, city_data: CityData, points_data: PointsData,
                 coordinate_helper: CoordinateHelper, log_message: Optional[Callable] = None):
        super().__init__(log_message)
        self.city_data = city_data
        self.points_data = points_data
        self.coordinate_helper = coordinate_helper

    def process_point_with_city(self, parsed_point: PointRecord) -> Tuple[Optional[PointRecord], Optional[str]]:
        """Обработка точки с указанным городом."""
        found_city = find_city_by_name(self.city_data.records, parsed_point.city)

        if found_city:
            new_point = new_point_from_city_data(
                found_city,
                parsed_point,
                get_country_by_lat_lon,
                self.coordinate_helper.get_sk42_with_logging,
                self.log_message,
            )
            return new_point, None
        else:
            self.log(
                f"Город не найден в city_data: {parsed_point.city}",
                color="red",
                logger_level="warning",
            )
            country_eng, country_rus = get_country_by_lat_lon(
                parsed_point.latitude, parsed_point.longitude
            )
            new_city = (
                f"{parsed_point.city}=н.п.НАЗВАНИЕ ГОРОДА_"
                f"широта центра города_долгота центра города_"
                f"{country_eng}_описание относитьно обласного центра_"
                f"на территории {country_rus}"
            )
            return None, new_city

    def process_point_without_city(self, parsed_point: PointRecord) -> Tuple[Optional[PointRecord], Optional[PointRecord]]:
        """Обработка точки без указанного города."""
        found_point = find_point_by_lat_lon(
            self.points_data.points,
            parsed_point.latitude,
            parsed_point.longitude,
            0.01,
        )

        if found_point:
            parsed_point.city = found_point.city
            found_city = find_city_by_name(self.city_data.records, parsed_point.city)
            if found_city:
                new_point = new_point_from_city_data(
                    found_city,
                    parsed_point,
                    get_country_by_lat_lon,
                    self.coordinate_helper.get_sk42_with_logging,
                    self.log_message,
                )
                return new_point, None

        point_to_edit = point_without_city(
            parsed_point,
            get_country_by_lat_lon,
            self.coordinate_helper.get_sk42_with_logging,
            self.log_message,
        )
        return None, point_to_edit

    def add_point_to_data(self, point: PointRecord) -> None:
        """Добавление точки в основную базу данных."""
        self.points_data.add_point(point)
        self.log(
            f"Добавлена точка: дата {point.date}, время {point.time}, "
            f"{point.area_desc} координаты: широта={point.latitude}, долгота={point.longitude}",
            color="blue",
        )


class ReportGenerator(LoggingMixin):
    """Генератор отчетов."""

    def __init__(self, log_message: Optional[Callable] = None):
        super().__init__(log_message)

    def create_excel_report(self, points: List[PointRecord], folder: str) -> None:
        """Создание Excel отчета."""
        if not points:
            return

        data_xlsx_path = os.path.join(folder, "data.xlsx")
        save_points_to_excel(points, data_xlsx_path, self.log_message)
        self.log(f"Точки сохранены в {data_xlsx_path}", color="blue")

    def create_kml_files(self, points: List[PointRecord], folder: str, suffix: str = "") -> None:
        """Создание KML файлов для точек."""
        for point in points:
            if point.file_path:
                base_name = os.path.splitext(os.path.basename(point.file_path))[0]
                kml_file_path = os.path.join(folder, f"{base_name}{suffix}.kml")
            else:
                time_str = point.time.replace(':', '') if point.time else "notime"
                kml_file_path = os.path.join(
                    folder,
                    f"point{suffix}_{point.latitude}_{point.longitude}_{time_str}.kml",
                )

            create_kml_file(point, kml_file_path, self.log_message)
            color = "orange" if suffix else "blue"
            message = f"Создан KML файл{' для точки без города' if suffix else ''}: {kml_file_path}"
            self.log(message, color=color)

    def create_word_report(self, points: List[PointRecord], wrong_cities: List[str], folder: str) -> None:
        """Создание Word отчета."""
        if not (points or wrong_cities):
            return

        report_path = os.path.join(folder, "report.docx")
        create_word_report(points, wrong_cities, report_path, self.log_message)
        self.log(f"Создан Word отчёт: {report_path}", color="blue")

    def create_csv_report(self, points: List[PointRecord], folder: str) -> None:
        """Создание CSV отчета для точек без города."""
        if not points:
            return

        points_to_edit_file = os.path.join(folder, "points_without_city.csv")
        self.log("Точки без города в текущей папке:", color="orange", logger_level="debug")

        for point in points:
            self.log(
                f" - дата: {point.date}, время: {point.time}, {point.area_desc}, "
                f"координаты: широта={point.latitude}, долгота={point.longitude}",
                color="orange",
                logger_level="debug",
            )

        save_points_without_city_to_csv(points, points_to_edit_file, self.log_message)


class CorePipeline(LoggingMixin):
    """Основной координатор процесса обработки."""

    def __init__(self, city_data: CityData, points_data: PointsData, settings: Settings,
                 log_message: Optional[Callable] = None, status_callback: Optional[Callable] = None):
        super().__init__(log_message)
        self.city_data = city_data
        self.points_data = points_data
        self.settings = settings
        self.status_callback = status_callback

        # Инициализация компонентов
        self.coordinate_helper = CoordinateHelper(log_message)
        self.folder_processor = FolderProcessor(log_message)
        self.file_processor = FileProcessor(log_message)
        self.point_processor = PointProcessor(city_data, points_data, self.coordinate_helper, log_message)
        self.report_generator = ReportGenerator(log_message)

    def process_folder(self, folder: str) -> None:
        """Обработка одной папки."""
        self.log(f"Папка без data.xlsx: {folder}")

        points_folder: List[PointRecord] = []
        wrong_city_data_folder: List[str] = []
        points_to_edit_folder: List[PointRecord] = []

        # Получаем файлы для парсинга
        files = self.folder_processor.get_parseable_files(folder)

        # Обрабатываем каждый файл
        for file_path in files:
            parsed_points = self.file_processor.parse_file(file_path)

            if not parsed_points:  # Если список пуст
                continue

            # Обрабатываем каждую точку из файла
            for parsed_point in parsed_points:
                new_point: Optional[PointRecord] = None

                if parsed_point.city is not None:
                    # Обработка точки с городом
                    new_point, wrong_city = self.point_processor.process_point_with_city(parsed_point)
                    if wrong_city:
                        wrong_city_data_folder.append(wrong_city)
                else:
                    # Обработка точки без города
                    new_point, point_to_edit = self.point_processor.process_point_without_city(parsed_point)
                    if point_to_edit:
                        points_to_edit_folder.append(point_to_edit)

                # Добавляем новую точку в коллекции
                if new_point is not None:
                    self.point_processor.add_point_to_data(new_point)
                    points_folder.append(new_point)

        # Создаем отчеты
        self._generate_reports(folder, points_folder, wrong_city_data_folder, points_to_edit_folder)

    def _generate_reports(self, folder: str, points: List[PointRecord],
                         wrong_cities: List[str], points_without_city: List[PointRecord]) -> None:
        """Генерация всех отчетов для папки."""
        # Excel и KML для обычных точек
        self.report_generator.create_excel_report(points, folder)
        self.report_generator.create_kml_files(points, folder)

        # Word отчет
        self.report_generator.create_word_report(points, wrong_cities, folder)

        # CSV и KML для точек без города
        self.report_generator.create_csv_report(points_without_city, folder)
        self.report_generator.create_kml_files(points_without_city, folder, "_without_city")

    def run(self, input_folder: str) -> None:
        """Запуск основного процесса обработки."""
        folders = self.folder_processor.find_target_folders(input_folder)
        total_folders = len(folders)

        for folder_index, folder in enumerate(folders, 1):
            # Отображаем статус обработки папки
            if self.status_callback:
                self.status_callback(f"Обработка папки {folder_index}/{total_folders}: {folder}")

            self.process_folder(folder)

        # Сохраняем все точки в основной базе
        self.points_data.save()



def find_and_parse_files(
    input_folder: str,
    city_data: CityData,
    points_data: PointsData,
    settings: Settings,
    log_message=None,
    status_callback=None,
) -> None:
    """
    Основная функция для поиска папок с отсутствующим data.xlsx, парсинга xml/json файлов и формирования отчетов.

    Использует объектно-ориентированную архитектуру с разделением ответственностей.

    Args:
        input_folder (str): Путь к корневой папке для поиска.
        city_data (CityData): Объект с данными о городах.
        points_data (PointsData): Объект с данными о всех ранее отмеченных точках.
        settings (Settings): Настройки приложения.
        log_message (callable, optional): Функция для логирования.
        status_callback (callable, optional): Функция для отображения статуса.

    Returns:
        None
    """
    # Создаем и запускаем пайплайн обработки
    pipeline = CorePipeline(
        city_data=city_data,
        points_data=points_data,
        settings=settings,
        log_message=log_message,
        status_callback=status_callback
    )

    pipeline.run(input_folder)
