import time

from eth_account import Account
from loguru import logger

from config import Chains
from core.bot import Bot
from utils.logging import init_logger
from utils.utils import random_sleep
from utils.utils import get_accounts


def main():
    """ Основная функция """
    # Инициализация консоли и логгера
    init_logger()
    # Получаем список аккаунтов из файлов
    accounts = get_accounts()

    # Перебираем аккаунты
    for account in accounts:
        # передаем аккаунт в функцию worker
        try:
            worker(account)
        except Exception as e:
            logger.error(f"Ошибка в аккаунте {account.profile_number}: {e}")

def worker(account: Account) -> None:
    """
    Функция для работы с аккаунтом, создает бота и передает его в функцию activity
    :param account: аккаунт
    :return: None
    """
    # Создаем бота
    with Bot(account, Chains.LINEA) as bot:
        # Вызываем функцию activity и передаем в нее бота
        activity(bot)


def activity(bot: Bot):
    """
    Функция для работы с ботом, описываем логику активности бота.
    :param bot: бот
    :return: None
    """
    # открывать гугл и вбить в поле поиска "как узнать свой ip"
    bot.ads.open_url("https://www.google.com/")
    if bot.account.profile_number == 944:
        raise Exception("Ошибка")

    # bot.excel.increase_counter('google')
    # bot.excel.get_cell('google')
    # time.sleep(10)




if __name__ == '__main__':
    main()
