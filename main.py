from src.logger import logger
from models.settings import Settings
from models.city import CityData
from models.points import PointsData
# Загрузка настроек приложения
settings = Settings()

# Инициализация данных
city_data = CityData(settings.cityDataFile)
points_data = PointsData(settings.mainDataCSV)


if __name__ == "__main__":
    # Приложение запущено
    logger.info("Приложение запущено")
    logger.info("Лог выполнения программы будет сохранён в файл logs/app.log")

