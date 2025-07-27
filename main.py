from models.city import CityData
from models.points import PointsData
from models.settings import Settings
from src.core import find_and_parse_files
from src.logger import logger

# Загрузка настроек приложения
settings = Settings()

# Инициализация данных
city_data = CityData(settings.cityDataFile)
points_data = PointsData(settings.mainDataCSV)


if __name__ == "__main__":
    # Приложение запущено
    logger.info("Приложение запущено")
    logger.info("Лог выполнения программы будет сохранён в файл logs/app.log")
    # Найти и обработать файлы в входной папке
    logger.info(f"Начинаю обработку файлов в папке: {settings.rootFolder}")
    find_and_parse_files(settings.rootFolder, city_data, points_data)
    logger.info("Обработка файлов завершена")
