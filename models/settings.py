

"""
Модуль для управления настройками приложения PointsManager.

Содержит класс Settings с методами для загрузки, сохранения, проверки и сериализации настроек.
Все классы и методы снабжены подробными комментариями и докстрингами согласно лучшим практикам.
"""

import os
from typing import Any, Dict
import logging

logger = logging.getLogger("PointsManager")




class Settings:
    """
    Класс для хранения и управления настройками приложения PointsManager.

    Автоматически загружает настройки при создании экземпляра.
    Предоставляет методы для проверки, сериализации и сохранения настроек.
    """

    def __init__(
        self,
        config_path: str = "settings.txt",
        rootFolder: str = "INPUT",
        mainDataCSV: str = "data/AllPoint.csv",
        cityDataFile: str = "data/city.txt",
        log_level: str = "INFO",
    ):
        """
        Инициализация объекта Settings и автоматическая загрузка настроек.

        Args:
            config_path (str): Путь к файлу настроек.
            rootFolder (str): Директория для поиска файлов.
            mainDataCSV (str): Путь к файлу базы данных точек.
            cityDataFile (str): Путь к файлу данных о городах.
            log_level (str): Уровень логирования.
        """
        self.config_path = config_path
        self._rootFolder = rootFolder
        self._mainDataCSV = mainDataCSV
        self._cityDataFile = cityDataFile
        self._log_level = log_level.upper()
        self.load()





    @property
    def log_level(self) -> str:
        """
        Уровень логирования (например, INFO, DEBUG, WARNING, ERROR).

        Returns:
            str: Текущий уровень логирования.
        """
        return self._log_level

    @log_level.setter
    def log_level(self, value: str) -> None:
        """
        Установить уровень логирования и сохранить настройки.

        Args:
            value (str): Новый уровень логирования.
        """
        self._log_level = value.upper()
        self.save()

    # __post_init__ больше не нужен


    @property
    def rootFolder(self) -> str:
        """
        Директория для поиска файлов для парсинга (абсолютный путь).
        При изменении автоматически сохраняет настройки.

        Returns:
            str: Абсолютный путь к директории.
        """
        return os.path.abspath(self._rootFolder)

    @rootFolder.setter
    def rootFolder(self, value: str) -> None:
        """
        Установить директорию для поиска файлов и сохранить настройки.

        Args:
            value (str): Новый путь к директории.
        """
        self._rootFolder = value
        self.save()


    @property
    def mainDataCSV(self) -> str:
        """
        Путь к файлу базы данных точек.
        При изменении автоматически сохраняет настройки.

        Returns:
            str: Путь к файлу базы данных точек.
        """
        return self._mainDataCSV

    @mainDataCSV.setter
    def mainDataCSV(self, value: str) -> None:
        """
        Установить путь к файлу базы данных точек и сохранить настройки.

        Args:
            value (str): Новый путь к файлу.
        """
        self._mainDataCSV = value
        self.save()


    @property
    def cityDataFile(self) -> str:
        """
        Путь к файлу данных о городах.
        При изменении автоматически сохраняет настройки.

        Returns:
            str: Путь к файлу данных о городах.
        """
        return self._cityDataFile

    @cityDataFile.setter
    def cityDataFile(self, value: str) -> None:
        """
        Установить путь к файлу данных о городах и сохранить настройки.

        Args:
            value (str): Новый путь к файлу.
        """
        self._cityDataFile = value
        self.save()


    @classmethod
    def create_default_file(cls, filepath: str) -> None:
        """
        Создать файл настроек с дефолтными значениями и комментариями.

        Args:
            filepath (str): Путь к файлу настроек.
        """
        logger.info("Создание файла настроек: %s", filepath)
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
        except Exception as e:
            logger.error("Ошибка при создании директории: %s", e)
            return
        lines = [
            "# ===============================================================================",
            "# Файл настроек для приложения PointsManager",
            "# Формат: <имя_параметра>=<значение> (без пробелов вокруг знака равно)",
            "# Все строки, начинающиеся с #, считаются комментариями и игнорируются.",
            "# Файл должен быть сохранён в кодировке UTF-8 для поддержки путей с русскими символами.",
            "# Если параметр не указан — используется значение по умолчанию.",
            "# ===============================================================================",
            "",
            "# === Пути к данным ===",
            "# rootFolder — директория для поиска файлов для парсинга (xml, json и т.д.)",
            "rootFolder=INPUT",
            "# mainDataCSV — файл (база данных) для хранения всех ранее отмеченных точек (CSV, UTF-8)",
            "mainDataCSV=data/AllPoint.csv",
            "# cityDataFile — файл для хранения данных о городах (txt, UTF-8)",
            "cityDataFile=data/city.txt",
            "",
            "# === Логирование ===",
            "# log_level — уровень логирования: DEBUG, INFO, WARNING, ERROR",
            "log_level=INFO",
        ]
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
        except Exception as e:
            logger.error("Ошибка при записи файла настроек: %s", e)
        else:
            logger.info("Файл настроек создан: %s", filepath)


    def load(self) -> None:
        """
        Загрузить настройки из файла. Если файл отсутствует или повреждён — создать дефолтный.
        """
        logger.info("Загрузка настроек из файла: %s", self.config_path)
        if not os.path.exists(self.config_path):
            logger.info("Файл настроек не найден: %s", self.config_path)
            self.create_default_file(self.config_path)
        values: Dict[str, str] = {}
        try:
            with open(self.config_path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" not in line:
                        logger.error("Ошибка формата строки: '%s'", line)
                        raise ValueError(f"Ошибка формата строки: '{line}'")
                    key, value = line.split("=", 1)
                    values[key.strip()] = value.strip()
        except Exception as e:
            logger.error("Ошибка при чтении файла настроек: %s", e)
            raise
        self._rootFolder = values.get("rootFolder", self._rootFolder)
        self._mainDataCSV = values.get("mainDataCSV", self._mainDataCSV)
        self._cityDataFile = values.get("cityDataFile", self._cityDataFile)
        self._log_level = values.get("log_level", self._log_level).upper()
        logger.info("Входная директория: %s", os.path.abspath(self._rootFolder))
        logger.info("Файл данных о городах: %s", self._cityDataFile)
        logger.info("Файл базы данных точек: %s", self._mainDataCSV)
        logger.info("Уровень логирования: %s", self._log_level)


    def validate(self) -> Dict[str, str]:
        """
        Проверить корректность настроек.

        Returns:
            Dict[str, str]: Словарь ошибок (пустой, если всё ок).
        """
        errors: Dict[str, str] = {}
        if not os.path.isdir(self.rootFolder):
            errors["rootFolder"] = f"Директория не найдена: {self.rootFolder}"
        main_csv_dir = os.path.dirname(self.mainDataCSV)
        if main_csv_dir and not os.path.isdir(main_csv_dir):
            errors["mainDataCSV"] = f"Директория для CSV не найдена: {main_csv_dir}"
        elif not os.path.exists(self.mainDataCSV):
            errors["mainDataCSV"] = f"Файл базы данных точек не найден: {self.mainDataCSV}"
        city_file_dir = os.path.dirname(self.cityDataFile)
        if city_file_dir and not os.path.isdir(city_file_dir):
            errors["cityDataFile"] = f"Директория для файла городов не найдена: {city_file_dir}"
        elif not os.path.exists(self.cityDataFile):
            errors["cityDataFile"] = f"Файл данных о городах не найден: {self.cityDataFile}"
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if self.log_level not in valid_levels:
            errors["log_level"] = f"Недопустимый уровень логирования: {self.log_level}"
        return errors


    def save(self) -> None:
        """
        Сохранить текущие настройки в файл.
        """
        self.save_to_file(self.config_path)


    def to_dict(self) -> Dict[str, Any]:
        """
        Конвертировать объект Settings в словарь.

        Returns:
            Dict[str, Any]: Словарь с настройками.
        """
        return {
            "rootFolder": self.rootFolder,
            "mainDataCSV": self.mainDataCSV,
            "cityDataFile": self.cityDataFile,
            "log_level": self.log_level,
        }


    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Settings":
        """
        Создать Settings из словаря.

        Args:
            d (Dict[str, Any]): Словарь с настройками.

        Returns:
            Settings: Новый объект Settings.
        """
        return cls(
            rootFolder=d.get("rootFolder", "INPUT"),
            mainDataCSV=d.get("mainDataCSV", "data/AllPoint.csv"),
            cityDataFile=d.get("cityDataFile", "data/city.txt"),
            log_level=d.get("log_level", "INFO"),
        )


    def save_to_file(self, filepath: str) -> None:
        """
        Сохранить настройки в указанный файл.

        Args:
            filepath (str): Путь к файлу настроек.
        """
        dirpath = os.path.dirname(filepath)
        if dirpath:
            try:
                os.makedirs(dirpath, exist_ok=True)
            except Exception as e:
                logger.error("Ошибка при создании директории: %s", e)
                return
        lines = [
            "# ===============================================================================",
            "# Файл настроек для приложения PointsManager",
            "# Формат: <имя_параметра>=<значение> (без пробелов вокруг знака равно)",
            "# Все строки, начинающиеся с #, считаются комментариями и игнорируются.",
            "# Файл должен быть сохранён в кодировке UTF-8 для поддержки путей с русскими символами.",
            "# Если параметр не указан — используется значение по умолчанию.",
            "# ===============================================================================",
            "",
            "# === Пути к данным ===",
            "# rootFolder — директория для поиска файлов для парсинга (xml, json и т.д.)",
            f"rootFolder={self._rootFolder}",
            "# mainDataCSV — файл (база данных) для хранения всех ранее отмеченных точек (CSV, UTF-8)",
            f"mainDataCSV={self.mainDataCSV}",
            "# cityDataFile — файл для хранения данных о городах (txt, UTF-8)",
            f"cityDataFile={self.cityDataFile}",
            "",
            "# === Логирование ===",
            "# log_level — уровень логирования: DEBUG, INFO, WARNING, ERROR",
            f"log_level={self.log_level}",
        ]
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
        except Exception as e:
            logger.error("Ошибка при сохранении файла настроек: %s", e)
            raise
