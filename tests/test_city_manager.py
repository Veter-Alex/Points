import os
import tempfile

import pytest

from src.city_manager import CityManager, CityRecord

CITY_TXT_CONTENT = """
London=г.Лондон_51,505064_-0,126634_Англия__на территории Англии
Москва=г.Москва_55,754057_37,623898_Россия__на территории России
# Комментарий
' Ещё комментарий
Paris=г.Париж_48,8566_2,3522_Франция__на территории Франции
"""


def create_temp_city_file(content: str) -> str:
    fd, path = tempfile.mkstemp(suffix=".txt")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(content)
    return path


def test_load_and_search_by_eng():
    path = create_temp_city_file(CITY_TXT_CONTENT)
    mgr = CityManager(path)
    rec = mgr.find_by_eng("London")
    assert rec is not None
    assert rec.orig_name == "London"
    assert rec.country == "Англия"
    os.remove(path)


def test_load_and_search_by_rus():
    path = create_temp_city_file(CITY_TXT_CONTENT)
    mgr = CityManager(path)
    rec = mgr.find_by_rus("Лондон")
    assert rec is not None
    assert rec.orig_name == "London"
    os.remove(path)


def test_search_universal():
    path = create_temp_city_file(CITY_TXT_CONTENT)
    mgr = CityManager(path)
    assert mgr.search("Москва").country == "Россия"
    assert mgr.search("г.Москва").country == "Россия"
    assert mgr.search("Paris").country == "Франция"
    assert mgr.search("Париж").country == "Франция"
    os.remove(path)


def test_all_cities():
    path = create_temp_city_file(CITY_TXT_CONTENT)
    mgr = CityManager(path)
    all_cities = mgr.all_cities()
    assert len(all_cities) == 3
    names = {c.orig_name for c in all_cities}
    assert "London" in names and "Москва" in names and "Paris" in names
    os.remove(path)


def test_ignore_comments_and_headers():
    content = """
# comment
' comment
================== АНГЛИЯ ==================
London=г.Лондон_51,505064_-0,126634_Англия__
"""
    path = create_temp_city_file(content)
    mgr = CityManager(path)
    assert mgr.find_by_eng("London") is not None
    os.remove(path)


def test_parse_float():
    path = create_temp_city_file("London=г.Лондон_51,505064_-0,126634_Англия__\n")
    mgr = CityManager(path)
    rec = mgr.find_by_eng("London")
    assert isinstance(rec.latitude, float)
    assert abs(rec.latitude - 51.505064) < 1e-6
    os.remove(path)
