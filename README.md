# PointsManager

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![GUI](https://img.shields.io/badge/GUI-CustomTkinter-green)

Приложение для управления и анализа точек на карте с удобным графическим интерфейсом.

## Возможности
- Поиск, добавление и редактирование городов
- Импорт и экспорт данных (CSV, TXT)
- Работа с большими наборами точек
- Гибкие настройки через `settings.txt`
- Поддержка пользовательских путей к данным
- Совместимость с Windows

## Структура проекта
```
Points/
├── main.py                # Главный файл приложения (GUI)
├── src/
│   ├── city_manager.py    # Логика работы с городами
│   └── settings_manager.py# Работа с настройками
├── data/
│   ├── AllPoint.csv       # Основная база точек
│   └── city.txt           # Данные о городах
├── settings.txt           # Конфигурация приложения
├── tests/                 # Тесты
├── .gitignore             # Исключения для git
└── README.md              # Описание проекта
```

## Быстрый старт
1. Клонируйте репозиторий:
   ```sh
   git clone https://github.com/Veter-Alex/Points.git
   cd Points
   ```
2. Установите зависимости (если есть):
   ```sh
   pip install -r requirements.txt
   ```
3. Запустите приложение:
   ```sh
   python main.py
   ```

## Настройки
Все параметры настраиваются в файле `settings.txt`:
- `rootFolder` — директория для поиска файлов
- `mainDataCSV` — путь к базе точек
- `cityDataFile` — путь к файлу городов

## Тестирование
Тесты находятся в папке `tests/`:
```sh
python -m unittest discover tests
```

## Контакты
Автор: Alex Wind
Email: vet-an@yandex.ru

---

> Проект находится в активной разработке. Будем рады вашим предложениям и pull request!
