import asyncio
import random

from loguru import logger
from playwright.async_api import BrowserContext, Page

from core.browsers.modules.metamask import Metamask
from core.excel import Excel
from models.chain import Chain
from utils.utils import async_random_sleep


class ConnectWalletException(Exception):
    pass


class ReddioFaucetPage:
    pass


class ReddioNotAuth(Exception):
    pass


class Reddio:
    def __init__(
            self,
            browser: BrowserContext,
            metamask: Metamask,
            account_excel: Excel
    ):
        self.browser = browser
        self.metamask = metamask
        self.account_excel = account_excel

    async def check_login_testnet(self, page):
        logger.info("Проверка подключен ли кошелек")
        await page.goto('https://testnet.reddio.com/')
        connect_button = await page.wait_for_selector(
            'xpath=/html/body/div/div/main/div/div[9]/div/div/div[1]/div[1]/button',
            timeout=5000)
        text_button = await connect_button.inner_text()
        if text_button == 'Added':
            logger.info("Кошелек подключен")
            return True
        logger.warning("Кошелек не подключен")

    async def connect_wallet(self, page):
        connect_button = await page.wait_for_selector(
            'xpath=/html/body/div[1]/div/main/div/div[9]/div/div/div[1]/div[1]/button',
            timeout=1000)
        await connect_button.click()
        locator_metamask = page.locator(
            'xpath=/html/body/div[2]/div/div/div[2]/div/div/div/div/div[1]/div[2]/div[2]/div[3]')
        await self.metamask.connect(locator=locator_metamask)

    async def to_faucet(self, page) -> Page:
        faucet_button = await page.wait_for_selector(
            'xpath=/html/body/div[1]/div/main/div/div[9]/div/div/div[1]/div[2]/button',
            timeout=1000
        )
        async with self.browser.expect_page(timeout=3 * 1000) as page_catcher:
            await faucet_button.click()
        faucet_page = await page_catcher.value
        return faucet_page

    async def set_network(self):
        chain = Chain(
            name='RED',
            rpc='https://reddio-dev.reddio.com',
            chain_id=50341,
            metamask_name='Reddio Devnet',
            explorer_url='reddio-devnet.l2scan.co'
        )
        await self.metamask.select_chain(chain=chain)

    async def login_testnet(self, page: Page):
        if not await self.check_login_testnet(page):
            await self.set_network()
            await self.connect_wallet(page)
            if not await self.check_login_testnet(page):
                raise ConnectWalletException('Ошибка подключения кошелька')

    ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

    async def connect_wallet_points(self, page):
        connect_button = await page.wait_for_selector(
            'xpath=/html/body/div[1]/main/div/div[8]/div/div/div[2]/div[2]/button',
            timeout=1000)
        await connect_button.click()
        locator_metamask = page.locator(
            'xpath=/html/body/div[3]/div/div/div[2]/div/div/div/div/div[1]/div[2]/div[2]')
        await self.metamask.connect(locator=locator_metamask)

    async def check_login_points(self, page: Page):
        logger.info("Проверка подключен ли кошелек")
        await page.goto('https://points.reddio.com/profile')

        try:
            profile_wallet = await page.wait_for_selector(
                'xpath=/html/body/div[1]/main/div/header/div[2]/div/div/div/span[2]',
                timeout=3000
            )
            return True
        except:
            logger.info('Кошелек не подключен')
            return False

    async def login_points(self, page: Page):
        if not await self.check_login_points(page):
            await self.set_network()
            await self.connect_wallet_points(page)
            if not await self.check_login_points(page):
                raise ConnectWalletException('Ошибка подключения кошелька')

    async def check_auth(self, page: Page):
        logger.info('Raddio check auth')
        # go to profile page
        await page.goto('https://points.reddio.com/profile')
        # check Points text
        try:
            await page.wait_for_selector(
                'xpath=/html/body/div[1]/main/div/div[8]/div/div[2]/div[1]/div/div[1]/div[1]/p',
                timeout=3000
            )
            logger.info('Raddio success auth')
        except:
            err = "Reddio not auth"
            logger.error(err)
            self.set_reddio_error_info(err)
            raise ReddioNotAuth(err)

    def set_reddio_error_info(self, message: str):
        self.account_excel.set_cell('Radio Error info', message)

    def clear_reddio_error_info(self):
        self.account_excel.set_cell('Radio Error info', ' ')

    async def daily_faucet(self, page: Page):
        logger.info('Проверка Reddio Faucet')
        # check checkin
        try:
            button = await page.wait_for_selector(
                'xpath=/html/body/div[1]/main/div/div[8]/div/div[2]/div[1]/button',
                timeout=3000
            )
        except:
            logger.warning('Уже выполнен Reddio Faucet')
            return

        button_text = await button.inner_text()
        if button_text == 'Go':
            logger.info('Переходим в кран')
            async with self.browser.expect_page(timeout=3000) as page_catcher:
                await button.click()
            page = await page_catcher.value
            await async_random_sleep()
            logger.info('Вводим кошелек')
            input_sel = await page.wait_for_selector(
                'xpath=/html/body/div/div[2]/div[1]/div[2]/div[2]/div/div[1]/input',
                timeout=5000
            )
            await input_sel.click()
            await async_random_sleep()
            await input_sel.fill(await self.metamask.get_address())
            await async_random_sleep()
            button_enter = await page.wait_for_selector(
                'xpath=/html/body/div/div[2]/div[1]/div[2]/div[2]/div/div[1]/button',
                timeout=1000
            )
            await button_enter.click()
            await page.wait_for_selector(
                'xpath=/html/body/div/div[1]/div/div',
                timeout=5000
            )
            logger.info('Успешный налив')

        elif button_text == 'Verify':
            await button.click()
        else:
            logger.info('Reddio Faucet выполнено')

    async def go_tasks(self, page: Page):
        # go to tasks page
        await page.goto('https://points.reddio.com/task')
        tasks = [
            self.daily_faucet
        ]
        random.shuffle(tasks)
        for task in tasks:
            await task(page)
            await async_random_sleep()

    async def start(self):
        logger.info("Reddio Points Start")
        status_project = self.account_excel.get_cell('Reddio status')
        if status_project != 'in_work':
            return

        self.clear_reddio_error_info()
        main_page = await self.browser.new_page()
        await self.check_auth(main_page)
        await async_random_sleep()
        await self.go_tasks(main_page)

        return
        main_page = await self.browser.new_page()
        await self.login_points(main_page)
        await async_random_sleep(1, 3)

        # faucet_page = await self.to_faucet(main_page)
        await asyncio.sleep(111111)
