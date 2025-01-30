from loguru import logger

from core.browsers.ads import Ads
from core.excel import Excel
from core.browsers.modules.metamask import Metamask
from core.okx_py import OKX
from core.onchain import Onchain
from models.chain import Chain
from models.account import Account
from config import config


class Bot:
    def __init__(self, account: Account, chain: Chain = config.start_chain) -> None:
        logger.info(f"{account.profile_number} Запуск профиля")
        self.chain = chain
        self.account = account
        self.ads = Ads(account)
        self.metamask = Metamask(self.ads, account)
        self.okx = OKX(account)
        self.excel = Excel(account)
        self.onchain = Onchain(account, chain)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.ads._close_browser()
        if exc_type is None:
            logger.success(f"{self.account.profile_number} Аккаунт завершен успешно")
        elif issubclass(exc_type, TimeoutError):
            logger.error(f"{self.account.profile_number} Аккаунт завершен по таймауту")
        else:
            if "object has no attribute 'page'" in str(exc_val):
                logger.error(f"{self.account.profile_number} Аккаунт завершен с ошибкой, возможно вы выключили работу браузера и пытаетесь сделать логику работу с браузером. {exc_val}'")
            else:
                logger.critical(f"{self.account.profile_number} Аккаунт завершен с ошибкой {exc_val}")
        return True
