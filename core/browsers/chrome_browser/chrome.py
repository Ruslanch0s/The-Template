from __future__ import annotations
from __future__ import annotations

import asyncio
import sys
from pathlib import PurePath, Path
from tempfile import TemporaryDirectory
from typing import List, Optional

import httpx
from async_class import link
from botright import ProxyManager, Botright, Faker
from botright.playwright_mock import BrowserContext
from browsers import Browser

from config.settings import config


async def custom_new_browser(botright: Botright, proxy: ProxyManager, faker: Faker, flags: List[str],
                             temp_dir_path: str = None, extension_paths: list[str] = None,
                             **launch_arguments) -> BrowserContext:
    if botright.mask_fingerprint:
        fingerprint = faker.fingerprint
        parsed_launch_arguments = {
            "locale": "en-US",
            "user_agent": fingerprint.navigator.user_agent,
            "timezone_id": proxy.timezone,
            "geolocation": {"longitude": proxy.longitude, "latitude": proxy.latitude, "accuracy": 0.7},
            "permissions": ["geolocation"],
            "ignore_https_errors": True,
            "screen": {"width": fingerprint.screen.width, "height": fingerprint.screen.height},
            "viewport": {"width": fingerprint.screen.avail_width, "height": fingerprint.screen.avail_height},
            "color_scheme": "dark",
            "proxy": proxy.browser_proxy,
            "http_credentials": {"username": proxy.username, "password": proxy.password} if proxy.username else None,
            "ignore_default_args": ["--enable-automation"],
            **launch_arguments,
        }  # self.faker.locale
    else:
        parsed_launch_arguments = {
            "locale": "en-US",
            "timezone_id": proxy.timezone,
            "geolocation": {"longitude": proxy.longitude, "latitude": proxy.latitude, "accuracy": 0.7},
            "ignore_https_errors": True,
            "color_scheme": "dark",
            "proxy": proxy.browser_proxy,
            "http_credentials": {"username": proxy.username, "password": proxy.password} if proxy.username else None,
            "ignore_default_args": ["--enable-automation"],
            **launch_arguments,
        }  # self.faker.locale

    if not temp_dir_path:
        if sys.version_info.minor >= 10:
            temp_dir = TemporaryDirectory(prefix="botright-", ignore_cleanup_errors=True)
        else:
            temp_dir = TemporaryDirectory(prefix="botright-")
        temp_dir_path = temp_dir.name
        botright.temp_dirs.append(temp_dir)
    print(temp_dir_path)

    # Добавляем расширение, если путь указан
    if extension_paths:
        for extension_path in extension_paths:
            flags.extend([
                f"--disable-extensions-except={extension_path}",
                f"--load-extension={extension_path}",
            ])

    # Spawning a new Context for more options
    if proxy.browser_proxy:
        _browser = await botright.playwright.chromium.launch_persistent_context(
            user_data_dir=temp_dir_path, headless=botright.headless, executable_path=botright.browser["path"],
            args=flags, chromium_sandbox=True, **parsed_launch_arguments
        )
    else:
        _browser = await botright.playwright.chromium.launch_persistent_context(
            user_data_dir=temp_dir_path, headless=botright.headless, executable_path=botright.browser["path"],
            args=flags, chromium_sandbox=True, **parsed_launch_arguments
        )

    browser = BrowserContext(
        _browser,
        proxy,
        faker,
        use_undetected_playwright=botright.use_undetected_playwright,
        cache=botright.cache,
        user_action_layer=botright.user_action_layer,
        mask_fingerprint=botright.mask_fingerprint,
        scroll_into_view=botright.scroll_into_view,
    )

    # Preprocessing to save computing resources
    if botright.block_images:
        await browser.block_images()

    if botright.cache_responses:
        await browser.cache_responses()

    return browser


class CustomProxyManager(ProxyManager):
    async def __ainit__(self, botright, proxy: str) -> None:
        link(self, botright)

        self.proxy = proxy.strip() if proxy else ""

        self.timeout = httpx.Timeout(20.0, read=None)
        self._httpx = httpx.AsyncClient()

        if self.proxy:
            self.split_proxy()
            self.proxy = f"{self.username}:{self.password}@{self.ip}:{self.port}" if self.username else f"{self.ip}:{self.port}"
            self.plain_proxy = f"http://{self.proxy}"
            self._phttpx = httpx.AsyncClient(proxy=self.plain_proxy)
            self.http_proxy = {"http": self.plain_proxy, "https": self.plain_proxy}

            if self.username:
                self.browser_proxy = {"server": f"{self.ip}:{self.port}", "username": self.username,
                                      "password": self.password}
            else:
                self.browser_proxy = {"server": self.plain_proxy}

            await self.check_proxy(self._phttpx)

        else:
            self._phttpx = self._httpx
            await self.check_proxy(self._phttpx)


