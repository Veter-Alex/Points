import os
import tempfile

import pytest

from models.city import CityData, CityRecord

CITY_TEMPLATE = """
' ================== TEST ==================
TestCity=ТестовыйГород_55,7558_37,6173_RU_Описание_Регион
"""


def test_create_and_load_city_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        city_path = os.path.join(tmpdir, "city.txt")
        with open(city_path, "w", encoding="utf-8") as f:
            f.write(CITY_TEMPLATE)
        data = CityData(city_path)
        assert len(data.records) == 1
        rec = data.records[0]
        assert rec.name_original == "TestCity"
        assert rec.name_ru == "ТестовыйГород"
        assert rec.latitude == 55.7558
        assert rec.longitude == 37.6173
        assert rec.country == "RU"
        assert rec.description == "Описание"
        assert rec.region == "Регион"


def test_add_city_and_duplicate():
    with tempfile.TemporaryDirectory() as tmpdir:
        city_path = os.path.join(tmpdir, "city.txt")
        data = CityData(city_path)
        city = CityRecord(
            name_original="City1",
            name_ru="Город1",
            latitude=10.0,
            longitude=20.0,
            country="RU",
            description="desc",
            region="reg",
        )
        data.add_city(city)
        assert data.get_by_name("City1") is not None
        # Попытка добавить дубликат по name_original
        data.add_city(city)
        assert len([r for r in data.records if r.name_original == "City1"]) == 1


def test_get_by_country():
    with tempfile.TemporaryDirectory() as tmpdir:
        city_path = os.path.join(tmpdir, "city.txt")
        data = CityData(city_path)
        city1 = CityRecord("A", "A", 1, 2, "RU")
        city2 = CityRecord("B", "B", 3, 4, "KZ")
        data.add_city(city1)
        data.add_city(city2)
        assert len(data.get_by_country("RU")) == 1
        assert len(data.get_by_country("KZ")) == 1


def test_parse_line_invalid():
    # Недостаточно частей
    with pytest.raises(ValueError):
        CityData.parse_line("BadLine=OnlyOneField")
    # Пустые обязательные поля
    with pytest.raises(ValueError):
        CityData.parse_line("=__1_2_3")


def test_save_and_backup():
    with tempfile.TemporaryDirectory() as tmpdir:
        city_path = os.path.join(tmpdir, "city.txt")
        data = CityData(city_path)
        city = CityRecord("C", "C", 1, 2, "RU")
        data.add_city(city)
        data.save_data_to_file()
        # Проверяем, что файл создан
        assert os.path.exists(city_path)
        # Проверяем, что backup создаётся
        data.save_data_to_file()
        backup_dir = os.path.join(tmpdir, "backup")
        backups = [f for f in os.listdir(backup_dir) if f.endswith(".bak")]
        assert len(backups) >= 1
        backups = [f for f in os.listdir(backup_dir) if f.endswith(".bak")]
        assert len(backups) >= 1
