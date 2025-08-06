
"""
Модуль geo_manager.py
=====================

Модуль предназначен для работы с географическими данными, включая:
- Определение страны по координатам (широта/долгота)
- Преобразование координат между системами WGS-84 и СК-42

Все функции снабжены подробными комментариями и докстрингами согласно лучшим практикам Python.
"""

import math
import os
from typing import Optional, Tuple

import geopandas as gpd  # type: ignore
from shapely.geometry import Point  # type: ignore

# Глобальный кэш для GeoDataFrame со странами мира
_WORLD_GDF: Optional[gpd.GeoDataFrame] = None




def get_country_by_lat_lon(lat: float, lon: float) -> Tuple[str, str]:
    """
    Определяет страну по координатам широта/долгота.

    Функция ищет страну, в которую попадает точка с заданными координатами.
    Сначала производится точная проверка попадания точки в геометрию страны,
    затем — по буферу вокруг точки, если точное совпадение не найдено.

    Args:
        lat (float): Широта точки (WGS-84).
        lon (float): Долгота точки (WGS-84).

    Returns:
        Tuple[str, str]: Кортеж (английское название, русское название страны).
    """
    global _WORLD_GDF
    if _WORLD_GDF is None:
        # Загружаем геоданные стран из geojson при первом вызове
        geojson_path = os.path.join(os.path.dirname(__file__), "countries.geojson")
        _WORLD_GDF = gpd.read_file(geojson_path)
    point = Point(lon, lat)
    # Ищем страну по точному попаданию точки в геометрию
    matches = _WORLD_GDF[_WORLD_GDF["geometry"].contains(point)]
    if not matches.empty:
        country_eng = matches.iloc[0]["name"]
    else:
        # Если точное попадание не найдено, ищем по буферу вокруг точки (0.02 градуса)
        buffer_matches = _WORLD_GDF[_WORLD_GDF["geometry"].intersects(point.buffer(0.02))]
        country_eng = buffer_matches.iloc[0]["name"] if not buffer_matches.empty else ""
    # Переводим название страны на русский язык (словарь переводов)
    # Словарь формируется на основе уникальных значений из поля "страна" файла city.txt
    country_translate = {
        "Russia": "России",
        "Ukraine": "Украины",
        "Belarus": "Белоруссии",
        "China": "Китая",
        "Turkey": "Турции",
        "Egypt": "Египта",
        "Romania": "Румынии",
        "Norway": "Норвегии",
        "England": "Англии",
        "UAE": "Объединённых Арабских Эмиратов",
        "Oman": "Омана",
        "Germany": "Германии",
        "Spain": "Испании",
        "Finland": "Финляндии",
        "USA": "США",
        "Algeria": "Алжира",
        "Kazakhstan": "Казахстана",
        "Armenia": "Армении",
        "France": "Франции",
        "Austria": "Австрии",
        "Scotland": "Шотландии",
        "Iran": "Ирана",
        "Japan": "Японии",
        "Malaysia": "Малайзии",
        "Poland": "Польши",
        "Italy": "Италии",
        "Greece": "Греции",
        "Cambodia": "Камбоджи",
        "Portugal": "Португалии",
        "Singapore": "Сингапура",
        "Yemen": "Йемена",
        "Syria": "Сирии",
        "Ghana": "Ганы",
        "Scotland": "Шотландии",
        "England": "Англии",
        "France": "Франции",
        "Austria": "Австрии",
        "Poland": "Польши",
        "Italy": "Италии",
        "Finland": "Финляндии",
        "Spain": "Испании",
        "Portugal": "Португалии",
        "Germany": "Германии",
        "Norway": "Норвегии",
        "Sweden": "Швеции",
        "Denmark": "Дании",
        "Netherlands": "Нидерландов",
        "Switzerland": "Швейцарии",
        "Ireland": "Ирландии",
        "Belgium": "Бельгии",
        "Czechia": "Чехии",
        "Slovakia": "Словакии",
        "Hungary": "Венгрии",
        "Bulgaria": "Болгарии",
        "Serbia": "Сербии",
        "Montenegro": "Черногории",
        "Croatia": "Хорватии",
        "Slovenia": "Словении",
        "Estonia": "Эстонии",
        "Latvia": "Латвии",
        "Lithuania": "Литвы",
        "Moldova": "Молдавии",
        "Georgia": "Грузии",
        "Azerbaijan": "Азербайджана",
        "Uzbekistan": "Узбекистана",
        "Kyrgyzstan": "Киргизии",
        "Tajikistan": "Таджикистана",
        "Turkmenistan": "Туркменистана",
        "Armenia": "Армении",
        "Kazakhstan": "Казахстана",
        "Australia": "Австралии",
        "New Zealand": "Новой Зеландии",
        "Canada": "Канады",
        "Mexico": "Мексики",
        "Brazil": "Бразилии",
        "Argentina": "Аргентины",
        "Chile": "Чили",
        "Peru": "Перу",
        "Colombia": "Колумбии",
        "Venezuela": "Венесуэлы",
        "Paraguay": "Парагвая",
        "Uruguay": "Уругвая",
        "Bolivia": "Боливии",
        "Ecuador": "Эквадора",
        "South Africa": "Южной Африки",
        "Morocco": "Марокко",
        "Tunisia": "Туниса",
        "Libya": "Ливии",
        "Sudan": "Судана",
        "Nigeria": "Нигерии",
        "Kenya": "Кении",
        "Ethiopia": "Эфиопии",
        "Somalia": "Сомали",
        "Angola": "Анголы",
        "Mozambique": "Мозамбика",
        "Madagascar": "Мадагаскара",
        "Cameroon": "Камеруна",
        "Gabon": "Габона",
        "Congo": "Конго",
        "Zambia": "Замбии",
        "Zimbabwe": "Зимбабве",
        "Botswana": "Ботсваны",
        "Namibia": "Намибии",
        "Gambia": "Гамбии",
        "Senegal": "Сенегала",
        "Guinea": "Гвинеи",
        "Mali": "Мали",
        "Burkina Faso": "Буркина-Фасо",
        "Ivory Coast": "Кот-д’Ивуара",
        "Ghana": "Ганы",
        "Togo": "Того",
        "Benin": "Бенина",
        "Sierra Leone": "Сьерра-Леоне",
        "Liberia": "Либерии",
        "Central African Republic": "Центральноафриканской Республики",
        "Chad": "Чада",
        "Niger": "Нигера",
        "Rwanda": "Руанды",
        "Burundi": "Бурунди",
        "Uganda": "Уганды",
        "Tanzania": "Танзании",
        "Malawi": "Малави",
        "Zaire": "Заира",
        "Seychelles": "Сейшел",
        "Mauritius": "Маврикия",
        "Comoros": "Коморских Островов",
        "Djibouti": "Джибути",
        "Eritrea": "Эритреи",
        "Guinea-Bissau": "Гвинеи-Бисау",
        "Cape Verde": "Кабо-Верде",
        "Sao Tome and Principe": "Сан-Томе и Принсипи",
        "Palestine": "Палестины",
        "Israel": "Израиля",
        "Lebanon": "Ливана",
        "Jordan": "Иордании",
        "Syria": "Сирии",
        "Iraq": "Ирака",
        "Saudi Arabia": "Саудовской Аравии",
        "Kuwait": "Кувейта",
        "Bahrain": "Бахрейна",
        "Qatar": "Катара",
        "United Arab Emirates": "Объединённых Арабских Эмиратов",
        "Oman": "Омана",
        "Yemen": "Йемена",
        "Afghanistan": "Афганистана",
        "Pakistan": "Пакистана",
        "India": "Индии",
        "Bangladesh": "Бангладеш",
        "Sri Lanka": "Шри-Ланки",
        "Nepal": "Непала",
        "Bhutan": "Бутана",
        "Maldives": "Мальдив",
        "Mongolia": "Монголии",
        "North Korea": "КНДР",
        "South Korea": "Республики Корея",
        "Japan": "Японии",
        "Taiwan": "Тайваня",
        "Hong Kong": "Гонконга",
        "Macau": "Макао",
        "Philippines": "Филиппин",
        "Vietnam": "Вьетнама",
        "Thailand": "Таиланда",
        "Myanmar": "Мьянмы",
        "Laos": "Лаоса",
        "Cambodia": "Камбоджи",
        "Malaysia": "Малайзии",
        "Singapore": "Сингапура",
        "Indonesia": "Индонезии",
        "Brunei": "Брунея",
        "East Timor": "Восточного Тимора",
        "Papua New Guinea": "Папуа — Новой Гвинеи",
        "Australia": "Австралии",
        "New Zealand": "Новой Зеландии",
        "Fiji": "Фиджи",
        "Samoa": "Самоа",
        "Tonga": "Тонга",
        "Vanuatu": "Вануату",
        "Solomon Islands": "Соломоновых Островов",
        "Micronesia": "Микронезии",
        "Palau": "Палау",
        "Marshall Islands": "Маршалловых Островов",
        "Kiribati": "Кирибати",
        "Nauru": "Науру",
        "Tuvalu": "Тувалу",
    }
    country_rus = country_translate.get(country_eng, country_eng)
    return country_eng, country_rus