class CustomBotright(Botright):
    async def new_browser(self, proxy: Optional[str] = None, temp_dir_path: str = None,
                          extension_paths: list[str] = None,
                          screen_size: dict = None,
                          **launch_arguments) -> BrowserContext:
        """
        Create a new Botright browser instance with specified configurations.

        Args:
            proxy (str, optional): Proxy server URL to use for the browser. Defaults to None.
            **launch_arguments: Additional launch arguments to the browser. See at `Playwright Docs <https://playwright.dev/python/docs/api/class-browsertype#browser-type-launch-persistent-context>`_.

        Returns:
            BrowserContext: A new browser context for web scraping or automation.
        """

        # Calling ProxyManager and Faker to get necessary information for Botright
        _proxy: ProxyManager = await CustomProxyManager(self, proxy)
        _faker: Faker = await Faker(self, _proxy)
        print(_faker.fingerprint.navigator.user_agent)
        print(self.browser.get('browser_type'))
        _faker.fingerprint.navigator.user_agent = _faker.adjust_browser_version(
            useragent=_faker.fingerprint.navigator.user_agent,
            browser_type='Chrome',
            browser_version=self.browser.get('version')
        )
        print('fake', _faker.fingerprint.navigator.user_agent)
        # Launching Main Browser
        if self.mask_fingerprint:
            flags = self.flags + [f"--user-agent={_faker.fingerprint.navigator.user_agent}"]
        else:
            flags = self.flags

        if screen_size:
            _faker.fingerprint.screen.width = screen_size['width']
            _faker.fingerprint.screen.height = screen_size['height']

            _faker.fingerprint.screen.avail_width = screen_size['width']
            _faker.fingerprint.screen.avail_height = screen_size['height']

        _browser = await custom_new_browser(self, _proxy, _faker, flags, temp_dir_path=temp_dir_path,
                                            extension_paths=extension_paths, **launch_arguments)
        _browser.proxy = _proxy
        _browser.faker = _faker
        _browser.user_action_layer = self.user_action_layer
        _browser.scroll_into_view = self.scroll_into_view
        _browser.mask_fingerprint = self.mask_fingerprint

        await _browser.grant_permissions(["notifications", "geolocation"])
        self.stoppable.append(_browser)

        return _browser


class BotrightBrowser:
    def __init__(
            self,
            profile_number: int,

            proxy_ip: str,
            proxy_port: str,
            proxy_login: str,
            proxy_password: str,

            addons: list[str] = None
    ):
        self.browser_config = Browser(
            browser_type='chromium',
            path=str(PurePath(config.base_dir, 'config', 'data', 'ungoogled-chromium_132.0.6834.110-1.1_windows_x64',
                              'chrome.exe')),
            display_name='Google Chrome',
            version='132.0.6834.110'
        )
        self.profile_number = profile_number
        self.proxy = f'{proxy_login}:{proxy_password}@{proxy_ip}:{proxy_port}'
        self.screen_size = {'width': 1920, 'height': 1080}
        self.temp_dir_path = Path(config.chrome_profiles_dir, str(self.profile_number))
        self.botright_client = None
        self.browser = None
        self.extension_paths = [str(Path(config.chrome_profiles_dir, 'extensions', addon)) for addon in
                                addons] if addons else []

    async def __aenter__(self):
        # # Удаляем временные директории
        # botright.Botright.delete_botright_temp_dirs()
        # Инициализируем Botright клиент
        self.botright_client = await CustomBotright(
            spoof_canvas=False,
            use_undetected_playwright=True,
            user_action_layer=True,

        )
        self.botright_client.flags.remove('--incognito')

        # Устанавливаем конфигурацию браузера
        self.botright_client.browser = self.browser_config

        # Создаем новый браузер
        self.browser = await self.botright_client.new_browser(
            proxy=self.proxy,
            temp_dir_path=str(self.temp_dir_path),
            extension_paths=self.extension_paths,
            screen_size=self.screen_size
        )

        return self.browser

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.browser:
            await self.browser.close()
        if self.botright_client:
            await self.botright_client.close()


async def main():
    async with BotrightBrowser(
            profile_number=1,
            proxy='puxtbrxz:tdym3r4xte8q@198.23.239.134:6540',
            extension_name='MetaMask'
    ) as browser:
        page = await browser.new_page()
        await page.goto("https://www.browserscan.net/browser-checker")
        await asyncio.sleep(10000)  # Ожидание для демонстрации


if __name__ == "__main__":
    asyncio.run(main())
