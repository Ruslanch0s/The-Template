from typing import Optional, Literal

from loguru import logger
from playwright.sync_api import Locator, Page

from utils.utils import random_sleep


class Helper:
    def __init__(self, context):
        self.context = context

    # @abstractmethod
    # async def open_browser(self):
    #     pass
    #
    # @abstractmethod
    # async def close_browser(self):
    #     pass
    #
    # async def __aenter__(self):
    #     await self.close_browser()
    #     return self
    #
    # async def __aexit__(self, exc_type, exc, tb):
    #     await self.close_browser()
    async def click_and_catch_page(self, locator: Locator, timeout=30) -> Page:
        """
        Кликает по элементу и ждет появления страницы, ловит и возвращает ее
        :param locator: локатор элемента
        :return: страница
        """
        with self.context.expect_page(timeout=timeout * 1000) as page_catcher:
            locator.click()
        return page_catcher.value

    def open_url(
            self,
            page: Page,
            url: str,
            wait_until: Optional[
                Literal["commit", "domcontentloaded", "load", "networkidle"]
            ] = "load",
            locator: Optional[Locator] = None,
            timeout: int = 30,
            attempts: int = 1
    ) -> None:
        """
        Открывает страницу по url, если еще не открыта. Может ждать элемент на странице.
        :param url: ссылка на страницу, желательно в формате https://
        :param wait_until: состояние страницы, когда считается что она загрузилась. По умолчанию load.
        :param locator: элемент, который нужно дождаться на странице
        :param timeout: время ожидания в секундах
        :param attempts: количество попыток открыть страницу
        :return: None
        """
        # Переводим время ожидания в миллисекунды, если передали секунды
        if timeout < 1000:
            timeout = timeout * 1000

        # Проверяем, если передана ссылка на расширение chrome
        if not url.startswith("chrome-extension"):
            # Проверяем и добавляем https:// если необходимо
            if not (url.startswith("http://") or url.startswith("https://")):
                url = f"https://{url}"

        # Проверяем, если одна из версий URL уже открыта
        if page.url != url:
            for attempt in range(attempts):
                try:
                    page.goto(url, wait_until=wait_until, timeout=timeout)
                    break
                except Exception as e:
                    if attempt == attempts - 1:
                        raise e
                    logger.error(
                        f"{self.profile_number} Ошибка при открытии страницы {url}: {e}")
                    random_sleep(1, 2)

        # Если передан xpath, ждем элемент на странице заданное время
        if locator:
            locator.wait_for(state='visible', timeout=timeout)
