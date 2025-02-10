import asyncio

from loguru import logger

from core.browsers.chrome_browser.chrome import BotrightBrowser
from core.browsers.modules.metamask import MetamaskExcel
from core.excel import Excel
from models.account import Account
from utils.logging import init_logger
from utils.utils import get_accounts, serialize_proxy


async def activity(account):
    excel = Excel(account)
    proxy_ip, proxy_port, proxy_login, proxy_password = serialize_proxy(account.proxy)
    async with BotrightBrowser(
            profile_number=account.profile_number,
            proxy_ip=proxy_ip,
            proxy_port=proxy_port,
            proxy_login=proxy_login,
            proxy_password=proxy_password,
            addons=['MetaMask-Chrome']
    ) as browser:
        await asyncio.sleep(3)
        metamask = MetamaskExcel(
            excel=excel,
            browser=browser,
            password=account.password,
            seed=account.seed,
            profile_number=account.profile_number
        )

        await metamask.auth_metamask()

        await asyncio.sleep(999000000)

        # reddio = Reddio(
        #     browser=browser,
        #     metamask=metamask
        # )
        # await reddio.start()


async def worker(account: Account) -> None:
    try:
        await activity(account)
    except Exception as e:
        logger.critical(f"Ошибка выполнения воркера: {e}")


async def main() -> None:
    profile_number = input('Введите номер профиля: ')
    init_logger()
    accounts = get_accounts()
    for account in accounts:
        if str(account.profile_number) == str(profile_number):
            await worker(account)


if __name__ == '__main__':
    asyncio.run(main())
