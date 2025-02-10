from __future__ import annotations

import json
import random
import time
from typing import Optional, Literal

import requests

from config.settings import config
from models.account import Account
from utils.utils import random_sleep, get_response

from patchright.sync_api import sync_playwright, Browser, Page, Locator, \
    Playwright, Frame
from loguru import logger


class Ads:
    _local_api_url = "http://local.adspower.net:50325/api/v1/"

    def __init__(self, account: Account):
        self.profile_number = account.profile_number
        self._profile_id = None  # id профиля в ADS, реализован геттер profile_id
        self._user_agent = None  # user_agent браузера, реализован геттер user_agent

        if config.set_proxy:
            self.proxy = account.proxy
            self._set_proxy()

        if not config.is_browser_run:
            return

        self.pw: Optional[Playwright] = None
        self._browser = self._start_browser()
        self.context = self._browser.contexts[0]
        self.page = self.context.new_page()
        self._prepare_browser()

        if config.is_mobile_proxy:
            get_response(config.link_change_ip, attempts=1,
                         return_except=False)

        if config.check_proxy:
            self._check_proxy()

    @property
    def profile_id(self) -> str:
        if not self._profile_id:
            self._profile_id = self._get_profile_id()
        return self._profile_id

    @property
    def user_agent(self) -> str:
        """
        Возвращает user_agent запущенного браузера
        :return: user_agent
        """
        if not self._user_agent:
            self._user_agent = self.page.evaluate('navigator.userAgent')
        return self._user_agent

    def _open_browser(self) -> str:
        """
        Открывает браузер в ADS, номер профиля берется из self.profile_number
        :return: параметры запущенного браузера
        """
        params = dict(serial_number=self.profile_number)
        url = self._local_api_url + 'browser/start'
        random_sleep(1, 2)
        try:
            data = get_response(url, params)
            return data['data']['ws']['puppeteer']
        except Exception as e:
            logger.error(
                f"{self.profile_number} Ошибка при открытии браузера: {e}")
            raise e

    def _check_browser_status(self) -> Optional[str]:
        """
        Проверяет статус браузера в ADS, номер профиля берется из self.profile_number
        :return: параметры запущенного браузера
        """
        params = dict(serial_number=self.profile_number)
        url = self._local_api_url + 'browser/active'
        random_sleep(1, 2)
        try:
            data = get_response(url, params)
            if data['data']['status'] == 'Active':
                logger.info(f"{self.profile_number} Браузер уже активен")
                return data['data']['ws']['puppeteer']
            return None
        except Exception as e:
            logger.error(
                f"{self.profile_number} Ошибка при проверке статуса браузера (запущен ли ADS?: {e} ")
            raise e

    def _start_browser(self) -> Browser:
        """
        Запускает браузер в ADS, номер профиля берется из self.profile_number
        Делает 3 попытки прежде чем вызвать исключение.
        :return: объект Browser
        """
        for attempt in range(3):
            try:
                # Проверяем статус браузера и запускаем его, если не активен
                if not (endpoint := self._check_browser_status()):
                    logger.info(f"{self.profile_number} Запускаем браузер")
                    random_sleep(3, 4)
                    endpoint = self._open_browser()

                # подключаемся к браузеру
                random_sleep(4, 5)
                self.pw = sync_playwright().start()
                slow_mo = random.randint(*config.speed)
                browser = self.pw.chromium.connect_over_cdp(endpoint,
                                                            slow_mo=slow_mo)
                if browser.is_connected():
                    return browser
                logger.error(
                    f"{self.profile_number} Error не удалось запустить браузер")

            except Exception as e:
                logger.error(
                    f"{self.profile_number} Error не удалось запустить браузер {e}")
                self.pw.stop() if self.pw else None
                random_sleep(5, 10)

        raise Exception(f"Error не удалось запустить браузер")

    def _prepare_browser(self) -> None:
        """
        Закрывает все страницы кроме текущей
        :return: None
        """
        try:
            for page in self.context.pages:
                if 'offscreen' in page.url:
                    continue
                if page.url != self.page.url:
                    page.close()

        except Exception as e:
            logger.error(
                f"{self.profile_number} Ошибка при закрытии страниц: {e}")
            raise e

    def _close_browser(self) -> None:
        """
        Останавливает браузер в ADS, номер профиля берется из self.profile_number
        :return: None
        """
        if not config.is_browser_run:
            return

        if not self._browser.is_connected():
            self._browser.close()

        self.pw.stop() if self.pw else None
        params = dict(serial_number=self.profile_number)
        url = self._local_api_url + 'browser/stop'
        random_sleep(1, 2)
        try:
            get_response(url, params)
        except Exception as e:
            logger.error(
                f"{self.profile_number} Ошибка при остановке браузера: {e}")
            raise e

    def catch_page(self, url_contains: str | list[str] = None,
                   timeout: int = 10) -> \
            Optional[Page]:
        """
        Ищет страницу по частичному совпадению url. Если не находит, возвращает None. Каждые 3 попытки обновляет контекст.
        :param url_contains: текст, который ищем в url или список текстов
        :param timeout: время ожидания
        :return: страница с нужным url или None
        """
        if isinstance(url_contains, str):
            url_contains = [url_contains]

        for attempt in range(timeout):
            for page in self.context.pages:
                for url in url_contains:
                    if url in page.url:
                        return page
                    if attempt and attempt % 3 == 0:
                        self.pages_context_reload()
                    random_sleep(1, 2)

        logger.warning(
            f"{self.profile_number} Ошибка страница не найдена: {url_contains}")
        return None

    def pages_context_reload(self) -> None:
        """
        Перезагружает контекст вкладок. Необходимо когда playwright не видит вкладку.
        :return: None
        """
        new_page = self.context.new_page()
        random_sleep(1, 2)
        new_page.close()

    def _set_proxy(self) -> None:
        """
        Устанавливает прокси для профиля в ADS
        :return: None
        """
        try:
            ip, port, login, password = self.proxy.split(":")

            profile_id = self._get_profile_id()

            proxy_config = {
                "proxy_type": "http",
                "proxy_host": ip,
                "proxy_port": port,
                "proxy_user": login,
                "proxy_password": password,
                "proxy_soft": "other"
            }

            data = {
                "user_id": profile_id,
                "user_proxy_config": proxy_config
            }
            url = self._local_api_url + "user/update"
            response = requests.post(url, json=data, headers={
                "Content-Type": "application/json"})
            response.raise_for_status()
            random_sleep(2)

        except Exception as e:
            logger.error(
                f"{self.profile_number} Ошибка при установке прокси: {e}")
            raise e

    def _get_profile_id(self) -> str:
        """
        Запрашивает id профиля в ADS по номеру профиля
        :return: id профиля в ADS
        """
        url = self._local_api_url + 'user/list'
        params = {"serial_number": self.profile_number}

        random_sleep(1, 2)
        try:
            data = get_response(url, params)
            return data['data']['list'][0]['user_id']
        except Exception as e:
            logger.error(
                f"{self.profile_number} Ошибка при получении id профиля: {e}")
            raise e

    def _check_proxy(self) -> None:
        """
        Проверяет, что прокси работает, сравнивая ip профиля и прокси, вызывает исключение, если не совпадают
        :return: None
        """
        ip, port, login, password = self.proxy.split(":")
        current_ip = self._get_ip()
        logger.error(f"{self.profile_number} Текущий ip: {current_ip}")
        if current_ip != ip:
            raise Exception("Прокси не работает")

    def _get_ip(self) -> str:
        """
        # Получает ip текущего профиля
        # :return: ip_check_browser_status
        # """
        try:
            ip = self.page.evaluate('''
                        async () => {
                            const response = await fetch('https://api.ipify.org');
                            const data = await response.text();
                            return data;
                        }
                    ''')
        except Exception:
            logger.error(f"{self.profile_number} Ошибка при получении ip")
            self.page.goto("https://api.ipify.org/?format=json")
            random_sleep(1, 2)
            ip_text = self.page.locator(
                "//pre").inner_text()  # парсим json и возвращаем ip
            ip = json.loads(ip_text)["ip"]  # парсим json и возвращаем ip

        return ip

    def open_url(
            self,
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
        if self.page.url != url:
            for attempt in range(attempts):
                try:
                    self.page.goto(url, wait_until=wait_until, timeout=timeout)
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

    def click_if_exists(
            self,
            locator: Optional[Locator] = None,
            *,
            method: Optional[Literal["test_id", "role", "text"]] = None,
            value: Optional[str] = None
    ) -> None:
        """
        Кликает по элементу, если он существует, можно передать локатор или метод поиска и имя элемента
        :param locator: локатор элемента
        :param method: метод поиска элемента
        :param name: value для поиска элемента, если role, в формате "role:name"
        :return:
        """
        if not locator:
            match method:
                case "test_id":
                    locator = self.page.get_by_test_id(value)
                case "role":
                    role, name = value.split(":", 1)
                    locator = self.page.get_by_role(role, name=name)
                case "text":
                    locator = self.page.get_by_text(value)
        random_sleep(2, 3)
        if locator.count():
            locator.click()

    def click_and_catch_page(self, locator: Locator, timeout=30) -> Page:
        """
        Кликает по элементу и ждет появления страницы, ловит и возвращает ее
        :param locator: локатор элемента
        :return: страница
        """
        with self.context.expect_page(timeout=timeout * 1000) as page_catcher:
            locator.click()
        return page_catcher.value

    def get_text_with_clipboard(self, locator: Locator) -> str:
        """
        Получает текст из элемента через буфер обмена
        :param locator: локатор элемента
        :return: текст из элемента
        """
        import pyperclip

        old_clipboard = pyperclip.paste()
        # кликаем по элементу, чтобы скопировать текст в буфер обмена
        locator.click()
        # получаем текст из буфера обмена
        new_clipboard = pyperclip.paste()

        # восстанавливаем старое значение
        pyperclip.copy(old_clipboard)

        return new_clipboard

    def keyboard_emulation(self, locator: Locator, text: str,
                           mistake: bool = False) -> None:
        """
        Вводит текст в поле посимвольно с паузой от 0.1 до 0.5 секунды.
        :param mistake: допускать ли ошибки при вводе
        :param locator: локатор текстового поля
        :param text: текст который нужно ввести в поле
        :return: None
        """
        for symbol in text:
            if mistake and random.randint(0, 10) > 8:
                random_symbol = random.choice('abcdefghijklmnopqrstuvwxyz')
                locator.press_sequentially(random_symbol)
                random_sleep(0.01, 0.1)
                locator.press('Backspace')
            locator.press_sequentially(symbol)
            random_sleep(0.01, 0.1)

    def dump_frame_tree(self, page: Optional[Page] = None) -> None:
        """
        Рекурсивно выводит дерево фреймов.
        :param page: страница, если не передана, то используется текущая страница в атрибуте ads.page
        :return: None
        """
        if not page:
            page = self.page
        self._dump_frame_tree(page.main_frame)

    def _dump_frame_tree(self, frame: Frame, indent: str = "") -> None:
        """
        Рекурсивно выводит дерево фреймов, необходимо передать main_frame.
        :param frame: фрейм
        :param indent: отступ
        :return: None
        """
        print(indent + frame.name + '@' + frame.url)
        for child in frame.child_frames:
            self._dump_frame_tree(child, indent + "    ")
