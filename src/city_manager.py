import re
from typing import Any, Dict, List, Optional


class CityRecord:
    def __init__(
        self,
        orig_name: str,
        type_and_rus: str,
        latitude: float,
        longitude: float,
        country: str,
        description: str = "",
        region: str = "",
    ):
        self.orig_name = orig_name
        self.type_and_rus = type_and_rus
        self.latitude = latitude
        self.longitude = longitude
        self.country = country
        self.description = description
        self.region = region

    def to_dict(self) -> Dict[str, Any]:
        return {
            "orig_name": self.orig_name,
            "type_and_rus": self.type_and_rus,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "country": self.country,
            "description": self.description,
            "region": self.region,
        }


class CityManager:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.cities: Dict[str, CityRecord] = {}
        self._rus_name_map: Dict[str, str] = {}
        self.load()

    def load(self) -> None:
        self.cities.clear()
        self._rus_name_map.clear()
        with open(self.filepath, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("'") or line.startswith("="):
                    continue
                if re.match(r"^=+ ", line):
                    continue  # country section header
                if "=" not in line:
                    continue
                orig_name, rest = line.split("=", 1)
                parts = rest.split("_")
                # Format: <тип_Русское_название>_<широта>_<долгота>_<страна>_[описание]_<регион>
                if len(parts) < 5:
                    continue  # invalid line
                type_and_rus = parts[0]
                latitude = self._parse_float(parts[1])
                longitude = self._parse_float(parts[2])
                country = parts[3]
                description = parts[4] if len(parts) > 4 else ""
                region = parts[5] if len(parts) > 5 else ""
                record = CityRecord(
                    orig_name=orig_name,
                    type_and_rus=type_and_rus,
                    latitude=latitude,
                    longitude=longitude,
                    country=country,
                    description=description,
                    region=region,
                )
                self.cities[orig_name] = record
                # Русское название для поиска
                rus_name = self._extract_rus_name(type_and_rus)
                if rus_name:
                    self._rus_name_map[rus_name] = orig_name

    def _parse_float(self, s: str) -> float:
        s = s.replace(",", ".")
        try:
            return float(s)
        except Exception:
            return 0.0

    def _extract_rus_name(self, type_and_rus: str) -> Optional[str]:
        # тип.Русское_название или г.Белгород, н.п.Аннаба и т.д.
        if "." in type_and_rus:
            return type_and_rus.split(".", 1)[1]
        return type_and_rus

    def find_by_eng(self, orig_name: str) -> Optional[CityRecord]:
        return self.cities.get(orig_name)

    def find_by_rus(self, rus_name: str) -> Optional[CityRecord]:
        eng = self._rus_name_map.get(rus_name)
        if eng:
            return self.cities.get(eng)
        return None

    def search(self, name: str) -> Optional[CityRecord]:
        # Поиск по английскому или русскому названию, с обработкой префикса "г." и "г "
        clean_name = name.strip()
        if clean_name.lower().startswith("г."):
            clean_name = clean_name[2:].lstrip()
        elif clean_name.lower().startswith("г "):
            clean_name = clean_name[2:].lstrip()
        rec = self.find_by_eng(clean_name)
        if rec:
            return rec
        return self.find_by_rus(clean_name)

    def all_cities(self) -> List[CityRecord]:
        return list(self.cities.values())
