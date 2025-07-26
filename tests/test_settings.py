import os
import tempfile
import shutil
from models.settings import Settings

def test_settings_defaults():
    s = Settings()
    assert s.rootFolder == "INPUT"
    assert s.mainDataCSV == "data/AllPoint.csv"
    assert s.cityDataFile == "data/city.txt"

def test_settings_from_dict():
    d = {"rootFolder": "DATA", "mainDataCSV": "points.csv", "cityDataFile": "cities.txt"}
    s = Settings.from_dict(d)
    assert s.rootFolder == "DATA"
    assert s.mainDataCSV == "points.csv"
    assert s.cityDataFile == "cities.txt"

def test_settings_to_dict():
    s = Settings(rootFolder="A", mainDataCSV="B", cityDataFile="C")
    d = s.to_dict()
    assert d["rootFolder"] == "A"
    assert d["mainDataCSV"] == "B"
    assert d["cityDataFile"] == "C"

def test_settings_save_and_load():
    s = Settings(rootFolder="FOLDER", mainDataCSV="file.csv", cityDataFile="city.txt")
    tmpdir = tempfile.mkdtemp()
    try:
        path = os.path.join(tmpdir, "settings.txt")
        s.save_to_file(path)
        loaded = Settings.load_from_file(path)
        assert loaded.rootFolder == "FOLDER"
        assert loaded.mainDataCSV == "file.csv"
        assert loaded.cityDataFile == "city.txt"
    finally:
        shutil.rmtree(tmpdir)
