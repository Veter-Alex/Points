import sys

import geopandas as gpd
from shapely.ops import unary_union

# Пути к файлам (можно заменить на свои)
COUNTRIES_PATH = "src/countries.geojson"
EXPORT_PATH = "src/export.geojson"
OUTPUT_PATH = "src/countries_updated.geojson"

# Ключи для поиска стран
RUSSIA_KEYS = {"name": "Russia", "ISO3166-1-Alpha-3": "RUS", "ISO3166-1-Alpha-2": "RU"}
UKRAINE_KEYS = {
    "name": "Ukraine",
    "ISO3166-1-Alpha-3": "UKR",
    "ISO3166-1-Alpha-2": "UA",
}


def find_country_idx(gdf, keys):
    for idx, row in gdf.iterrows():
        for k, v in keys.items():
            if k in row and row[k] == v:
                return idx
    return None


def main():
    # Загрузка стран
    countries = gpd.read_file(COUNTRIES_PATH)
    # Загрузка новых территорий
    new_areas = gpd.read_file(EXPORT_PATH)
    # Объединяем все новые территории в один MultiPolygon
    new_union = unary_union(new_areas.geometry)

    # Найти Россию и Украину
    idx_rus = find_country_idx(countries, RUSSIA_KEYS)
    idx_ukr = find_country_idx(countries, UKRAINE_KEYS)
    if idx_rus is None or idx_ukr is None:
        print("Не найдены Россия или Украина в countries.geojson")
        sys.exit(1)

    # Обновить геометрию России (union)
    countries.at[idx_rus, "geometry"] = countries.at[idx_rus, "geometry"].union(
        new_union
    )
    # Обновить геометрию Украины (difference)
    countries.at[idx_ukr, "geometry"] = countries.at[idx_ukr, "geometry"].difference(
        new_union
    )

    # Сохранить результат
    countries.to_file(OUTPUT_PATH, driver="GeoJSON")
    print(f"Готово! Сохранено в {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
