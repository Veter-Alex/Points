import os
import tempfile
import shutil
import pytest
from models.city import CityData, CityRecord
from models.city_template import CITY_TXT_TEMPLATE

def test_create_file_if_not_exists(tmp_path):
    city_file = tmp_path / "city.txt"
    city_data = CityData(str(city_file))
    city_data.create_file_if_not_exists()
    assert city_file.exists()
    with open(city_file, encoding="utf-8") as f:
        content = f.read()
    assert content == CITY_TXT_TEMPLATE

def test_load_and_parse_line(tmp_path):
    city_file = tmp_path / "city.txt"
    content = "London=г.Лондон_51,505064_-0,126634_Англия__на территории Англии\n"
    city_file.write_text(content, encoding="utf-8")
    city_data = CityData(str(city_file))
    city_data.load()
    assert len(city_data.records) == 1
    rec = city_data.records[0]
    assert rec.name_original == "London"
    assert rec.name_ru == "г.Лондон"
    assert rec.latitude == 51.505064
    assert rec.longitude == -0.126634
    assert rec.country == "Англия"
    assert rec.region == "на территории Англии"

def test_add_city_creates_block_and_inserts_alphabetically(tmp_path):
    city_file = tmp_path / "city.txt"
    city_file.write_text("", encoding="utf-8")
    city_data = CityData(str(city_file))
    city1 = CityRecord(
        name_original="Berlin",
        name_ru="г.Берлин",
        latitude=52.52,
        longitude=13.405,
        country="Германия",
        description="",
        region="на территории Германии"
    )
    city2 = CityRecord(
        name_original="Aachen",
        name_ru="г.Аахен",
        latitude=50.775,
        longitude=6.083,
        country="Германия",
        description="",
        region="на территории Германии"
    )
    city_data.add_city(city1)
    city_data.add_city(city2)
    with open(city_file, encoding="utf-8") as f:
        lines = f.readlines()
    # Проверяем, что блок создан и города по алфавиту
    block_lines = [l for l in lines if not l.startswith("'") and l.strip()]
    assert block_lines[0].startswith("Aachen=")
    assert block_lines[1].startswith("Berlin=")

def test_get_by_country_and_get_by_name(tmp_path):
    city_file = tmp_path / "city.txt"
    content = (
        "London=г.Лондон_51,505064_-0,126634_Англия__на территории Англии\n"
        "Berlin=г.Берлин_52,52_13,405_Германия__на территории Германии\n"
    )
    city_file.write_text(content, encoding="utf-8")
    city_data = CityData(str(city_file))
    city_data.load()
    by_country = city_data.get_by_country("Германия")
    assert len(by_country) == 1
    assert by_country[0].name_original == "Berlin"
    by_name = city_data.get_by_name("г.Лондон")
    assert by_name is not None
    assert by_name.name_original == "London"

def test_backup_created_and_limited(tmp_path):
    city_file = tmp_path / "city.txt"
    city_file.write_text("London=г.Лондон_51,505064_-0,126634_Англия__на территории Англии\n", encoding="utf-8")
    city_data = CityData(str(city_file))
    # Многократно вызываем add_city, чтобы создать бэкапы
    for i in range(12):
        city = CityRecord(
            name_original=f"Test{i}",
            name_ru=f"Тест{i}",
            latitude=50.0 + i,
            longitude=36.0 + i,
            country="Тестовая страна",
            description="",
            region="регион"
        )
        city_data.add_city(city)
    backup_dir = tmp_path / "backup"
    backups = [f for f in os.listdir(backup_dir) if f.startswith("city.txt") and f.endswith(".bak")]
    assert len(backups) <= 10
