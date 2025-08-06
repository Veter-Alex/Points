
"""
Модуль для централизованного управления логированием приложения PointsManager.

Содержит класс Logger, который настраивает уровень, формат, ротацию и вывод логов.
Все методы снабжены подробными комментариями и докстрингами согласно лучшим практикам.
"""

import os
import sys
from typing import Optional

from loguru import logger
from models.settings import Settings

class Logger:
    """
    Класс для управления логированием приложения PointsManager.

    Позволяет централизованно настраивать уровень, формат, ротацию и вывод логов.
    """

    def __init__(self, settings: Optional[Settings]):
        """
        Инициализация Logger с настройками приложения.

        Args:
            settings (Optional[Settings]): Объект с настройками приложения.
        """
        self.settings = settings
        self.log_level: str = self._get_log_level()
        self._configure_logger()

    def _get_log_level(self) -> str:
        """
        Получает уровень логирования из переменной окружения или настроек.

        Returns:
            str: Уровень логирования (например, 'INFO', 'DEBUG').
        """
        env_level = os.environ.get("LOG_LEVEL")
        if env_level:
            return env_level.strip().upper()
        return getattr(self.settings, "log_level", "INFO").upper()

    def _configure_logger(self) -> None:
        """
        Конфигурирует логгер: добавляет вывод в stdout и файл с ротацией.
        """
        os.makedirs("logs", exist_ok=True)
        logger.remove()
        logger.add(
            sys.stdout,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            level=self.log_level,
        )
        logger.add(
            "logs/app.log",
            rotation="10 MB",
            retention=10,
            encoding="utf-8",
            level=self.log_level,
            backtrace=True,
            diagnose=True,
        )

    def set_level(self, level: str) -> None:
        """
        Динамически изменяет уровень логирования.

        Args:
            level (str): Новый уровень логирования.
        """
        self.log_level = level.upper()
        self._configure_logger()

    def get_logger(self):
        """
        Возвращает объект логгера loguru.

        Returns:
            loguru.Logger: Экземпляр логгера.
        """
        return logger
