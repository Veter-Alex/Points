import os
from typing import Any, Dict, Optional


class SettingsManager:
    # Шаблон настроек с подробными комментариями и порядком
    SETTINGS_TEMPLATE = [
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
        "rootFolder=E:\\Programming\\Projects\\Python\\weather\\INPUT",
        "# mainDataCSV — файл (база данных) для хранения всех ранее отмеченных точек (CSV, UTF-8)",
        "mainDataCSV=E:\\Programming\\Projects\\Python\\weather\\settings\\AllPoint.csv",
        "# cityDataFile — файл для хранения данных о городах (txt, UTF-8)",
        "cityDataFile=E:\\Programming\\Projects\\Python\\weather\\data\\city.txt",
    ]

    def __init__(self, filepath: str = "settings.txt"):
        self.filepath = filepath
        self.settings: Dict[str, Any] = {}
        self.load()

    def load(self) -> None:
        """Загрузить настройки из файла."""
        self.settings.clear()
        if not os.path.exists(self.filepath):
            return
        with open(self.filepath, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                self.settings[key.strip()] = self._parse_value(value.strip())

    def save(self) -> None:
        """Сохранить текущие настройки в файл с подробными комментариями и структурой."""
        template_lines = self.SETTINGS_TEMPLATE.copy()
        # Сопоставим ключи из шаблона с текущими значениями
        result_lines = []
        for line in template_lines:
            if line.strip().startswith("#") or "=" not in line:
                result_lines.append(line)
                continue
            key, _ = line.split("=", 1)
            key = key.strip()
            value = self.settings.get(key, "")
            result_lines.append(f"{key}={self._serialize_value(value)}")
        with open(self.filepath, "w", encoding="utf-8") as f:
            for line in result_lines:
                f.write(line.rstrip("\n") + "\n")

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        return self.settings.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self.settings[key] = value

    def _parse_value(self, value: str) -> Any:
        # Попытка привести к bool, int, float, иначе оставить строкой
        if value.lower() in ("true", "false"):
            return value.lower() == "true"
        try:
            return int(value)
        except ValueError:
            pass
        try:
            return float(value)
        except ValueError:
            pass
        return value

    def _serialize_value(self, value: Any) -> str:
        if isinstance(value, bool):
            return "True" if value else "False"
        return str(value)
