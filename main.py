import asyncio
import random
import time
from pathlib import Path

from camoufox import Camoufox
from loguru import logger

from config import config
from core.browsers.modules.metamask import MetamaskExcel
from core.excel import Excel
from models.account import Account
from projects.reddio import Reddio
from utils.logging import init_logger
from utils.utils import get_accounts, random_sleep, serialize_proxy


def activity(account):
    account_excel = Excel(account)
    proxy_ip, proxy_port, proxy_login, proxy_password = serialize_proxy(account.proxy)
    with Camoufox(
            addons=[
                str(Path(config.camfox_profiles_dir, 'addons', 'metamask-firefox-12.9.3'))
            ],
            window=(1920, 1080),
            geoip=True,
            proxy={
                'server': f'http://{proxy_ip}:{proxy_port}',
                'username': proxy_login,
                'password': proxy_password
            },
            persistent_context=True,
            user_data_dir=config.camfox_profiles_dir / Path('2'),
    ) as browser:
        page = browser.pages[0]
        page.goto("https://www.browserscan.net")
        time.sleep(5)
        page.mouse.move(40, 40)
        time.sleep(3)




def worker(account: Account) -> None:
    activity(account)

    try:
        activity(account)
    except Exception as e:
        logger.critical(f"Ошибка выполнения воркера: {e}")


def main() -> None:
    init_logger()
    accounts = get_accounts()
    random.shuffle(accounts)
    for account in accounts:
        if account.status != 'in_work':
            continue
        worker(account)
        random_sleep(*config.pause_between_profile)


if __name__ == '__main__':
    main()
