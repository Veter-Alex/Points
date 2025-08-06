# PointsManager

**PointsManager** — это приложение для парсинга XML/JSON файлов.

## Основные возможности

- Графический интерфейс на базе CustomTkinter
- Парсинг XML и JOSN файлов.
- Сохранение списка всех ранее отмеченных точек с описанием.
- Формирование KML файлов для каждой отмеченной точки.
- Экспорт данных в Excel, Word.
- Поддержка работы с большими наборами точек
- Логирование событий в файл и GUI
- Сборка в один exe-файл для Windows

## Быстрый старт

1. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```
2. Запустите приложение:
   ```bash
   python main.py
   ```
3. Для Windows: используйте exe-файл из папки `dist` (PointsManager.exe)

## Сборка exe

Для сборки используйте PyInstaller и файл PointsManager.spec:

```bash
pyinstaller PointsManager.spec
```

## Структура проекта

- `main.py` — точка входа
- `src/` — бизнес-логика, обработка файлов, GUI
- `models/` — модели данных, логгер, настройки
- `data/` — файлы городов, резервные копии
- `requirements.txt` — зависимости
- `PointsManager.spec` — сборка exe

## Зависимости

- customtkinter
- pandas, openpyxl
- geopandas, shapely, pyproj, fiona, pyogrio
- python-docx
- loguru

## Особенности

- Автоматическое определение страны по координатам через countries.geojson
- Поддержка работы из exe-файла (PyInstaller, resource_path)
- Цветовое логирование: синий — info, желтый — warning, красный — error

## Лицензия

MIT
