#!/usr/bin/env python3
"""
Тестирование класса CityData с новым форматом city.txt (без зависимостей)
"""

import os
import sys
from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class CityRecord:
    name_original: str
    name_ru: str
    latitude: float
    longitude: float
    country: Optional[str] = None
    description: Optional[str] = None
    region: Optional[str] = None


class SimpleCityData:
    """Упрощенная версия CityData для тестирования без зависимостей"""

    def __init__(self, filepath: str):
        self.filepath = filepath
        self.records: List[CityRecord] = []
        self.load()

    def load(self):
        """Загружает данные из файла"""
        self.records = []

        try:
            with open(self.filepath, encoding="utf-8") as f:
                for i, line in enumerate(f, 1):
                    line = line.strip()
                    if not line or line.startswith("'") or "=" not in line:
                        continue
                    try:
                        record = self.parse_line(line)
                        if record:
                            self.records.append(record)
                    except Exception as e:
                        print(f"Ошибка парсинга строки {i}: {e}")
                        raise
        except Exception as e:
            print(f"Ошибка загрузки {self.filepath}: {e}")
            raise

    @staticmethod
    def parse_line(line: str) -> Optional[CityRecord]:
        """Парсинг строки в CityRecord"""
        try:
            name_original, rest = line.split("=", 1)
            parts = rest.split("_")

            if len(parts) < 4:
                raise ValueError(f"Недостаточно частей в строке: {line}")

            name_ru = parts[0]
            latitude = float(parts[1].replace(",", "."))
            longitude = float(parts[2].replace(",", "."))
            country = parts[3] if parts[3] else None

            description = parts[4] if len(parts) > 4 and parts[4] else None
            region = parts[5] if len(parts) > 5 and parts[5] else None

            if not all([name_original.strip(), name_ru.strip()]):
                raise ValueError("Обязательные поля пусты")

            return CityRecord(
                name_original=name_original.strip(),
                name_ru=name_ru.strip(),
                latitude=latitude,
                longitude=longitude,
                country=country.strip() if country else None,
                description=description.strip() if description else None,
                region=region.strip() if region else None,
            )
        except Exception as e:
            print(f"Ошибка парсинга строки: '{line}' Причина: {e}")
            raise

    @staticmethod
    def city_to_line(city: CityRecord) -> str:
        """Формирование строки из CityRecord"""

        def safe_value(value: Optional[str]) -> str:
            if not value:
                return ""
            return value.replace("_", "-").replace("=", "-")

        latitude_str = str(city.latitude)
        longitude_str = str(city.longitude)

        country = safe_value(city.country) if city.country else "Неизвестно"
        description = safe_value(city.description) if city.description else ""
        region = safe_value(city.region) if city.region else f"на территории {country}"

        return (
            f"{safe_value(city.name_original)}="
            f"{safe_value(city.name_ru)}_"
            f"{latitude_str}_"
            f"{longitude_str}_"
            f"{country}_"
            f"{description}_"
            f"{region}"
        )


def test_city_data_loading():
    """Тест загрузки данных из city.txt"""
    print("=" * 60)
    print("ТЕСТ ЗАГРУЗКИ ДАННЫХ ИЗ CITY.TXT")
    print("=" * 60)

    try:
        city_data = SimpleCityData("data/city.txt")
        print(f"✅ Загружено записей: {len(city_data.records)}")

        if not city_data.records:
            print("❌ Нет записей для анализа!")
            return False

        print("\n📋 АНАЛИЗ ПЕРВЫХ 5 ЗАПИСЕЙ:")
        print("-" * 60)

        for i, record in enumerate(city_data.records[:5]):
            print(f"\n{i+1}. Оригинальное название: '{record.name_original}'")
            print(f"   Русское название: '{record.name_ru}'")
            print(f"   Координаты: {record.latitude}, {record.longitude}")
            print(f"   Страна: '{record.country}'")
            print(
                f"   Описание: '{record.description}'"
                if record.description
                else "   Описание: (пусто)"
            )
            print(
                f"   Регион: '{record.region}'"
                if record.region
                else "   Регион: (пусто)"
            )

        return True

    except Exception as e:
        print(f"❌ Ошибка при загрузке: {e}")
        return False


