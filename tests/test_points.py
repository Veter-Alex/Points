import csv
import os
import tempfile

import pytest

from models.points import PointRecord, PointsData


@pytest.fixture
def temp_csv_file():
    fd, path = tempfile.mkstemp(suffix=".csv")
    os.close(fd)
    yield path
    if os.path.exists(path):
        os.remove(path)
    backup_dir = os.path.join(os.path.dirname(path), "backup")
    if os.path.exists(backup_dir):
        for f in os.listdir(backup_dir):
            os.remove(os.path.join(backup_dir, f))
        os.rmdir(backup_dir)


def test_create_and_load_empty(temp_csv_file):
    data = PointsData(temp_csv_file)
    assert os.path.exists(temp_csv_file)
    assert data.points == []
    assert data.index == {}


def test_add_and_find_point(temp_csv_file):
    data = PointsData(temp_csv_file)
    point = PointRecord(
        date="2025-07-27",
        time="12:00",
        latitude=55.75,
        longitude=37.62,
        x_sk42=123456,
        y_sk42=654321,
        country="Россия",
        city="Москва",
        area_desc="центр",
        region_desc="Московская область",
        original_text="Москва, центр",
    )
    assert data.add_point(point) is True
    found = data.find_by_lat_lon(55.75, 37.62)
    assert found is not None
    assert found.city == "Москва"


def test_duplicate_by_coords_and_time(temp_csv_file):
    data = PointsData(temp_csv_file)
    p1 = PointRecord("2025-07-27", "12:00", 1.0, 2.0, 1, 2, "A", "B", None, None, "txt")
    p2 = PointRecord("2025-07-27", "12:00", 1.0, 2.0, 1, 2, "A", "B", None, None, "txt")
    assert data.add_point(p1) is True
    assert data.add_point(p2) is False


def test_duplicate_only_coords(temp_csv_file):
    data = PointsData(temp_csv_file)
    p1 = PointRecord("2025-07-27", "12:00", 1.0, 2.0, 1, 2, "A", "B", None, None, "txt")
    p2 = PointRecord("2025-07-27", "13:00", 1.0, 2.0, 1, 2, "A", "B", None, None, "txt")
    assert data.add_point(p1) is True
    assert data.add_point(p2) is True  # now allowed, time is different


def test_save_and_load(temp_csv_file):
    data = PointsData(temp_csv_file)
    point = PointRecord(
        "2025-07-27", "12:00", 1.0, 2.0, 1, 2, "A", "B", "desc", "reg", "txt"
    )
    data.add_point(point)
    data.save()
    # reload
    data2 = PointsData(temp_csv_file)
    assert len(data2.points) == 1
    p = data2.points[0]
    assert p.latitude == 1.0
    assert p.longitude == 2.0
    assert p.x_sk42 == 1
    assert p.y_sk42 == 2
    assert p.area_desc == "desc"
    assert p.region_desc == "reg"
    assert p.original_text == "txt"


def test_backup_created(temp_csv_file):
    data = PointsData(temp_csv_file)
    point = PointRecord(
        "2025-07-27", "12:00", 1.0, 2.0, 1, 2, "A", "B", None, None, "txt"
    )
    data.add_point(point)
    data.save()
    backup_dir = os.path.join(os.path.dirname(temp_csv_file), "backup")
    backups = [f for f in os.listdir(backup_dir) if f.endswith(".bak")]
    assert len(backups) >= 1


def test_x_sk42_y_sk42_none_on_invalid(temp_csv_file):
    # вручную пишем строку с невалидными x_sk42/y_sk42
    with open(temp_csv_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=PointsData.FIELD_NAMES)
        writer.writeheader()
        writer.writerow(
            {
                "Data": "2025-07-27",
                "Time": "12:00",
                "Lat_WGS84": "1.0",
                "Lon_WGS84": "2.0",
                "X_SK-42_Gauss_Kruger": "notanumber",
                "Y_SK-42_Gauss_Kruger": "",
                "Country_Value": "A",
                "City_Value": "B",
                "Description of the area": "",
                "Description of the region": "",
                "Original text": "txt",
            }
        )
    data = PointsData(temp_csv_file)
    assert len(data.points) == 1
    p = data.points[0]
    assert p.x_sk42 is None
    assert p.y_sk42 is None
    p = data.points[0]
    assert p.x_sk42 is None
    assert p.y_sk42 is None
