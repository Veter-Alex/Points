import os
import shutil
import tempfile
from typing import Tuple

import pytest

from src.settings_manager import SettingsManager


def make_settings_file(content: str) -> Tuple[str, str]:
    temp_dir: str = tempfile.mkdtemp()
    file_path: str = os.path.join(temp_dir, "settings.txt")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    return file_path, temp_dir


def test_load_and_get() -> None:
    content = """
# === Пути к данным ===
rootFolder=/tmp/input
mainDataCSV=/tmp/data.csv
cityDataFile=/tmp/city.txt
"""
    file_path, temp_dir = make_settings_file(content)
    try:
        sm: SettingsManager = SettingsManager(file_path)
        assert sm.get("rootFolder") == "/tmp/input"
        assert sm.get("mainDataCSV") == "/tmp/data.csv"
        assert sm.get("cityDataFile") == "/tmp/city.txt"
        assert sm.get("not_exist", 123) == 123
    finally:
        shutil.rmtree(temp_dir)


def test_set_and_save() -> None:
    content = """
# === Пути к данным ===
rootFolder=/tmp/input
mainDataCSV=/tmp/data.csv
cityDataFile=/tmp/city.txt
"""
    file_path, temp_dir = make_settings_file(content)
    try:
        sm: SettingsManager = SettingsManager(file_path)
        sm.set("rootFolder", "/new/input")
        sm.set("mainDataCSV", "/new/data.csv")
        sm.save()
        # Проверяем, что файл обновился
        with open(file_path, encoding="utf-8") as f:
            saved: str = f.read()
        assert "/new/input" in saved
        assert "/new/data.csv" in saved
    finally:
        shutil.rmtree(temp_dir)


def test_save_preserves_comments() -> None:
    content = """
# === Пути к данным ===
# rootFolder — директория
rootFolder=/tmp/input
# mainDataCSV — файл
mainDataCSV=/tmp/data.csv
# cityDataFile — файл
cityDataFile=/tmp/city.txt
"""
    file_path, temp_dir = make_settings_file(content)
    try:
        sm: SettingsManager = SettingsManager(file_path)
        sm.set("rootFolder", "/abc")
        sm.save()
        with open(file_path, encoding="utf-8") as f:
            lines: list[str] = f.readlines()
        # Комментарии должны сохраниться
        assert any("директория" in l for l in lines)
        assert any("файл" in l for l in lines)
    finally:
        shutil.rmtree(temp_dir)
