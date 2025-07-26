from dataclasses import dataclass
from typing import List, Optional, Dict
import re
import os
import shutil
from datetime import datetime
from .city_template import CITY_TXT_TEMPLATE

@dataclass
class CityRecord:
    name_original: str
    name_ru: str
    latitude: float
    longitude: float
    country: Optional[str] = None
    description: Optional[str] = None
    region: Optional[str] = None


class CityData:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.records: List[CityRecord] = []
        self.create_file_if_not_exists()
        self.load()  # Автозагрузка при инициализации

    def create_file_if_not_exists(self):
        """Создаёт файл с шаблоном при отсутствии"""
        if not os.path.exists(self.filepath):
            os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
            with open(self.filepath, 'w', encoding='utf-8') as f:
                f.write(CITY_TXT_TEMPLATE)

    def load(self):
        """Загружает данные с обработкой ошибок"""
        self.records = []
        try:
            with open(self.filepath, encoding='utf-8') as f:
                for i, line in enumerate(f, 1):
                    line = line.strip()
                    if not line or line.startswith("'"):
                        continue
                    if record := self.parse_line(line):
                        self.records.append(record)
        except Exception as e:
            print(f"Ошибка загрузки {self.filepath}: {str(e)}")

    @staticmethod
    def parse_line(line: str) -> Optional[CityRecord]:
        """Парсинг строки с обработкой ошибок и логированием"""
        try:
            name_original, rest = line.split('=', 1)
            parts = rest.split('_')
            
            # Базовые обязательные поля
            if len(parts) < 4:
                raise ValueError(f"Недостаточно частей в строке: {line}")
                
            name_ru = parts[0]
            latitude = float(parts[1].replace(',', '.'))
            longitude = float(parts[2].replace(',', '.'))
            country = parts[3]
            
            # Опциональные поля
            description = parts[4] if len(parts) > 4 else None
            region = parts[5] if len(parts) > 5 else None
            
            # Проверка на пустые значения
            if not all([name_original, name_ru, country]):
                raise ValueError("Обязательные поля пусты")
                
            return CityRecord(
                name_original=name_original,
                name_ru=name_ru,
                latitude=latitude,
                longitude=longitude,
                country=country,
                description=description,
                region=region
            )
        except Exception as e:
            print(f"Ошибка парсинга строки: '{line}'\nПричина: {str(e)}")
            return None

    def get_by_country(self, country: str) -> List[CityRecord]:
        return [rec for rec in self.records if rec.country == country]

    def get_by_name(self, name: str) -> Optional[CityRecord]:
        name_lower = name.lower()
        for rec in self.records:
            if rec.name_original.lower() == name_lower or rec.name_ru.lower() == name_lower:
                return rec
        return None

    def add_city(self, city: CityRecord):
        """Упрощённое добавление города с перезаписью файла"""
        # Проверка дубликатов
        if self.get_by_name(city.name_original) or self.get_by_name(city.name_ru):
            print(f"Город {city.name_ru} уже существует!")
            return
            
        self.records.append(city)
        self.save_data_to_file()

    def save_data_to_file(self):
        """Полная перезапись файла из актуальных данных"""
        # Группировка по странам
        countries: Dict[str, List[CityRecord]] = {}
        for rec in self.records:
            if rec.country not in countries:
                countries[rec.country] = []
            countries[rec.country].append(rec)
        
        # Сортировка стран и городов
        sorted_countries = sorted(countries.keys())
        lines = []
        
        for country in sorted_countries:
            lines.append(f"' ================== {country.upper()} ==================")
            for city in sorted(countries[country], key=lambda c: c.name_original):
                lines.append(self._city_to_line(city))
            lines.append("")  # Пустая строка после блока
        
        # Создание бэкапа
        self.create_backup()
        
        # Запись в файл
        with open(self.filepath, 'w', encoding='utf-8') as f:
            f.write("\n".join(lines))

    def create_backup(self):
        """Управление бэкапами с сортировкой по timestamp"""
        if not os.path.exists(self.filepath):
            return
            
        backup_dir = os.path.join(os.path.dirname(self.filepath), 'backup')
        os.makedirs(backup_dir, exist_ok=True)
        
        # Формирование имени с timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"{os.path.basename(self.filepath)}.{timestamp}.bak"
        backup_path = os.path.join(backup_dir, backup_name)
        
        shutil.copy2(self.filepath, backup_path)
        
        # Удаление старых бэкапов (последние 10)
        backups = sorted(
            [f for f in os.listdir(backup_dir) if f.endswith('.bak')],
            reverse=True
        )
        for old_backup in backups[10:]:
            os.remove(os.path.join(backup_dir, old_backup))

    @staticmethod
    def _city_to_line(city: CityRecord) -> str:
        """Безопасное формирование строки"""
        # Замена запрещённых символов
        def safe_value(value: Optional[str]) -> str:
            if not value:
                return ""
            return value.replace("_", "-").replace("=", "-")
        
        return (
            f"{safe_value(city.name_original)}="
            f"{safe_value(city.name_ru)}_"
            f"{str(city.latitude).replace('.', ',')}_"
            f"{str(city.longitude).replace('.', ',')}_"
            f"{safe_value(city.country)}_"
            f"{safe_value(city.description)}_"
            f"{safe_value(city.region)}"
        )