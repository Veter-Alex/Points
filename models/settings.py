import os
from dataclasses import dataclass
from typing import Any, Dict, Optional

from src.logger import logger


class Settings:
    """
    Класс для хранения настроек приложения PointsManager.
    Автоматически загружает настройки при создании экземпляра.
    """

    def __init__(
        self,
        config_path: str = "settings.txt",
        rootFolder: str = "INPUT",
        mainDataCSV: str = "data/AllPoint.csv",
        cityDataFile: str = "data/city.txt",
    ):
        self.config_path = config_path
        self._rootFolder = rootFolder
        self._mainDataCSV = mainDataCSV
        self._cityDataFile = cityDataFile
        self.load()

    # __post_init__ больше не нужен

    @property
    def rootFolder(self) -> str:
        """
        Директория для поиска файлов для парсинга (абсолютный путь).
        При изменении автоматически сохраняет настройки.
        """
        # Возвращаем абсолютный путь
        return os.path.abspath(self._rootFolder)

    @rootFolder.setter
    def rootFolder(self, value: str) -> None:
        # Сохраняем как есть (относительный или абсолютный)
        self._rootFolder = value
        self.save()

    @property
    def mainDataCSV(self) -> str:
        """
        Путь к файлу базы данных точек.
        При изменении автоматически сохраняет настройки.
        """
        return self._mainDataCSV

    @mainDataCSV.setter
    def mainDataCSV(self, value: str) -> None:
        self._mainDataCSV = value
        self.save()

    @property
    def cityDataFile(self) -> str:
        """
        Путь к файлу данных о городах.
        При изменении автоматически сохраняет настройки.
        """
        return self._cityDataFile

    @cityDataFile.setter
    def cityDataFile(self, value: str) -> None:
        self._cityDataFile = value
        self.save()

    @classmethod
    def create_default_file(cls, filepath: str) -> None:
        """
        Создать файл настроек с дефолтными значениями и комментариями.
        """
        logger.info(
            "Создание файла настроек с дефолтными значениями и комментариями: {}",
            filepath,
        )

        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
        except Exception as e:
            logger.error("Ошибка при создании директории для файла настроек: {}", e)
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
        ]
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
        except Exception as e:
            logger.error("Ошибка при записи файла настроек: {}", e)
        else:
            logger.info("Файл настроек создан: {}", filepath)

    def load(self) -> None:
        """
        Загрузить настройки из файла. Если файл повреждён или содержит ошибку формата — логировать и выбрасывать исключение.
        """
        logger.info("Загрузка настроек из файла: {}", self.config_path)

        # Создать файл по умолчанию, если не существует
        if not os.path.exists(self.config_path):
            logger.info("Файл настроек не найден: {}", self.config_path)
            self.create_default_file(self.config_path)

        values = {}
        try:
            with open(self.config_path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" not in line:
                        logger.error(
                            f"Ошибка формата строки в файле настроек: '{line}'"
                        )
                        raise ValueError(
                            f"Ошибка формата строки в файле настроек: '{line}'"
                        )
                    key, value = line.split("=", 1)
                    values[key.strip()] = value.strip()
        except Exception as e:
            logger.error(f"Ошибка при чтении файла настроек: {e}")
            raise

        # Обновляем текущий экземпляр (без автосохранения)
        # Сохраняем как есть (относительный или абсолютный путь)
        self._rootFolder = values.get("rootFolder", self._rootFolder)
        self._mainDataCSV = values.get("mainDataCSV", self._mainDataCSV)
        self._cityDataFile = values.get("cityDataFile", self._cityDataFile)

        logger.info("Входная директория: {}", os.path.abspath(self._rootFolder))
        logger.info("Файл данных о городах: {}", self._cityDataFile)
        logger.info("Файл базы данных точек: {}", self._mainDataCSV)

    def save(self) -> None:
        """
        Сохранить текущие настройки в файл.
        """
        self.save_to_file(self.config_path)

    def to_dict(self) -> Dict[str, Any]:
        """
        Конвертировать объект Settings в словарь.
        """
        return {
            "rootFolder": self.rootFolder,
            "mainDataCSV": self.mainDataCSV,
            "cityDataFile": self.cityDataFile,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Settings":
        """
        Создать Settings из словаря.
        """
        return cls(
            rootFolder=d.get("rootFolder", "INPUT"),
            mainDataCSV=d.get("mainDataCSV", "data/AllPoint.csv"),
            cityDataFile=d.get("cityDataFile", "data/city.txt"),
        )

    def save_to_file(self, filepath: str) -> None:
        """
        Сохранить настройки в указанный файл.
        """
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
        except Exception as e:
            logger.error("Ошибка при создании директории для файла настроек: {}", e)
            return

        # Сохраняем rootFolder в том виде, как он был указан пользователем (относительный/абсолютный)
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
        ]
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
        except Exception as e:
            logger.error(f"Ошибка при сохранении файла настроек: {e}")
            raise
