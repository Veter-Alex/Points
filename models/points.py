import csv
import os
import shutil
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from src.logger import logger


@dataclass
class PointRecord:
    """
    Класс для хранения одной точки наблюдения.
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

    def __init__(self, filepath: str):
        """
        Инициализация PointsData: загрузка данных и создание файла при необходимости.
        """
        self.filepath = filepath
        self.points: List[PointRecord] = []
        self.index: Dict[Tuple[float, float], PointRecord] = {}
        self.create_file_if_not_exists()
        self.load()

    def create_file_if_not_exists(self):
        """
        Создать CSV-файл с заголовками, если он отсутствует.
        """
        if not os.path.exists(self.filepath):
            logger.info(f"Файл {self.filepath} не найден. Создаю новый с заголовками.")
            # Создаём директорию, если нужно
            try:
                dir_path = os.path.dirname(self.filepath)
                if dir_path:
                    os.makedirs(dir_path, exist_ok=True)
            except OSError as e:
                logger.error(f"Ошибка создания директории: {e}")
                raise
            # Создаём файл с заголовками
            try:
                with open(self.filepath, "w", encoding="utf-8", newline="") as f:
                    writer = csv.DictWriter(f, fieldnames=self.FIELD_NAMES)
                    writer.writeheader()
            except OSError as e:
                logger.error(f"Ошибка создания файла: {e}")
                raise
            logger.info(f"Файл создан: {self.filepath}")

    def load(self):
        """
        Загрузить данные из файла с обработкой ошибок и логированием.
        """
        logger.info(f"Загрузка данных из {self.filepath}")

        self.points.clear()
        self.index.clear()
        try:
            with open(self.filepath, encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for i, row in enumerate(reader, 1):
                    try:
                        lat_str = (row.get("Lat_WGS84") or "").replace('"', "")
                        lon_str = (row.get("Lon_WGS84") or "").replace('"', "")
                        x_sk42_raw = row.get("X_SK-42_Gauss_Kruger")
                        y_sk42_raw = row.get("Y_SK-42_Gauss_Kruger")
                        try:
                            x_sk42 = (
                                int(float(x_sk42_raw))
                                if x_sk42_raw and x_sk42_raw.strip()
                                else None
                            )
                        except Exception as e:
                            logger.warning(
                                f"Ошибка преобразования X_SK-42_Gauss_Kruger в строке {i}: {x_sk42_raw} — {e}"
                            )
                            x_sk42 = None
                        try:
                            y_sk42 = (
                                int(float(y_sk42_raw))
                                if y_sk42_raw and y_sk42_raw.strip()
                                else None
                            )
                        except Exception as e:
                            logger.warning(
                                f"Ошибка преобразования Y_SK-42_Gauss_Kruger в строке {i}: {y_sk42_raw} — {e}"
                            )
                            y_sk42 = None
                        area_desc = (
                            row.get("Description of the area")
                            if "Description of the area" in row
                            else None
                        )
                        region_desc = (
                            row.get("Description of the region")
                            if "Description of the region" in row
                            else None
                        )
                        file_path = row.get("File_Path", None)
                        point = PointRecord(
                            date=row.get("Data", ""),
                            time=row.get("Time", ""),
                            latitude=float(lat_str) if lat_str else 0.0,
                            longitude=float(lon_str) if lon_str else 0.0,
                            x_sk42=x_sk42,
                            y_sk42=y_sk42,
                            country=row.get("Country_Value", ""),
                            city=row.get("City_Value", ""),
                            area_desc=area_desc,
                            region_desc=region_desc,
                            original_text=row.get("Original text", ""),
                            file_path=file_path,
                        )
                        self.points.append(point)
                        self.index[(point.latitude, point.longitude)] = point
                    except Exception as e:
                        logger.error(f"Ошибка в строке {i}: {str(e)}; row={row}")
        except FileNotFoundError:
            logger.warning(f"Файл {self.filepath} не найден, создан новый")
            self.create_file_if_not_exists()
        except Exception as e:
            logger.critical(f"Критическая ошибка загрузки: {str(e)}")
        logger.info(f"Загружено {len(self.points)} точек из {self.filepath}")

    def find_by_lat_lon(
        self, latitude: float, longitude: float
    ) -> Optional[PointRecord]:
        """
        Поиск точки по точным координатам (без округления).
        """
        return self.index.get((latitude, longitude))

    def add_point(self, point: PointRecord) -> bool:
        """
        Добавить новую точку (дубликат — совпадение по дате, времени и координатам).
        Возвращает True, если точка добавлена, иначе False.
        """
        for p in self.points:
            if (
                p.latitude == point.latitude
                and p.longitude == point.longitude
                and p.date == point.date
                and p.time == point.time
            ):
                logger.warning(
                    f"Дубликат: точка с координатами ({point.latitude}, {point.longitude}) и датой/временем {point.date} {point.time} уже существует!"
                )
                return False
        self.points.append(point)
        self.index[(point.latitude, point.longitude)] = point
        return True

    def save(self):
        """
        Сохранить все точки в файл с созданием бэкапа.
        """
        self.create_backup()
        with open(self.filepath, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=self.FIELD_NAMES)
            writer.writeheader()
            for p in self.points:
                writer.writerow(
                    {
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
                    }
                )

    def create_backup(self):
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
