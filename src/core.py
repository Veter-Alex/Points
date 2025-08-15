

"""
Основной модуль обработки файлов с точками.

Содержит главную логику парсинга XML/JSON файлов, создания отчетов и сохранения данных.
Все функции снабжены подробными комментариями и докстрингами согласно лучшим практикам.
"""

import csv
import os
from typing import List, Optional

from models.city import CityData, CityRecord
from models.points import PointRecord, PointsData
from models.settings import Settings
from src.city_manager import find_city_by_name, get_area_desc
from src.excel_manager import save_points_to_excel, save_points_without_city_to_csv
from src.file_manager import find_folders_missing_data_csv
from src.geo_manager import get_country_by_lat_lon, get_sk42_coordinates
from src.kml_manager import create_kml_file
from src.parsers import parse_json, parse_xml
from src.points_manager import (
    find_point_by_lat_lon,
    new_point_from_city_data,
    point_without_city,
)
from src.word_report_manager import create_word_report



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

    def log(msg, color=None, logger_level=None):
        """
        Вспомогательная функция для логирования сообщений.

        Args:
            msg (str): Сообщение.
            color (str, optional): Цвет сообщения.
            logger_level (str, optional): Уровень логирования.
        """
        if log_message:
            log_message(msg, color=color, logger_level=logger_level)

    def get_sk42_with_logging(lat: float, lon: float, log_msg=None):
        """
        Вспомогательная функция для получения координат СК-42 с логированием.

        Args:
            lat (float): Широта.
            lon (float): Долгота.
            log_msg (callable, optional): Функция для логирования.

        Returns:
            tuple: Координаты СК-42.
        """
        return get_sk42_coordinates(lat, lon, log_msg or log_message)

    folders = find_folders_missing_data_csv(input_folder)
    total_folders = len(folders)
    for folder_index, folder in enumerate(folders, 1):
        # Отображаем статус обработки папки
        if status_callback:
            status_callback(f"Обработка папки {folder_index}/{total_folders}: {folder}")
        log(f"Папка без data.xlsx: {folder}")
        points_folder: List[PointRecord] = []
        wrong_city_data_folder: List[str] = []
        points_to_edit_folder: List[PointRecord] = []
        for file in os.listdir(folder):
            new_point: Optional[PointRecord] = None
            result_parse: Optional[PointRecord] = None
            # Парсим XML/JSON файлы
            if file.lower().endswith(".xml"):
                log(f"Парсинг XML: {file}")
                result_parse = parse_xml(os.path.join(folder, file), log_message)
            elif file.lower().endswith(".json"):
                log(f"Парсинг JSON: {file}")
                result_parse = parse_json(os.path.join(folder, file), log_message)
            # Обработка результата парсинга
            if result_parse is not None:
                if result_parse.city is not None:
                    found_city = find_city_by_name(city_data.records, result_parse.city)
                    if found_city:
                        new_point = new_point_from_city_data(
                            found_city,
                            result_parse,
                            get_country_by_lat_lon,
                            get_sk42_with_logging,
                            log_message,
                        )
                    else:
                        log(
                            f"Город не найден в city_data: {result_parse.city}",
                            color="red",
                            logger_level="warning",
                        )
                        country_eng, country_rus = get_country_by_lat_lon(
                            result_parse.latitude, result_parse.longitude
                        )
                        new_city = (
                            f"{result_parse.city}=н.п.НАЗВАНИЕ ГОРОДА_"
                            f"широта центра города_долгота центра города_"
                            f"{country_eng}_описание относитьно обласного центра_"
                            f"на территории {country_rus}"
                        )
                        wrong_city_data_folder.append(new_city)
                else:
                    found_point = find_point_by_lat_lon(
                        points_data.points,
                        result_parse.latitude,
                        result_parse.longitude,
                        0.01,
                    )
                    if found_point:
                        result_parse.city = found_point.city
                        found_city = find_city_by_name(
                            city_data.records, result_parse.city
                        )
                        if found_city:
                            new_point = new_point_from_city_data(
                                found_city,
                                result_parse,
                                get_country_by_lat_lon,
                                get_sk42_with_logging,
                                log_message,
                            )
                    else:
                        point_to_edit = point_without_city(
                            result_parse,
                            get_country_by_lat_lon,
                            get_sk42_with_logging,
                            log_message,
                        )
                        if point_to_edit is not None:
                            points_to_edit_folder.append(point_to_edit)
                if new_point is not None:
                    points_data.add_point(new_point)
                    points_folder.append(new_point)
                    log(
                        f"Добавлена точка: дата {new_point.date}, время {new_point.time}, {new_point.area_desc} координаты: широта={new_point.latitude}, долгота={new_point.longitude}",
                        color="blue",
                    )
        # Сохраняем точки в Excel и создаем KML-файлы
        if points_folder:
            data_xlsx_path = os.path.join(folder, "data.xlsx")
            save_points_to_excel(points_folder, data_xlsx_path, log_message)
            log(f"Точки сохранены в {data_xlsx_path}", color="blue")
            for point in points_folder:
                if point.file_path:
                    base_name = os.path.splitext(os.path.basename(point.file_path))[0]
                    kml_file_path = os.path.join(folder, f"{base_name}.kml")
                else:
                    kml_file_path = os.path.join(
                        folder,
                        f"point_{point.latitude}_{point.longitude}_{point.time.replace(':', '')}.kml",
                    )
                create_kml_file(point, kml_file_path, log_message)
                log(f"Создан KML файл: {kml_file_path}", color="blue")
        # Создаем Word-отчет
        if wrong_city_data_folder or points_folder:
            create_word_report(
                points_folder, wrong_city_data_folder, os.path.join(folder, "report.docx"), log_message
            )
            log(f"Создан Word отчёт: {os.path.join(folder, 'report.docx')}", color="blue")
        # Сохраняем точки без города в отдельный CSV
        if points_to_edit_folder:
            points_to_edit_file = os.path.join(folder, "points_without_city.csv")
            log("Точки без города в текущей папке:", color="orange", logger_level="debug")
            for point in points_to_edit_folder:
                log(
                    f" - дата: {point.date}, время: {point.time}, {point.area_desc}, координаты: широта={point.latitude}, долгота={point.longitude}",
                    color="orange",
                    logger_level="debug",
                )
            save_points_without_city_to_csv(
                points_to_edit_folder, points_to_edit_file, log_message
            )
            
            # Создаем KML файлы для точек без города
            for point in points_to_edit_folder:
                if point.file_path:
                    base_name = os.path.splitext(os.path.basename(point.file_path))[0]
                    kml_file_path = os.path.join(folder, f"{base_name}_without_city.kml")
                else:
                    kml_file_path = os.path.join(
                        folder,
                        f"point_without_city_{point.latitude}_{point.longitude}_{point.time.replace(':', '')}.kml",
                    )
                create_kml_file(point, kml_file_path, log_message)
                log(f"Создан KML файл для точки без города: {kml_file_path}", color="orange")
    # Сохраняем все точки в основной базе
    points_data.save()
