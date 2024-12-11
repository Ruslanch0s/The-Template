import datetime
import os
import sys

from loguru import logger

from config.settings import config
from utils.utils import send_telegram_message

profile_number = ''

def filter_record(record: dict) -> bool:
    """
    Фильтр для отлавливания событий и запуска функции отправки сообщения в телеграм
    :param record: запись лога
    :return: True
    """
    # Объявляем переменную profile_number глобальной, для хранения номера профиля
    global profile_number

    # Если в extra есть profile_number, то записываем его в переменную profile_number
    if isinstance(record["extra"].get("profile_number"), int):
        profile_number = record["extra"].get("profile_number")
    # если отправлена команда clear, то очищаем profile_number
    elif record["extra"].get("profile_number", None) == 'clear':
        record["extra"]["profile_number"] = ''
        profile_number = ''
        return False
    # если profile_number не передан, то записываем в extra profile_number
    elif record["extra"].get("profile_number", None) is None:
        record["extra"]["profile_number"] = profile_number

    if config.chat_id and config.bot_token:
        if record["level"].name in config.alert_types:
            send_telegram_message(record["message"])

        if record["extra"].get("telegram"):
            send_telegram_message(record["message"])

    return True  # Продолжаем обработку логов


def init_logger():
    logger.remove()
    logger.bind(profile_number=None)
    logger.add(
        sys.stdout,
        level="INFO",
        colorize=True,
        format="<light-cyan>{time:DD-MM HH:mm:ss}</light-cyan> | <level> {level: <8} </level><white> {file}:{function}: {line}</white> - {extra[profile_number]} <light-white>{message}</light-white>",
        filter=filter_record
    )
    log_path = os.path.join(config.PATH_LOG, 'logs.log')
    logger.add(log_path, level='DEBUG', rotation=datetime.timedelta(days=1), retention='15 days')

