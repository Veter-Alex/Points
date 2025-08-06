"""
Модуль для централизованного управления логированием приложения PointsManager.
Содержит класс Logger, который настраивает уровень, формат, ротацию и вывод логов.
"""

import os
import sys
from typing import Optional

from loguru import logger

from models.settings import Settings


class Logger:
    """
    Класс для управления логированием приложения PointsManager.
    """

    def __init__(self, settings: Optional[Settings]):
        self.settings = settings
        self.log_level = self._get_log_level()
        self._configure_logger()

    def _get_log_level(self) -> str:
        env_level = os.environ.get("LOG_LEVEL")
        if env_level:
            return env_level.strip().upper()
        return getattr(self.settings, "log_level", "INFO").upper()

    def _configure_logger(self) -> None:
        os.makedirs("logs", exist_ok=True)
        logger.remove()
        log_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        )
        if sys.stdout:
            logger.add(sys.stdout, format=log_format, level=self.log_level)
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
        self.log_level = level.upper()
        self._configure_logger()

    def get_logger(self):
        """Возвращает объект логгера loguru (обратная совместимость)."""
        return logger

    @property
    def instance(self):
        """Возвращает объект логгера loguru."""
        return logger
