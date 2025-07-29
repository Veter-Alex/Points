#!/usr/bin/env python3
"""
Проверка определения страны для набора координат (WGS84)
"""

import os
import sys

sys.path.append(".")

from src.core import get_country_by_lat_lon


def parse_coord(val):
    # Заменяет запятую на точку и преобразует к float
    return float(str(val).replace(",", "."))


def test_bulk_country_detection():
    coordinates = [
        ("46,6019", "31,5514"),
        ("46,6049", "31,0477"),
        ("46,5755", "31,1642"),
        ("63,5899", "10,827"),
        ("1,3", "103,909"),
        ("1,3", "103,909"),
        ("36,593", "36,162"),
        ("27,235", "33,841"),
        ("24,567", "118,1"),
        ("1,33", "103,45"),
        ("24,567", "118,1"),
        ("27,633", "33,583"),
        ("44,817", "29,967"),
        ("24,567", "118,1"),
        ("24,567", "118,1"),
        ("44,817", "29,967"),
        ("27,235", "33,841"),
        ("27,235", "33,841"),
        ("36,593", "36,162"),
        ("36,593", "36,162"),
        ("24,567", "118,1"),
        ("24,567", "118,1"),
        ("24,567", "118,1"),
        ("1,3", "103,909"),
        ("60,2547", "19,1504"),
    ]

    print("Проверка определения страны для координат:")
    print("=" * 60)
    for lat_str, lon_str in coordinates:
        lat = parse_coord(lat_str)
        lon = parse_coord(lon_str)
        try:
            country_eng, country_rus = get_country_by_lat_lon(lat, lon)
            result = country_eng or "(не определено)"
            print(f"{lat},{lon}  ->  {result}")
        except Exception as e:
            print(f"{lat},{lon}  ->  Ошибка: {e}")


if __name__ == "__main__":
    test_bulk_country_detection()
