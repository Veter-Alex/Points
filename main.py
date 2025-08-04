"""
Главный модуль приложения для обработки точек из XML/JSON файлов.
"""

import os
from typing import NoReturn

from models.city import CityData
from models.points import PointsData
from models.settings import Settings
from src.core import find_and_parse_files
from src.logger import logger

# Загрузка настроек приложения
settings: Settings = Settings()

# Инициализация данных
city_data: CityData = CityData(settings.cityDataFile)
points_data: PointsData = PointsData(settings.mainDataCSV)


def main() -> None:
    """Основная функция приложения."""
    # Приложение запущено
    logger.info("Приложение запущено")
    logger.info("Лог выполнения программы будет сохранён в файл logs/app.log")

    # Проверка входной папки
    if not os.path.isdir(settings.rootFolder):
        logger.error(f"Входная папка не найдена: {settings.rootFolder}")
        # Завершаем работу приложения с ошибкой
        logger.error("Проверьте настройки приложения и попробуйте снова.")
        exit(1)  # Используем exit(1) вместо exit(0) для обозначения ошибки

    # Найти и обработать файлы в входной папке
    logger.info(f"Начинаю обработку файлов в папке: {settings.rootFolder}")
    find_and_parse_files(settings.rootFolder, city_data, points_data, settings)
    logger.info("Обработка файлов завершена")


if __name__ == "__main__":
    main()
