import os
import tempfile

from models.points import PointRecord
from src.parsers import DateTimeExtractor, JSONParser, XMLParser


def test_openweathermap_forecast_xml_parsing():
    xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
    <weatherdata>
        <location latitude="55.75" longitude="37.62">
            <name>Москва</name>
            <country>RU</country>
        </location>
    </weatherdata>'''
    with tempfile.NamedTemporaryFile(suffix='.xml', delete=False) as tmp:
        tmp.write(xml_content.encode('utf-8'))
        tmp.flush()
        parser = XMLParser(tmp.name)
        point = parser.parse()
        assert point is not None
        assert point.latitude == 55.75
        assert point.longitude == 37.62
        assert point.city == "Москва"
        assert point.country == "RU"
        # Дата/время из метаданных
        file_date, file_time = DateTimeExtractor.extract_from_file_metadata(tmp.name)
        assert point.date == file_date
        assert point.time == file_time
    os.remove(tmp.name)

def test_cityinfo_json_parsing():
    json_content = '{"city": "Москва", "country": "RU", "latitude": 55.75, "longitude": 37.62, "date": "2025-08-17", "time": "12:00:00"}'
    with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp:
        tmp.write(json_content.encode('utf-8'))
        tmp.flush()
        parser = JSONParser(tmp.name)
        point = parser.parse()
        assert point is not None
        assert point.latitude == 55.75
        assert point.longitude == 37.62
        assert point.city == "Москва"
        assert point.country == "RU"
        assert point.date == "17.08.2025"  # нормализация
        assert point.time == "12:00:00"
    os.remove(tmp.name)

def test_datetime_extractor_metadata():
    with tempfile.NamedTemporaryFile(suffix='.xml', delete=False) as tmp:
        tmp.write(b'<test></test>')
        tmp.flush()
        date, time = DateTimeExtractor.extract_from_file_metadata(tmp.name)
        assert date is not None
        assert time is not None
    os.remove(tmp.name)

    def test_worldweatheronline_json_parsing():
        json_content = '''{
            "data": {
                "nearest_area": [{
                    "latitude": "55.75",
                    "longitude": "37.62",
                    "areaName": [{"value": "Москва"}],
                    "country": [{"value": "RU"}]
                }],
                "time_zone": [{"localtime": "2025-08-17 12:00"}]
            }
        }'''
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp:
            tmp.write(json_content.encode('utf-8'))
            tmp.flush()
            parser = JSONParser(tmp.name)
            point = parser.parse()
            assert point is not None
            assert point.latitude == 55.75
            assert point.longitude == 37.62
            assert point.city == "Москва"
            assert point.country == "RU"
            assert point.date == "17.08.2025"
            assert point.time == "12:00:00"
        os.remove(tmp.name)

    def test_ipapi_json_parsing():
        json_content = '{"lat": 55.75, "lon": 37.62, "city": "Москва", "country": "RU", "current": {"dt": 1766011200}}'
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp:
            tmp.write(json_content.encode('utf-8'))
            tmp.flush()
            parser = JSONParser(tmp.name)
            point = parser.parse()
            assert point is not None
            assert point.latitude == 55.75
            assert point.longitude == 37.62
            assert point.city == "Москва"
            assert point.country == "RU"
            assert point.date is not None
            assert point.time is not None
        os.remove(tmp.name)

    def test_geoip_json_parsing():
        json_content = '{"latitude": 55.75, "longitude": 37.62, "city": "Москва", "countryName": "RU"}'
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp:
            tmp.write(json_content.encode('utf-8'))
            tmp.flush()
            parser = JSONParser(tmp.name)
            point = parser.parse()
            assert point is not None
            assert point.latitude == 55.75
            assert point.longitude == 37.62
            assert point.city == "Москва"
            assert point.country == "RU"
        os.remove(tmp.name)

    def test_openweathermap_json_parsing():
        json_content = '{"coord": {"lat": 55.75, "lon": 37.62}, "name": "Москва", "sys": {"country": "RU"}}'
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp:
            tmp.write(json_content.encode('utf-8'))
            tmp.flush()
            parser = JSONParser(tmp.name)
            point = parser.parse()
            assert point is not None
            assert point.latitude == 55.75
            assert point.longitude == 37.62
            assert point.city == "Москва"
            assert point.country == "RU"
        os.remove(tmp.name)

    def test_accuweather_json_parsing():
        json_content = '''{
            "GeoPosition": {"Latitude": 55.75, "Longitude": 37.62},
            "LocalizedName": "Москва",
            "Country": {"LocalizedName": "RU"}
        }'''
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp:
            tmp.write(json_content.encode('utf-8'))
            tmp.flush()
            parser = JSONParser(tmp.name)
            point = parser.parse()
            assert point is not None
            assert point.latitude == 55.75
            assert point.longitude == 37.62
            assert point.city == "Москва"
            assert point.country == "RU"
        os.remove(tmp.name)

    def test_point_xml_parsing():
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
        <root>
            <point>
                <latitude Value="55.75" />
                <longitude Value="37.62" />
                <datetime Value="2025-08-17 12:00:00" />
                <City Value="Москва" />
                <Country Value="RU" />
            </point>
        </root>'''
        with tempfile.NamedTemporaryFile(suffix='.xml', delete=False) as tmp:
            tmp.write(xml_content.encode('utf-8'))
            tmp.flush()
            parser = XMLParser(tmp.name)
            point = parser.parse()
            assert point is not None
            assert point.latitude == 55.75
            assert point.longitude == 37.62
            assert point.city == "Москва"
            assert point.country == "RU"
            assert point.date == "17.08.2025"
            assert point.time == "12:00:00"
        os.remove(tmp.name)

    def test_devexpert_xml_parsing():
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
        <root>
            <loc lat="55.75" lon="37.62" name="Москва" country="RU">
                <obs dt="2025-08-17T12:00:00" />
            </loc>
        </root>'''
        with tempfile.NamedTemporaryFile(suffix='.xml', delete=False) as tmp:
            tmp.write(xml_content.encode('utf-8'))
            tmp.flush()
            parser = XMLParser(tmp.name)
            point = parser.parse()
            assert point is not None
            assert point.latitude == 55.75
            assert point.longitude == 37.62
            assert point.city == "Москва"
            assert point.country == "RU"
            assert point.date == "17.08.2025"
            assert point.time == "12:00:00"
        os.remove(tmp.name)

    def test_openweathermap_current_xml_parsing():
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
        <current>
            <city name="Москва">
                <coord lat="55.75" lon="37.62" />
                <country>RU</country>
            </city>
            <lastupdate value="2025-08-17T12:00:00" />
        </current>'''
        with tempfile.NamedTemporaryFile(suffix='.xml', delete=False) as tmp:
            tmp.write(xml_content.encode('utf-8'))
            tmp.flush()
            parser = XMLParser(tmp.name)
            point = parser.parse()
            assert point is not None
            assert point.latitude == 55.75
            assert point.longitude == 37.62
            assert point.city == "Москва"
            assert point.country == "RU"
            assert point.date == "17.08.2025"
            assert point.time == "12:00:00"
        os.remove(tmp.name)
