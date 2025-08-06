
"""
Модуль для работы с городами и их данными.

Содержит классы и функции для загрузки, сохранения, парсинга и управления данными о городах.
Все классы и методы снабжены подробными комментариями и докстрингами согласно лучшим практикам.
"""

import os
import shutil
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Callable

from .city_template import CITY_TXT_TEMPLATE



@dataclass
class CityRecord:
    """
    Структура для хранения информации о городе.

    Args:
        name_original (str): Оригинальное название города.
        name_ru (str): Русское название города.
        latitude (float): Широта города.
        longitude (float): Долгота города.
        country (Optional[str]): Страна.
        description (Optional[str]): Описание.
        region (Optional[str]): Регион.
    """
    name_original: str
    name_ru: str
    latitude: float
    longitude: float
    country: Optional[str] = None
    description: Optional[str] = None
    region: Optional[str] = None



class CityData:
    """
    Класс для управления данными о городах.

    Позволяет загружать, сохранять, парсить и управлять списком городов.
    Все методы снабжены подробными комментариями и докстрингами.
    """
    def __init__(self, filepath: str, log_message):
        """
        Инициализация CityData: путь к файлу, автосоздание и автозагрузка данных.

        Args:
            filepath (str): Путь к файлу данных о городах.
            log_message (callable): Функция для логирования.
        """
        self.filepath = filepath
        self.log_message = log_message
        self.records: List[CityRecord] = []
        self.create_file_if_not_exists()
        self.load()  # Автозагрузка при инициализации

    def create_file_if_not_exists(self):
        """
        Создаёт файл с шаблоном при отсутствии.
        """
        if not os.path.exists(self.filepath):
            self.log_message(
                f"Файл {self.filepath} с описанием населённых пунктов не найден."
                f" Создаю новый с шаблоном.",
                color="blue",
                logger_level="info",
            )

            # Создаём директорию, если нужно
            try:
                os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
            except OSError as e:
                self.log_message(
                    f"Ошибка создания директории: {e}",
                    color="red",
                    logger_level="error",
                )
                raise
            # Создаём файл с шаблоном
            try:
                with open(self.filepath, "w", encoding="utf-8") as f:
                    f.write(CITY_TXT_TEMPLATE)
            except OSError as e:
                self.log_message(
                    f"Ошибка создания файла: {e}", color="red", logger_level="error"
                )
                raise
            self.log_message(
                f"Файл создан: {self.filepath}", color="blue", logger_level="info"
            )

    def load(self):
        """
        Загружает данные из файла.

        При ошибке логирует и выбрасывает исключение.
        Пропускает строки без символа '=' (например, разделители и комментарии).
        """
        self.records = []
        self.log_message(
            f"Загрузка данных из {self.filepath}", color="blue", logger_level="info"
        )

        try:
            with open(self.filepath, encoding="utf-8") as f:
                for i, line in enumerate(f, 1):
                    line = line.strip()
                    if not line or line.startswith("'") or "=" not in line:
                        continue
                    try:
                        record = self.parse_line(line)
                        if record:
                            self.records.append(record)
                    except Exception as e:
                        self.log_message(
                            f"Ошибка парсинга строки {i} в {self.filepath}: {e}",
                            color="red",
                            logger_level="error",
                        )
                        raise
        except Exception as e:
            self.log_message(
                f"Ошибка загрузки {self.filepath}: {e}",
                color="red",
                logger_level="error",
            )
            raise
        self.log_message(
            f"Загружено {len(self.records)} записей из {self.filepath}",
            color="blue",
            logger_level="info",
        )

    @staticmethod
    def parse_line(line: str) -> Optional[CityRecord]:
        """
        Парсинг строки с обработкой ошибок и логированием.

        Формат строки:
            <Оригинальное_название>=<Русское_название>_<широта>_<долгота>_<страна>_<описание>_<регион>

        Args:
            line (str): Строка для парсинга.

        Returns:
            Optional[CityRecord]: Объект CityRecord или выбрасывает ValueError при ошибке.
        """
        try:
            name_original, rest = line.split("=", 1)
            parts = rest.split("_")

            # Проверяем минимальное количество частей (название, широта, долгота, страна)
            if len(parts) < 4:
                raise ValueError(f"Недостаточно частей в строке: {line}")

            # Обязательные поля
            name_ru = parts[0]
            latitude = float(
                parts[1].replace(",", ".")
            )  # Поддержка старого формата с запятыми
            longitude = float(
                parts[2].replace(",", ".")
            )  # Поддержка старого формата с запятыми
            country = parts[3] if parts[3] else None

            # Опциональные поля
            description = parts[4] if len(parts) > 4 and parts[4] else None
            region = parts[5] if len(parts) > 5 and parts[5] else None

            # Проверка на пустые обязательные значения
            if not all([name_original.strip(), name_ru.strip()]):
                raise ValueError("Обязательные поля пусты")

            return CityRecord(
                name_original=name_original.strip(),
                name_ru=name_ru.strip(),
                latitude=latitude,
                longitude=longitude,
                country=country.strip() if country else None,
                description=description.strip() if description else None,
                region=region.strip() if region else None,
            )
        except Exception as e:
            # В статическом методе не можем использовать self._log, используем print
            print(f"Ошибка парсинга строки: '{line}' Причина: {e}")
            raise

    def get_by_country(self, country: str) -> List[CityRecord]:
        """
        Получить список городов по стране.

        Args:
            country (str): Название страны.

        Returns:
            List[CityRecord]: Список городов в указанной стране.
        """
        return [rec for rec in self.records if rec.country == country]

    def get_by_name(self, name: str) -> Optional[CityRecord]:
        """
        Получить город по оригинальному названию (без учёта регистра).

        Args:
            name (str): Оригинальное название города.

        Returns:
            Optional[CityRecord]: Найденный город или None.
        """
        name_lower = name.lower()
        for rec in self.records:
            if rec.name_original.lower() == name_lower:
                return rec
        return None

    def add_city(self, city: CityRecord):
        """
        Добавить город (только если нет дубликата по name_original), затем сохранить файл.

        Args:
            city (CityRecord): Город для добавления.
        """
        if self.get_by_name(city.name_original):
            self.log_message(
                f"Город с оригинальным названием '{city.name_original}' уже существует!",
                color="orange",
                logger_level="warning",
            )
            return
        self.records.append(city)
        self.save_data_to_file()

    def save_data_to_file(self):
        """
        Полная перезапись файла из актуальных данных с бэкапом.

        Сохраняет в формате: комментарии + отсортированные по алфавиту записи.
        """
        # Создаем бэкап перед сохранением
        self.create_backup()

        # Комментарии в начале файла
        header_comments = [
            "' =====================================================================================",
            "' Географическая база данных для анализа погодных данных (city.txt)",
            "'",
            "' Формат файла:",
            "' <Оригинальное_название>=<Русское_название>_<широта>_<долгота>_<страна>_<описание>_<регион>",
            "",
            "' - Пример строки:",
            "'   Babayevka=н.п.Бабинка_53.243_33.119_Россия_83 км зап. г.Брянск_на территории Брянской области",
            "'   Krolevets=н.п.Кролевец_51.547029_33.379761_Украина_122 км сев.-зап. г.Сумы_на территории Украины",
            "'   Belgorod=г.Белгород_50.595414_36.587277_Россия__на территории Белгородской области",
            "'   London=г.Лондон_51.505064_-0.126634_Англия__на территории Англии",
            "'",
            "' - Все строки-комментарии начинаются с одинарной кавычки (') и игнорируются при обработке.",
            "' - Строки с описанием отсортированы по алфавиту.",
            "' - Должен быть знак равно после оригинального названия города (без пробелов)",
            "' - Широта и долгота указываются через точку (например: 50.450441).",
            "' - Страна указывается всегда (например: Россия, Украина, Китай, ...).",
            "' - Описание и регион могут быть пустыми.",
            "'",
            "",
        ]

        # Сортируем записи по оригинальному названию
        sorted_records = sorted(self.records, key=lambda c: c.name_original.lower())

        # Формируем строки данных
        data_lines = [self._city_to_line(city) for city in sorted_records]

        # Записываем файл
        with open(self.filepath, "w", encoding="utf-8") as f:
            # Записываем комментарии
            for comment in header_comments:
                f.write(comment + "\n")

            # Записываем данные
            for line in data_lines:
                f.write(line + "\n")

        self.log_message(
            f"Сохранено {len(sorted_records)} записей в {self.filepath}",
            color="blue",
            logger_level="info",
        )

    def create_backup(self):
        """
        Создать бэкап файла и удалить старые (оставить 10 последних).
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

    @staticmethod
    def _city_to_line(city: CityRecord) -> str:
        """
        Безопасное формирование строки для записи города в файл.

        Формат:
            <Оригинальное_название>=<Русское_название>_<широта>_<долгота>_<страна>_<описание>_<регион>

        Args:
            city (CityRecord): Город для сериализации.

        Returns:
            str: Строка для записи в файл.
        """

        def safe_value(value: Optional[str]) -> str:
            if not value:
                return ""
            return value.replace("_", "-").replace("=", "-")

        # Координаты используют точку как разделитель
        latitude_str = str(city.latitude)
        longitude_str = str(city.longitude)

        # Страна всегда должна быть указана
        country = safe_value(city.country) if city.country else "Неизвестно"

        # Описание может быть пустым (двойное подчеркивание)
        description = safe_value(city.description) if city.description else ""

        # Регион всегда должен быть указан
        region = safe_value(city.region) if city.region else f"на территории {country}"

        return (
            f"{safe_value(city.name_original)}="
            f"{safe_value(city.name_ru)}_"
            f"{latitude_str}_"
            f"{longitude_str}_"
            f"{country}_"
            f"{description}_"
            f"{region}"
        )
