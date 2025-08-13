
"""
Модуль для работы с точками наблюдения и их хранением в CSV.

Содержит классы и функции для загрузки, сохранения, поиска и резервного копирования точек.
Все классы и методы снабжены подробными комментариями и докстрингами согласно лучшим практикам.
"""

import csv
import os
import shutil
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Callable



@dataclass
class PointRecord:
    """
    Класс для хранения одной точки наблюдения.

    Args:
        date (str): Дата наблюдения.
        time (str): Время наблюдения.
        latitude (float): Широта.
        longitude (float): Долгота.
        x_sk42 (Optional[int]): X в системе СК-42.
        y_sk42 (Optional[int]): Y в системе СК-42.
        country (Optional[str]): Страна.
        city (Optional[str]): Город.
        area_desc (Optional[str]): Описание района.
        region_desc (Optional[str]): Описание региона.
        original_text (str): Исходный текст.
        file_path (Optional[str]): Путь к исходному файлу.
    """
    date: str
    time: str
    latitude: float
    longitude: float
    x_sk42: Optional[int]
    y_sk42: Optional[int]
    country: Optional[str]
    city: Optional[str]
    area_desc: Optional[str]
    region_desc: Optional[str]
    original_text: str
    file_path: Optional[str] = None




class PointsData:
    """
    Класс для работы с данными из AllPoint.csv.

    Автоматически загружает данные при создании экземпляра.
    Предоставляет методы для поиска, добавления, сохранения и резервного копирования точек.
    """

    FIELD_NAMES = [
        "Data",
        "Time",
        "Lat_WGS84",
        "Lon_WGS84",
        "X_SK-42_Gauss_Kruger",
        "Y_SK-42_Gauss_Kruger",
        "Country_Value",
        "City_Value",
        "Description of the area",
        "Description of the region",
        "Original text",
        "File_Path",
    ]

    def __init__(self, filepath: str, log_message: Callable[..., None]):
        """
        Инициализация PointsData: загрузка данных и создание файла при необходимости.

        Args:
            filepath (str): Путь к файлу данных точек.
            log_message (Callable): Функция для логирования.
        """
        self.filepath = filepath
        self.log_message = log_message
        self.points: List[PointRecord] = []
        self.index: Dict[Tuple[float, float], PointRecord] = {}
        self.create_file_if_not_exists()
        self.load()

    def create_file_if_not_exists(self) -> None:
        """
        Создать CSV-файл с заголовками, если он отсутствует.
        """
        if not os.path.exists(self.filepath):
            self.log_message(
                f"Файл {self.filepath} не найден. Создаю новый с заголовками.",
                color="blue",
                logger_level="info",
            )
            # Создаём директорию, если нужно
            try:
                dir_path = os.path.dirname(self.filepath)
                if dir_path:
                    os.makedirs(dir_path, exist_ok=True)
            except OSError as e:
                self.log_message(
                    f"Ошибка создания директории: {e}",
                    color="red",
                    logger_level="error",
                )
                raise
            # Создаём файл с заголовками
            try:
                with open(self.filepath, "w", encoding="utf-8", newline="") as f:
                    writer = csv.DictWriter(f, fieldnames=self.FIELD_NAMES)
                    writer.writeheader()
            except OSError as e:
                self.log_message(
                    f"Ошибка создания файла: {e}", color="red", logger_level="error"
                )
                raise
            self.log_message(
                f"Файл создан: {self.filepath}", color="blue", logger_level="info"
            )

    def load(self) -> None:
        """
        Загрузить данные из файла с обработкой ошибок и логированием.
        Оптимизированная версия для быстрой загрузки больших файлов.
        """
        self.log_message(
            f"Загрузка данных из {self.filepath}", color="blue", logger_level="info"
        )

        self.points.clear()
        self.index.clear()

        # Функции для быстрого преобразования типов
        def safe_int_from_float(value: str) -> Optional[int]:
            try:
                return int(float(value)) if value and value.strip() else None
            except (ValueError, TypeError):
                return None

        def safe_float(value: str) -> float:
            try:
                return float(value) if value else 0.0
            except (ValueError, TypeError):
                return 0.0

        try:
            with open(self.filepath, encoding="utf-8") as f:
                reader = csv.DictReader(f)
                points_batch = []

                for i, row in enumerate(reader, 1):
                    try:
                        # Ускоренное извлечение координат
                        lat_str = (row.get("Lat_WGS84") or "").replace('"', "")
                        lon_str = (row.get("Lon_WGS84") or "").replace('"', "")

                        latitude = safe_float(lat_str)
                        longitude = safe_float(lon_str)

                        # Ускоренное преобразование СК-42 координат
                        x_sk42 = safe_int_from_float(row.get("X_SK-42_Gauss_Kruger", ""))
                        y_sk42 = safe_int_from_float(row.get("Y_SK-42_Gauss_Kruger", ""))

                        # Быстрое извлечение остальных полей
                        point = PointRecord(
                            date=row.get("Data", ""),
                            time=row.get("Time", ""),
                            latitude=latitude,
                            longitude=longitude,
                            x_sk42=x_sk42,
                            y_sk42=y_sk42,
                            country=row.get("Country_Value", ""),
                            city=row.get("City_Value", ""),
                            area_desc=row.get("Description of the area"),
                            region_desc=row.get("Description of the region"),
                            original_text=row.get("Original text", ""),
                            file_path=row.get("File_Path"),
                        )

                        points_batch.append(point)

                        # Обрабатываем батчами для лучшей производительности
                        if len(points_batch) >= 1000:
                            self.points.extend(points_batch)
                            for p in points_batch:
                                self.index[(p.latitude, p.longitude)] = p
                            points_batch.clear()

                    except Exception as e:
                        self.log_message(
                            f"Ошибка в строке {i}: {str(e)}",
                            color="red",
                            logger_level="error",
                        )

                # Добавляем оставшиеся точки
                if points_batch:
                    self.points.extend(points_batch)
                    for p in points_batch:
                        self.index[(p.latitude, p.longitude)] = p

        except FileNotFoundError:
            self.log_message(
                f"Файл {self.filepath} не найден, создан новый",
                color="orange",
                logger_level="warning",
            )
            self.create_file_if_not_exists()
        except Exception as e:
            self.log_message(
                f"Критическая ошибка загрузки: {str(e)}",
                color="red",
                logger_level="critical",
            )

        self.log_message(
            f"Загружено {len(self.points)} точек из {self.filepath}",
            color="blue",
            logger_level="info",
        )

    def find_by_lat_lon(self, latitude: float, longitude: float) -> Optional[PointRecord]:
        """
        Поиск точки по точным координатам (без округления).

        Args:
            latitude (float): Широта.
            longitude (float): Долгота.

        Returns:
            Optional[PointRecord]: Найденная точка или None.
        """
        return self.index.get((latitude, longitude))

    def add_point(self, point: PointRecord) -> bool:
        """
        Добавить новую точку (дубликат — совпадение по дате, времени и координатам).

        Args:
            point (PointRecord): Точка для добавления.

        Returns:
            bool: True, если точка добавлена, иначе False.
        """
        for p in self.points:
            if (
                p.latitude == point.latitude
                and p.longitude == point.longitude
                and p.date == point.date
                and p.time == point.time
            ):
                self.log_message(
                    f"Дубликат: точка с координатами ({point.latitude}, {point.longitude}) и датой/временем {point.date} {point.time} уже существует!",
                    color="orange",
                    logger_level="warning",
                )
                return False
        self.points.append(point)
        self.index[(point.latitude, point.longitude)] = point
        return True

    def save(self) -> None:
        """
        Сохранить все точки в файл с созданием бэкапа.
        Перед сохранением удаляет дубликаты эффективным способом.
        """
        self.create_backup()

        # Эффективная дедупликация с сохранением порядка
        seen_keys = set()
        unique_points = []

        for p in self.points:
            # Ключ для определения уникальности: координаты + дата + время
            key = (p.latitude, p.longitude, p.date, p.time)
            if key not in seen_keys:
                seen_keys.add(key)
                unique_points.append(p)

        # Логируем информацию о дубликатах, если они были найдены
        duplicates_count = len(self.points) - len(unique_points)
        if duplicates_count > 0:
            self.log_message(
                f"Обнаружено и удалено {duplicates_count} дубликатов перед сохранением",
                color="orange",
                logger_level="warning",
            )

        # Обновляем внутренний список и перестраиваем индекс одним проходом
        self.points = unique_points
        self.index = {(p.latitude, p.longitude): p for p in unique_points}

        # Подготавливаем данные для записи (избегаем повторных обращений к атрибутам)
        rows_data = []
        for p in unique_points:
            rows_data.append({
                "Data": p.date,
                "Time": p.time,
                "Lat_WGS84": f"{p.latitude:.6f}",
                "Lon_WGS84": f"{p.longitude:.6f}",
                "X_SK-42_Gauss_Kruger": (
                    p.x_sk42 if p.x_sk42 is not None else ""
                ),
                "Y_SK-42_Gauss_Kruger": (
                    p.y_sk42 if p.y_sk42 is not None else ""
                ),
                "Country_Value": p.country,
                "City_Value": p.city,
                "Description of the area": p.area_desc or "",
                "Description of the region": p.region_desc or "",
                "Original text": p.original_text,
                "File_Path": p.file_path or "",
            })

        # Записываем в файл одним блоком
        with open(self.filepath, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=self.FIELD_NAMES)
            writer.writeheader()
            writer.writerows(rows_data)

    def create_backup(self) -> None:
        """
        Создать резервную копию файла (оставляет только 10 последних бэкапов).
        """
        if not os.path.exists(self.filepath):
            return
        backup_dir = os.path.join(os.path.dirname(self.filepath), "backup")
        os.makedirs(backup_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{os.path.basename(self.filepath)}.{timestamp}.bak"
        backup_path = os.path.join(backup_dir, backup_name)
        shutil.copy2(self.filepath, backup_path)
        backups = sorted(
            [f for f in os.listdir(backup_dir) if f.endswith(".bak")], reverse=True
        )
        for old_backup in backups[10:]:
            os.remove(os.path.join(backup_dir, old_backup))
