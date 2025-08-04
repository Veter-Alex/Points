import os
import sys

from loguru import logger

from models.settings import Settings

# Создать папку logs, если нет
os.makedirs("logs", exist_ok=True)


# Получить уровень логирования из Settings или переменной окружения
def get_log_level():
    # Попытаться получить из переменной окружения
    env_level = os.environ.get("LOG_LEVEL")
    if env_level:
        return env_level.strip().upper()
    # Получить из Settings
    try:
        settings = Settings()
        return getattr(settings, "log_level", "INFO").upper()
    except Exception:
        return "INFO"


LOG_LEVEL = get_log_level()

# Настройка логгера: лог в файл logs/app.log и в консоль, ротация по размеру, кодировка utf-8
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level=LOG_LEVEL,
)
logger.add(
    "logs/app.log",
    rotation="10 MB",
    retention=10,  # Хранить не более 10 файлов логов
    encoding="utf-8",
    level=LOG_LEVEL,
    backtrace=True,
    diagnose=True,
)

# Пример использования:
# logger.info("Информационное сообщение")
# logger.error("Ошибка: {}", err)
