from models.city import CityRecord
from models.points import PointRecord


def test_point_record_creation():
    point = PointRecord(
        date="17.08.2025",
        time="12:00:00",
        latitude=55.75,
        longitude=37.62,
        x_sk42=None,
        y_sk42=None,
        country="RU",
        city="Москва",
        area_desc=None,
        region_desc=None,
        original_text="<xml></xml>",
        file_path="/tmp/test.xml"
    )
    assert point.date == "17.08.2025"
    assert point.city == "Москва"
    assert point.latitude == 55.75
    assert point.longitude == 37.62

def test_city_record_creation():
    city = CityRecord(
        name_original="Moscow",
        name_ru="Москва",
        latitude=55.75,
        longitude=37.62,
        country="RU",
        description="Столица",
        region="Москва"
    )
    assert city.name_ru == "Москва"
    assert city.latitude == 55.75
    assert city.country == "RU"
    assert city.country == "RU"
