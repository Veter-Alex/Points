"""
Основной модуль обработки файлов с точками.
Содержит главную логику парсинга XML/JSON файлов и создания отчетов.
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
) -> None:
    """
    Основная функция для поиска папок с отсутствующим data.xlsx и парсинга xml и json файлов.

    Args:
        input_folder (str): путь к корневой папке для поиска
        city_data (CityData): объект с данными о городах
        points_data (PointsData): объект с данными о всех ранее отмеченных точках
    """
    # Список для хранения городов, которые не удалось найти в city_data
    wrong_city_data: List[str] = []
    # Список для хранения точек без города
    points_to_edit: List[PointRecord] = []

    # Создаем обертку для get_sk42_coordinates с log_message
    def get_sk42_with_logging(lat: float, lon: float, log_msg=None):
        return get_sk42_coordinates(lat, lon, log_msg or log_message)

    # Проходим по всем папкам, где отсутствует data.xlsx
    for folder in find_folders_missing_data_csv(input_folder):
        log_message(f"Папка без data.xlsx: {folder}")
        # Список точек, найденных в текущей папке
        points_folder: List[PointRecord] = []
        # Перебираем все файлы в папке
        for file in os.listdir(folder):
            new_point: Optional[PointRecord] = None
            result_parse: Optional[PointRecord] = None
            # Если файл XML — парсим как XML
            if file.lower().endswith(".xml"):
                if log_message:
                    log_message(f"Парсинг XML: {file}")
                result_parse = parse_xml(os.path.join(folder, file), log_message)
            # Если файл JSON — парсим как JSON
            if file.lower().endswith(".json"):
                if log_message:
                    log_message(f"Парсинг JSON: {file}")
                result_parse = parse_json(os.path.join(folder, file), log_message)
            # Если удалось распарсить точку
            if result_parse is not None:
                # Если в точке указан город
                if result_parse.city is not None:
                    # Пытаемся найти город в city_data
                    found_city = find_city_by_name(city_data.records, result_parse.city)
                    if found_city:
                        # Если город найден — создаём точку с привязкой к городу
                        new_point = new_point_from_city_data(
                            found_city,
                            result_parse,
                            get_country_by_lat_lon,
                            get_sk42_with_logging,
                            log_message,
                        )
                    else:
                        # Если город не найден — логируем и добавляем в список не найденных
                        if log_message:
                            log_message(
                                f"Город не найден в city_data: {result_parse.city}",
                                color="red",
                                logger_level="warning",
                            )
                        else:
                            log_message(
                                f"Город не найден в city_data: {result_parse.city}",
                                color="red",
                                logger_level="warning",
                            )
                        country_eng, country_rus = get_country_by_lat_lon(
                            result_parse.latitude, result_parse.longitude
                        )
                        # Формируем строку для отчёта о не найденных городах
                        new_city = (
                            f"{result_parse.city}=н.п.НАЗВАНИЕ ГОРОДА_"
                            f"широта центра города_долгота центра города_"
                            f"{country_eng}_описание относитьно обласного центра_"
                            f"на территории {country_rus}"
                        )
                        wrong_city_data.append(new_city)
                else:
                    # Если город не указан — ищем точку по координатам среди уже отмеченных
                    found_point = find_point_by_lat_lon(
                        points_data.points,
                        result_parse.latitude,
                        result_parse.longitude,
                        0.01,  # Допустимая погрешность 1 км
                    )
                    if found_point:
                        # Если точка найдена, взять значение наименования города из найденной точки
                        result_parse.city = found_point.city
                        # Пытаемся найти город по полученному имени населённого пункта
                        found_city = find_city_by_name(
                            city_data.records, result_parse.city
                        )
                        if found_city:
                            # Если город найден — создаём точку с привязкой к городу
                            new_point = new_point_from_city_data(
                                found_city,
                                result_parse,
                                get_country_by_lat_lon,
                                get_sk42_with_logging,
                                log_message,
                            )

                    else:
                        # Если точка не найдена — создаём точку без города
                        point_to_edit = point_without_city(
                            result_parse,
                            get_country_by_lat_lon,
                            get_sk42_with_logging,
                            log_message,
                        )
                        if point_to_edit is not None:
                            points_to_edit.append(point_to_edit)

                # Если точка успешно создана — добавляем её в общий список
                if new_point is not None:
                    points_data.add_point(new_point)
                    points_folder.append(new_point)
                    if log_message:
                        log_message(
                            f"Добавлена точка: дата {new_point.date}, время {new_point.time}, {new_point.area_desc} координаты: широта={new_point.latitude}, долгота={new_point.longitude}",
                            color="blue",
                        )
                    else:
                        log_message(
                            f"Добавлена точка: дата {new_point.date}, время {new_point.time}, {new_point.area_desc} координаты: широта={new_point.latitude}, долгота={new_point.longitude}"
                        )

        # Если найдены точки — сохраняем их в Excel, создаём KML и Word-отчёт
        if points_folder:
            data_xlsx_path = os.path.join(folder, "data.xlsx")
            save_points_to_excel(points_folder, data_xlsx_path, log_message)
            if log_message:
                log_message(f"Точки сохранены в {data_xlsx_path}", color="blue")
            else:
                log_message(f"Точки сохранены в {data_xlsx_path}")
            # Для каждой точки создаём KML-файл
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
                if log_message:
                    log_message(f"Создан KML файл: {kml_file_path}", color="blue")
                else:
                    log_message(f"Создан KML файл: {kml_file_path}")
            # Создаём Word-отчёт по точкам
            create_word_report(
                points_folder, os.path.join(folder, "report.docx"), log_message
            )
            if log_message:
                log_message(
                    f"Создан Word отчёт: {os.path.join(folder, 'report.docx')}",
                    color="blue",
                )
            else:
                log_message(f"Создан Word отчёт: {os.path.join(folder, 'report.docx')}")

    # Сохраняем все точки в основной CSV
    points_data.save()

    # Если были города, которые не удалось найти — сохраняем их в отдельный файл
    if wrong_city_data:
        # Определяем путь к city.txt
        city_txt_path = getattr(settings, "cityDataFile", None) or "city.txt"
        city_txt_dir = os.path.dirname(city_txt_path)
        wrong_city_file = os.path.join(city_txt_dir, "wrong_cities.txt")
        if log_message:
            log_message("Не найденные города:", color="yellow", logger_level="debug")
            for city in wrong_city_data:
                log_message(f" - {city}", color="yellow", logger_level="debug")
        else:
            log_message("Не найденные города:", color="yellow", logger_level="debug")
            for city in wrong_city_data:
                log_message(f" - {city}", color="yellow", logger_level="debug")
        # Читаем уже существующие строки, если файл есть
        existing_cities = set()
        if os.path.exists(wrong_city_file):
            with open(wrong_city_file, "r", encoding="utf-8") as f:
                for line in f:
                    existing_cities.add(line.strip())
        # Добавляем только уникальные
        new_cities = [c for c in wrong_city_data if c not in existing_cities]
        if new_cities:
            with open(wrong_city_file, "a", encoding="utf-8") as f:
                for c in new_cities:
                    f.write(c + "\n")
            if log_message:
                log_message(
                    f"Не найденные города добавлены в {wrong_city_file}", color="yellow"
                )
            else:
                log_message(f"Не найденные города добавлены в {wrong_city_file}")
        else:
            if log_message:
                log_message(
                    f"Нет новых не найденных городов для добавления в {wrong_city_file}",
                    color="yellow",
                )
            else:
                log_message(
                    f"Нет новых не найденных городов для добавления в {wrong_city_file}"
                )

    # Если есть точки без города — сохраняем их в отдельный CSV-файл рядом с AllPoint.csv
    if points_to_edit:
        # Определяем путь к AllPoint.csv
        all_point_csv = getattr(points_data, "file_path", None) or settings.mainDataCSV
        all_point_dir = os.path.dirname(all_point_csv)
        points_to_edit_file = os.path.join(all_point_dir, "points_without_city.csv")
        if log_message:
            log_message("Точки без города:", color="yellow", logger_level="debug")
            for point in points_to_edit:
                log_message(
                    f" - дата: {point.date}, время: {point.time}, {point.area_desc}, координаты: широта={point.latitude}, долгота={point.longitude}",
                    color="yellow",
                    logger_level="debug",
                )
        else:
            log_message("Точки без города:", color="yellow", logger_level="debug")
            for point in points_to_edit:
                log_message(
                    f" - дата: {point.date}, время: {point.time}, {point.area_desc}, координаты: широта={point.latitude}, долгота={point.longitude}",
                    color="yellow",
                    logger_level="debug",
                )
        # Сохраняем точки без города в CSV
        save_points_without_city_to_csv(
            points_to_edit, points_to_edit_file, log_message
        )
