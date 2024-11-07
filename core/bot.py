from loguru import logger

from core.ads.ads import Ads
from core.excel import Excel
from core.ads.metamask import Metamask
from core.okx_py import OKX
from core.onchain import Onchain
from models.chain import Chain
from models.account import Account


class Bot:
    def __init__(self, account: Account, chain: Chain) -> None:
        self.account = account
        self.ads = Ads(account)
        self.metamask = Metamask(self.ads)
        self.okx = OKX()
        self.excel = Excel(account)
        self.onchain = Onchain(account.private_key, chain)

    def __enter__(self):
        logger.info(f"Запуск профиля {self.account.profile_number}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.ads.close_browser()
        if exc_type is None:
            logger.success(f"Аккаунт {self.account.profile_number} завершен")
        elif issubclass(exc_type, TimeoutError):
            logger.error(f"Аккаунт {self.ads.profile_number} завершен по таймауту")
        else:
            logger.error(f"Аккаунт {self.ads.profile_number} завершен с ошибкой {exc_val}")
        return False


