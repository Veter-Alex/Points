import os
import tempfile

import pytest

from models.settings import Settings


def test_create_default_file_and_load():
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = os.path.join(tmpdir, "settings.txt")
        # Создание и автозагрузка
        s = Settings(config_path=config_path)
        assert os.path.exists(config_path)
        assert s.rootFolder == "INPUT"
        assert s.mainDataCSV == "data/AllPoint.csv"
        assert s.cityDataFile == "data/city.txt"


def test_save_and_reload():
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = os.path.join(tmpdir, "settings.txt")
        s = Settings(config_path=config_path)
        s.rootFolder = "DATA"
        s.mainDataCSV = "main.csv"
        s.cityDataFile = "cities.txt"
        # Проверяем автосохранение
        s2 = Settings(config_path=config_path)
        assert s2.rootFolder == "DATA"
        assert s2.mainDataCSV == "main.csv"
        assert s2.cityDataFile == "cities.txt"


def test_to_dict_and_from_dict():
    s = Settings()
    d = s.to_dict()
    s2 = Settings.from_dict(d)
    assert s2.rootFolder == s.rootFolder
    assert s2.mainDataCSV == s.mainDataCSV
    assert s2.cityDataFile == s.cityDataFile


def test_invalid_config_format():
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = os.path.join(tmpdir, "settings.txt")
        with open(config_path, "w", encoding="utf-8") as f:
            f.write("broken_line_without_equal\n")
        with pytest.raises(ValueError):
            Settings(config_path=config_path)


def test_save_to_file_and_load():
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = os.path.join(tmpdir, "settings.txt")
        s = Settings(config_path=config_path)
        s.rootFolder = "SAVED"
        s.save_to_file(config_path)
        s2 = Settings(config_path=config_path)
        assert s2.rootFolder == "SAVED"
        s2 = Settings(config_path=config_path)
        assert s2.rootFolder == "SAVED"