def get_sk42_coordinates(
    lat: float, lon: float, log_message=None
) -> Tuple[Optional[int], Optional[int]]:
    """
    Преобразует координаты WGS-84 в систему координат СК-42 (Гаусса-Крюгера).

    Функция выполняет преобразование координат с помощью класса CoordinateTransformer.
    Если координаты вне зоны действия СК-42, возвращает (None, None) и пишет предупреждение в лог.
    В случае ошибки преобразования также возвращает (None, None) и пишет ошибку в лог.

    Args:
        lat (float): Широта в системе WGS-84.
        lon (float): Долгота в системе WGS-84.
        log_message (callable, optional): Функция для логирования сообщений (по желанию).

    Returns:
        Tuple[Optional[int], Optional[int]]: Кортеж (x_sk42, y_sk42) — координаты в СК-42, либо (None, None) при ошибке.
    """
    from src.coordinate_transformer import CoordinateTransformer

    # Проверяем, попадает ли долгота в диапазон действия СК-42 (18°–165°)
    if lon < 18 or lon > 165:
        if log_message:
            log_message(
                f"Координаты вне зоны действия СК-42: {lat}, {lon}",
                color="orange",
                logger_level="warning",
            )
        x_sk42, y_sk42 = None, None
    else:
        try:
            # Инициализируем трансформер для СК-42 (автоматический выбор зоны)
            transformer = CoordinateTransformer(
                system="SK42_GAUSS_KRUGER", zone="AUTO", log_message=log_message
            )
            x_sk42, y_sk42 = transformer.transform(lat, lon, to_wgs=False)
            # Проверяем результат на корректность (NaN, Inf)
            if x_sk42 is not None and (math.isinf(x_sk42) or math.isnan(x_sk42)):
                x_sk42 = None
            if y_sk42 is not None and (math.isinf(y_sk42) or math.isnan(y_sk42)):
                y_sk42 = None
        except Exception as e:
            if log_message:
                log_message(
                    f"Ошибка преобразования координат WGS84->СК-42: {e}",
                    color="red",
                    logger_level="error",
                )
            x_sk42, y_sk42 = None, None
    # Округляем координаты до целых, если они корректны
    x_sk42 = int(x_sk42) if x_sk42 is not None else None
    y_sk42 = int(y_sk42) if y_sk42 is not None else None
    return x_sk42, y_sk42
