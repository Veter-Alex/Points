from dataclasses import dataclass
from typing import Optional, Dict, Any
import os

@dataclass
class Settings:
    """
    Класс для хранения настроек приложения PointsManager.
    Автоматически загружает настройки при создании экземпляра.
    """
    config_path: str = "settings.txt"  # Путь к файлу конфигурации
    rootFolder: str = "INPUT"
    mainDataCSV: str = "data/AllPoint.csv"
    cityDataFile: str = "data/city.txt"

    def __post_init__(self):
        """Автоматическая загрузка настроек после инициализации"""
        self.load()

    @classmethod
    def create_default_file(cls, filepath: str) -> None:
        """Создать файл настроек с дефолтными значениями и комментариями."""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
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
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    def load(self) -> None:
        """Загрузить настройки из файла"""
        # Создать файл по умолчанию, если не существует
        if not os.path.exists(self.config_path):
            self.create_default_file(self.config_path)
        
        values = {}
        try:
            with open(self.config_path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    key, value = line.split("=", 1)
                    values[key.strip()] = value.strip()
        except FileNotFoundError:
            pass
        
        # Обновляем текущий экземпляр
        self.rootFolder = values.get("rootFolder", self.rootFolder)
        self.mainDataCSV = values.get("mainDataCSV", self.mainDataCSV)
        self.cityDataFile = values.get("cityDataFile", self.cityDataFile)

    def save(self) -> None:
        """Сохранить текущие настройки в файл"""
        self.save_to_file(self.config_path)

    def to_dict(self) -> Dict[str, Any]:
        """Конвертировать объект Settings в словарь"""
        return {
            "rootFolder": self.rootFolder,
            "mainDataCSV": self.mainDataCSV,
            "cityDataFile": self.cityDataFile,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Settings":
        """Создать Settings из словаря"""
        return cls(
            rootFolder=d.get("rootFolder", "INPUT"),
            mainDataCSV=d.get("mainDataCSV", "data/AllPoint.csv"),
            cityDataFile=d.get("cityDataFile", "data/city.txt"),
        )

    def save_to_file(self, filepath: str) -> None:
        """Сохранить настройки в указанный файл"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
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
            f"rootFolder={self.rootFolder}",
            "# mainDataCSV — файл (база данных) для хранения всех ранее отмеченных точек (CSV, UTF-8)",
            f"mainDataCSV={self.mainDataCSV}",
            "# cityDataFile — файл для хранения данных о городах (txt, UTF-8)",
            f"cityDataFile={self.cityDataFile}",
        ]
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))