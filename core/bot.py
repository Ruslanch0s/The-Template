from loguru import logger

from core.ads.ads import Ads
from core.excel import Excel
from core.ads.metamask import Metamask
from core.okx_py import OKX
from core.onchain import Onchain
from models.chain import Chain
from models.account import Account
from config import config


class Bot:
    def __init__(self, account: Account, chain: Chain = config.start_chain) -> None:
        self.chain = chain
        self.account = account
        self.ads = Ads(account)
        self.metamask = Metamask(self.ads, account)
        self.okx = OKX(account)
        self.excel = Excel(account)
        self.onchain = Onchain(account, chain)

    def __enter__(self):
        logger.bind(profile_number=self.account.profile_number).info(f"Запуск профиля")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.ads._close_browser()
        if exc_type is None:
            logger.success(f"Аккаунт завершен")
        elif issubclass(exc_type, TimeoutError):
            logger.error(f"Аккаунт завершен по таймауту")
        else:
            if "object has no attribute 'page'" in str(exc_val):
                logger.error(f"Аккаунт завершен с ошибкой, возможно вы выключили работу браузера и пытаетесь сделать логику работу с браузером. {exc_val}'")
            else:
                logger.error(f"Аккаунт завершен с ошибкой {exc_val}")
        logger.bind(profile_number='clear').info("")
        return True
