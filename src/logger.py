import os
import sys

from loguru import logger

# Создать папку logs, если нет
os.makedirs("logs", exist_ok=True)

# Настройка логгера: лог в файл logs/app.log и в консоль, ротация по размеру, кодировка utf-8
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
)
logger.add(
    "logs/app.log",
    rotation="10 MB",
    encoding="utf-8",
    level="INFO",
    backtrace=True,
    diagnose=True,
)

# Пример использования:
# logger.info("Информационное сообщение")
# logger.error("Ошибка: {}", err)
# logger.error("Ошибка: {}", err)
