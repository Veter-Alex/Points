import csv
import os
import shutil
from datetime import datetime
from typing import Tuple, Dict, List, Optional
from dataclasses import dataclass

@dataclass
class PointRecord:
    date: str
    time: str
    latitude: float
    longitude: float
    x_sk42: int
    y_sk42: int
    country: str
    city: str
    area_desc: Optional[str]
    region_desc: Optional[str]
    original_text: str

class PointsData:
    """
    Класс для работы с данными из AllPoint.csv.
    Автоматически загружает данные при создании экземпляра.
    """
    FIELD_NAMES = [
        'Data', 'Time', 'Lat_WGS84', 'Lon_WGS84',
        'X_SK-42_Gauss_Kruger', 'Y_SK-42_Gauss_Kruger',
        'Country_Value', 'City_Value',
        'Description of the area', 'Description of the region',
        'Original text'
    ]
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.points: List[PointRecord] = []
        self.index: Dict[Tuple[float, float], PointRecord] = {}
        self.create_file_if_not_exists()  # Создать файл если нужно
        self.load()  # Автоматическая загрузка

    def create_file_if_not_exists(self):
        """Создать CSV-файл с заголовками если отсутствует"""
        if not os.path.exists(self.filepath):
            os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
            with open(self.filepath, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=self.FIELD_NAMES)
                writer.writeheader()

    def load(self):
        """Загрузить данные из файла с обработкой ошибок"""
        self.points.clear()
        self.index.clear()
        
        try:
            with open(self.filepath, encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for i, row in enumerate(reader, 1):
                    try:
                        # Обработка значений с защитой от ошибок
                        lat_str = row['Lat_WGS84'].replace('"', '').replace(',', '.')
                        lon_str = row['Lon_WGS84'].replace('"', '').replace(',', '.')
                        
                        point = PointRecord(
                            date=row['Data'],
                            time=row['Time'],
                            latitude=float(lat_str),
                            longitude=float(lon_str),
                            x_sk42=int(float(row['X_SK-42_Gauss_Kruger'])),
                            y_sk42=int(float(row['Y_SK-42_Gauss_Kruger'])),
                            country=row['Country_Value'],
                            city=row['City_Value'],
                            area_desc=row.get('Description of the area'),
                            region_desc=row.get('Description of the region'),
                            original_text=row['Original text']
                        )
                        self.points.append(point)
                        self.index[(point.latitude, point.longitude)] = point
                    except Exception as e:
                        print(f"Ошибка в строке {i}: {str(e)}")
        except FileNotFoundError:
            print(f"Файл {self.filepath} не найден, создан новый")
            self.create_file_if_not_exists()
        except Exception as e:
            print(f"Критическая ошибка загрузки: {str(e)}")

    def find_by_lat_lon(self, latitude: float, longitude: float) -> Optional[PointRecord]:
        """Поиск точки по координатам"""
        return self.index.get((round(latitude, 6), round(longitude, 6)))

    def add_point(self, point: PointRecord):
        """Добавить новую точку (с проверкой дубликатов)"""
        key = (round(point.latitude, 6), round(point.longitude, 6))
        if key in self.index:
            print(f"Точка с координатами ({point.latitude}, {point.longitude}) уже существует!")
            return False
            
        self.points.append(point)
        self.index[key] = point
        return True

    def save(self):
        """Сохранить все точки в файл с созданием бэкапа"""
        self.create_backup()  # Создать бэкап перед изменением
        
        with open(self.filepath, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=self.FIELD_NAMES)
            writer.writeheader()
            for p in self.points:
                writer.writerow({
                    'Data': p.date,
                    'Time': p.time,
                    'Lat_WGS84': f"{p.latitude:.6f}".replace('.', ','),
                    'Lon_WGS84': f"{p.longitude:.6f}".replace('.', ','),
                    'X_SK-42_Gauss_Kruger': p.x_sk42,
                    'Y_SK-42_Gauss_Kruger': p.y_sk42,
                    'Country_Value': p.country,
                    'City_Value': p.city,
                    'Description of the area': p.area_desc or '',
                    'Description of the region': p.region_desc or '',
                    'Original text': p.original_text
                })

    def create_backup(self):
        """Создать резервную копию файла"""
        if not os.path.exists(self.filepath):
            return
            
        backup_dir = os.path.join(os.path.dirname(self.filepath), 'backup')
        os.makedirs(backup_dir, exist_ok=True)
        
        # Формирование уникального имени бэкапа
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"{os.path.basename(self.filepath)}.{timestamp}.bak"
        backup_path = os.path.join(backup_dir, backup_name)
        
        shutil.copy2(self.filepath, backup_path)
        
        # Удаление старых бэкапов (оставить последние 10)
        backups = sorted(
            [f for f in os.listdir(backup_dir) if f.endswith('.bak')],
            reverse=True
        )
        for old_backup in backups[10:]:
            os.remove(os.path.join(backup_dir, old_backup))