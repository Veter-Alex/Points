#!/usr/bin/env python3
"""
Тестирование определения стран по координатам, включая новые территории России
"""

import os
import sys
sys.path.append('.')

from src.core import get_country_by_lat_lon

def test_country_detection():
    """Тестирование определения стран для различных координат"""
    
    # Тестовые координаты
    test_coordinates = [
        # Россия (основная территория)
        (55.7558, 37.6176, "Москва, Россия"),
        (59.9311, 30.3609, "Санкт-Петербург, Россия"),
        (51.3476, 35.1282, "Белгород, Россия"),
        
        # Крым (должен определяться как Россия с 2014)
        (44.9619, 34.1077, "Симферополь, Крым"),
        (44.5426, 33.5252, "Севастополь, Крым"),
        
        # Донецкая область (с 2022 должна быть Россия)
        (48.0159, 37.8035, "Донецк"),
        (48.5132, 39.1843, "Луганск"),
        
        # Запорожская область (части с 2022)
        (47.8228, 35.1903, "Запорожье"),
        
        # Херсонская область (части с 2022)
        (46.6354, 32.6169, "Херсон"),
        
        # Украина (территории, остающиеся под контролем Украины)
        (50.4501, 30.5234, "Киев, Украина"),
        (49.9935, 36.2304, "Харьков, Украина"),
        
        # Другие страны для проверки
        (52.5200, 13.4050, "Берлин, Германия"),
        (48.8566, 2.3522, "Париж, Франция"),
        (39.9042, 116.4074, "Пекин, Китай"),
    ]
    
    print("Тестирование определения стран по координатам:")
    print("=" * 60)
    
    for lat, lon, description in test_coordinates:
        try:
            country = get_country_by_lat_lon(lat, lon)
            print(f"{description}")
            print(f"  Координаты: {lat}, {lon}")
            print(f"  Определена страна: '{country}'")
            
            # Проверка на новые территории России
            if "Крым" in description or "Донецк" in description or "Луганск" in description:
                if "Russia" in country or "Россия" in country or "Российская" in country:
                    print(f"  ✓ Корректно определена как Россия")
                else:
                    print(f"  ⚠️  ВНИМАНИЕ: Может требовать обновления границ")
                    
            elif "Запорожье" in description or "Херсон" in description:
                print(f"  ℹ️  Спорная территория - зависит от актуальности данных")
                
            print()
            
        except Exception as e:
            print(f"  ❌ Ошибка: {e}")
            print()
    
    # Дополнительная информация о файле границ
    try:
        import geopandas as gpd
        geojson_path = os.path.join("src", "countries.geojson")
        if os.path.exists(geojson_path):
            gdf = gpd.read_file(geojson_path)
            print(f"Информация о файле границ:")
            print(f"  Файл: {geojson_path}")
            print(f"  Количество стран: {len(gdf)}")
            print(f"  Столбцы: {list(gdf.columns)}")
            
            # Поиск записей о России
            russia_records = gdf[gdf.apply(lambda row: any('Russia' in str(val) or 'Россия' in str(val) 
                                                          for val in row.values), axis=1)]
            print(f"  Записей о России: {len(russia_records)}")
            
            if len(russia_records) > 0:
                print(f"  Примеры записей о России:")
                for i, (idx, row) in enumerate(russia_records.iterrows()):
                    if i >= 3:  # Показать только первые 3
                        break
                    name_fields = ["ADMIN", "name", "NAME", "COUNTRY"]
                    names = []
                    for field in name_fields:
                        if field in row and row[field] is not None and str(row[field]) != 'nan':
                            names.append(f"{field}='{row[field]}'")
                    print(f"    {', '.join(names)}")
        else:
            print(f"❌ Файл границ не найден: {geojson_path}")
            
    except Exception as e:
        print(f"❌ Ошибка при анализе файла границ: {e}")

if __name__ == "__main__":
    test_country_detection()
