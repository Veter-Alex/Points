"""
Главный модуль приложения для обработки точек из XML/JSON файлов.
"""

import os
from typing import NoReturn

from models.city import CityData
from models.logger import Logger
from models.points import PointsData
from models.settings import Settings
from src.core import find_and_parse_files
from src.gui_manager import PointsGUI

# Загрузить настройки
settings = Settings()
log_manager = Logger(settings)
logger = log_manager.get_logger()


def main() -> None:
    # Запустить GUI, передав экземпляры Settings и logger
    app = PointsGUI(settings, logger)
    app.mainloop()


if __name__ == "__main__":
    main()
