import csv
from typing import Dict, List, Optional


class AllPointRecord:
    """
    Класс для хранения одной точки из базы AllPoint.csv
    """

    def __init__(self, data: Dict[str, str]):
        self.data = data

    @property
    def date(self) -> str:
        return self.data.get("Data", "")

    @property
    def time(self) -> str:
        return self.data.get("Time", "")

    @property
    def lat(self) -> str:
        return self.data.get("Lat_WGS84", "")

    @property
    def lon(self) -> str:
        return self.data.get("Lon_WGS84", "")

    @property
    def x(self) -> str:
        return self.data.get("X_SK-42_Gauss_Kruger", "")

    @property
    def y(self) -> str:
        return self.data.get("Y_SK-42_Gauss_Kruger", "")

    @property
    def city(self) -> str:
        return self.data.get("City_Value", "")

    @property
    def country(self) -> str:
        return self.data.get("Country_Value", "")

    @property
    def area_desc(self) -> str:
        return self.data.get("Description of the area", "")

    @property
    def region_desc(self) -> str:
        return self.data.get("Description of the region", "")

    @property
    def original_text(self) -> str:
        return self.data.get("Original text", "")


class AllPointsManager:
    def find_by_lon_lat(self, lon: str, lat: str) -> List[AllPointRecord]:
        """
        Поиск точек по паре долгота и широта (строгое сравнение строк)
        """
        return [rec for rec in self.records if rec.lon == lon and rec.lat == lat]

    """
    Класс для управления базой точек AllPoint.csv
    """

    def __init__(self, csv_path: str):
        self.csv_path = csv_path
        self.header = [
            "Data",
            "Time",
            "Lat_WGS84",
            "Lon_WGS84",
            "X_SK-42_Gauss_Kruger",
            "Y_SK-42_Gauss_Kruger",
            "City_Value",
            "Country_Value",
            "Description of the area",
            "Description of the region",
            "Original text",
        ]
        self.records: List[AllPointRecord] = []
        self._load()

    def _load(self):
        self.records.clear()
        try:
            with open(self.csv_path, encoding="utf-8", newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self.records.append(AllPointRecord(row))
        except FileNotFoundError:
            pass  # Файл может отсутствовать при первом запуске

    def save(self):
        with open(self.csv_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=self.header)
            writer.writeheader()
            for rec in self.records:
                writer.writerow(rec.data)

    def add_point(self, point: AllPointRecord):
        self.records.append(point)
        self.save()

    def get_all(self) -> List[AllPointRecord]:
        return list(self.records)

    def find_by_city(self, city: str) -> List[AllPointRecord]:
        return [rec for rec in self.records if rec.city == city]

    def find_by_date(self, date: str) -> List[AllPointRecord]:
        return [rec for rec in self.records if rec.date == date]

    def clear(self):
        self.records.clear()
        self.save()
