import argparse
import asyncio
from loguru import logger
from core.browsers.chrome_browser.chrome import BotrightBrowser
from utils.logging import init_logger
from utils.utils import get_accounts, prepare_proxy, check_proxy


async def run_browser(profile_number):
    accounts = get_accounts()
    account = None
    for _account in accounts:
        if _account.profile_number == profile_number:
            account = _account
            break

    if not account:
        logger.error(f'Аккаунт #{profile_number} в таблице не найден')
        return

    proxy = prepare_proxy(account.proxy)
    if not check_proxy(proxy):
        logger.error(f"Ошибка прокси {proxy}, профиль #{profile_number}")
        return

    # puxtbrxz:tdym3r4xte8q@198.23.239.134:6540
    async with BotrightBrowser(
            profile_number=account.profile_number,
            proxy=proxy,
            extension_name='MetaMask'
    ) as browser:
        page = await browser.new_page()
        await page.goto("https://www.browserscan.net/browser-checker")
        print("Браузер запущен, страница загружена.")
        while True:
            try:
                # Проверяем состояние браузера
                if not browser.pages:
                    return
            # Попытка получить заголовок страницы
            except Exception as err:
                print(f"Браузер закрыт или произошла ошибка")
                break

            await asyncio.sleep(3)  # Ожидание для демонстрации


def main():
    init_logger()
    # Создаем парсер аргументов
    parser = argparse.ArgumentParser(description="Запуск браузера с указанным серийным номером.")
    parser.add_argument("profile_number", type=int, help="Серийный номер браузера")

    # Парсим аргументы
    args = parser.parse_args()

    # Запускаем асинхронный код
    asyncio.run(run_browser(args.profile_number))


if __name__ == "__main__":
    main()