def test_city_parsing():
    """Тест парсинга отдельных строк"""
    print("\n" + "=" * 60)
    print("ТЕСТ ПАРСИНГА СТРОК")
    print("=" * 60)

    test_lines = [
        "London=г.Лондон_51.505064_-0.126634_Англия__на территории Англии",
        "Kursk=г.Курск_51.730846_36.193015_Россия__на территории Курской области",
        "Alekseyevo-Druzhkovka=н.п.Алексеево-Дружковка_48.579088_37.611886_Россия_70 км сев.-зап. г.Донецк_на территории Донецкой области",
    ]

    for i, line in enumerate(test_lines, 1):
        try:
            record = SimpleCityData.parse_line(line)
            print(f"\n✅ Строка {i} успешно распарсена:")
            print(f"   Исходная строка: {line}")
            print(f"   Результат: {record.name_original} -> {record.name_ru}")
            print(f"   Координаты: ({record.latitude}, {record.longitude})")
            print(f"   Страна: {record.country}")
            print(f"   Описание: {record.description or '(пусто)'}")
            print(f"   Регион: {record.region or '(пусто)'}")
        except Exception as e:
            print(f"❌ Ошибка парсинга строки {i}: {e}")
            return False

    return True


def test_city_to_line():
    """Тест формирования строки из записи"""
    print("\n" + "=" * 60)
    print("ТЕСТ ФОРМИРОВАНИЯ СТРОК")
    print("=" * 60)

    test_records = [
        CityRecord(
            name_original="TestCity1",
            name_ru="г.Тестовый",
            latitude=55.7558,
            longitude=37.6176,
            country="Россия",
            description="",
            region="на территории Московской области",
        ),
        CityRecord(
            name_original="TestCity2",
            name_ru="н.п.Тестовое",
            latitude=50.4501,
            longitude=30.5234,
            country="Украина",
            description="25 км от центра",
            region="на территории Украины",
        ),
    ]

    for i, record in enumerate(test_records, 1):
        try:
            line = SimpleCityData.city_to_line(record)
            print(f"\n✅ Запись {i} успешно преобразована в строку:")
            print(f"   Исходная запись: {record.name_original} -> {record.name_ru}")
            print(f"   Результирующая строка: {line}")

            parsed_back = SimpleCityData.parse_line(line)
            if (
                parsed_back.name_original == record.name_original
                and parsed_back.name_ru == record.name_ru
            ):
                print("   ✅ Обратное преобразование успешно")
            else:
                print("   ❌ Ошибка обратного преобразования")
                return False

        except Exception as e:
            print(f"❌ Ошибка формирования строки для записи {i}: {e}")
            return False

    return True


def test_file_statistics():
    """Статистика по файлу"""
    print("\n" + "=" * 60)
    print("СТАТИСТИКА ПО ФАЙЛУ")
    print("=" * 60)

    try:
        city_data = SimpleCityData("data/city.txt")

        countries = {}
        records_with_description = 0
        records_with_region = 0

        for record in city_data.records:
            if record.country:
                countries[record.country] = countries.get(record.country, 0) + 1

            if record.description:
                records_with_description += 1
            if record.region:
                records_with_region += 1

        print(f"📊 Общее количество записей: {len(city_data.records)}")
        print(f"📊 Записей с описанием: {records_with_description}")
        print(f"📊 Записей с регионом: {records_with_region}")

        print(f"\n🌍 Распределение по странам (топ-10):")
        for country, count in sorted(
            countries.items(), key=lambda x: x[1], reverse=True
        )[:10]:
            print(f"   {country}: {count} записей")

        return True

    except Exception as e:
        print(f"❌ Ошибка при анализе статистики: {e}")
        return False


def main():
    """Основная функция тестирования"""
    print("🧪 ТЕСТИРОВАНИЕ НОВОГО ФОРМАТА CITY.TXT")
    print("📅 Дата:", "29.07.2025")
    print("📁 Файл:", "data/city.txt")

    if not os.path.exists("data/city.txt"):
        print("❌ Файл data/city.txt не найден!")
        return

    tests = [
        ("Загрузка данных", test_city_data_loading),
        ("Парсинг строк", test_city_parsing),
        ("Формирование строк", test_city_to_line),
        ("Статистика файла", test_file_statistics),
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\n🔄 Выполняется тест: {test_name}")
        result = test_func()
        results.append((test_name, result))

    print("\n" + "=" * 60)
    print("ИТОГОВЫЙ ОТЧЕТ")
    print("=" * 60)

    passed = 0
    for test_name, result in results:
        status = "✅ ПРОЙДЕН" if result else "❌ ПРОВАЛЕН"
        print(f"{status}: {test_name}")
        if result:
            passed += 1

    print(f"\n📈 Результат: {passed}/{len(tests)} тестов пройдено")

    if passed == len(tests):
        print("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ! Новый формат city.txt работает корректно.")
    else:
        print("⚠️  Обнаружены проблемы, требующие исправления.")


if __name__ == "__main__":
    main()
    main()
