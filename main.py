
"""
Главный модуль приложения PointsManager.

Запускает графический интерфейс для обработки точек из XML/JSON файлов.
Содержит точку входа main() с подробными комментариями и докстрингами согласно лучшим практикам.
"""


from models.logger import Logger
from models.settings import Settings
from src.gui_manager import PointsGUI


def main() -> None:
    """
    Точка входа приложения: инициализация и запуск графического интерфейса PointsManager.

    Последовательность действий:
        1. Загружает настройки приложения.
        2. Инициализирует логгер с заданными настройками.
        3. Создает и запускает графический интерфейс PointsGUI.
    """
    # Загружаем настройки приложения
    settings = Settings()
    # Инициализируем логгер
    logger = Logger(settings).get_logger()
    # Создаем и запускаем GUI
    app = PointsGUI(settings, logger)
    app.mainloop()


# Запуск приложения при прямом вызове модуля
if __name__ == "__main__":
    main()