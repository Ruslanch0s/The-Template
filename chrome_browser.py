import argparse
import asyncio

from core.browsers.chrome_browser.chrome import BotrightBrowser


async def run_browser(serial_number):
    async with BotrightBrowser(
            serial_number=serial_number,
            proxy='puxtbrxz:tdym3r4xte8q@198.23.239.134:6540',
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
    # Создаем парсер аргументов
    parser = argparse.ArgumentParser(description="Запуск браузера с указанным серийным номером.")
    parser.add_argument("serial_number", type=int, help="Серийный номер браузера")

    # Парсим аргументы
    args = parser.parse_args()

    # Запускаем асинхронный код
    asyncio.run(run_browser(args.serial_number))


if __name__ == "__main__":
    main()
