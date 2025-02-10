import asyncio

from loguru import logger
from playwright.async_api import Locator, BrowserContext

from core.excel import Excel
from models.chain import Chain
from utils.utils import generate_password


class MetamaskCreateException(Exception):
    pass


class Metamask:
    """
    Класс для работы с MetaMask v. 12.9.3
    """

    def __init__(self, browser: BrowserContext, password: str, seed: str, profile_number: int):
        self._url = "chrome-extension://kfjimnpjdnmkflhlihofnjcdpofmkohb/home.html"
        self.browser = browser
        self.password = password
        self.seed = seed
        self.page = None
        self.profile_number = profile_number

    async def open_metamask(self):
        """
        Открывает MetaMask и ждет появления кнопок, подтверждающих загрузку страницы.
        """
        if not self.page:
            self.page = await self.browser.new_page()
        await self.page.goto(self._url)
        await asyncio.sleep(1)

    async def create_wallet(self) -> tuple[str, str, str]:
        """
        Создает кошелек в MetaMask, возвращает адрес кошелька, seed-фразу и пароль в виде кортежа.
        :return: tuple (address, seed, password)
        """
        await self.open_metamask()
        try:
            await self.page.get_by_test_id('onboarding-terms-checkbox').wait_for(
                timeout=5000, state='visible')
        except Exception as e:
            raise Exception(
                f"Ошибка создания кошелька {self.profile_number}: вероятно, в MetaMask уже есть счет. Обнулите расширение. {e}")

        await self.page.get_by_test_id('onboarding-terms-checkbox').click()
        await self.page.get_by_test_id('onboarding-create-wallet').click()
        await self.page.get_by_test_id('metametrics-no-thanks').click()

        # Генерируем пароль и вводим в 2 поля
        if not self.password:
            self.password = generate_password()
        await self.page.get_by_test_id('create-password-new').fill(self.password)
        await self.page.get_by_test_id('create-password-confirm').fill(self.password)
        await self.page.get_by_test_id('create-password-terms').click()
        await self.page.get_by_test_id('create-password-wallet').click()

        await self.page.get_by_test_id('secure-wallet-recommended').click()
        await self.page.get_by_test_id('recovery-phrase-reveal').click()

        seed = []
        for i in range(12):
            test_id = f"recovery-phrase-chip-{i}"
            word = await self.page.get_by_test_id(test_id).inner_text()
            seed.append(word)

        await self.page.get_by_test_id('recovery-phrase-next').click()
        for i in range(12):
            if await self.page.get_by_test_id(f'recovery-phrase-input-{i}').count():
                await self.page.get_by_test_id(f'recovery-phrase-input-{i}').fill(seed[i])
        await self.page.get_by_test_id('recovery-phrase-confirm').click()
        await asyncio.sleep(1)
        await self.page.get_by_test_id('onboarding-complete-done').click()
        await self.page.get_by_test_id('pin-extension-next').click()
        await self.page.get_by_test_id('pin-extension-done').click()
        await asyncio.sleep(1)
        await self.page.get_by_test_id('popover-close').click()

        address = await self.get_address()
        seed_str = " ".join(seed)

        return address, seed_str, self.password

    async def auth_metamask(self) -> None:
        """
        Открывает страницу расширения MetaMask и авторизуется, вводя пароль.
        """
        await self.open_metamask()
        if not self.password:
            raise Exception(
                f"{self.profile_number}: не указан пароль для авторизации в MetaMask")

        try:
            await self.page.get_by_test_id('unlock-password').wait_for(
                timeout=5000, state='visible')
            await self.page.get_by_test_id('unlock-password').fill(self.password)
            await self.page.get_by_test_id('unlock-submit').click()
            # await asyncio.sleep(1)
            # await self.page.get_by_test_id('popover-close', timeout=3000).click()
        except Exception as e:
            logger.warning(
                f"{self.profile_number}: не смогли авторизоваться в MetaMask, вероятно, уже авторизованы. {e}")

        if await self.page.get_by_test_id('account-options-menu-button').count():
            logger.info(
                f"{self.profile_number}: успешно авторизован в MetaMask")
        else:
            logger.error(
                f"{self.profile_number}: ошибка авторизации в MetaMask, не смогли войти в кошелек")

    async def import_wallet(self) -> tuple[str, str, str]:
        """
        Импортирует кошелек в MetaMask, используя seed-фразу. Возвращает адрес кошелька и пароль в виде кортежа.
        :return: tuple (address, seed, password)
        """
        await self.open_metamask()

        seed_list = self.seed.split(" ")
        if not self.password:
            self.password = generate_password()
        try:
            await self.page.get_by_test_id('onboarding-create-wallet').wait_for(
                timeout=5000, state='visible')
            await self.page.get_by_test_id('onboarding-terms-checkbox').click()
            await self.page.get_by_test_id('onboarding-import-wallet').click()
            await self.page.get_by_test_id('metametrics-no-thanks').click()
            for i, word in enumerate(seed_list):
                await self.page.get_by_test_id(f"import-srp__srp-word-{i}").fill(word)
            await self.page.get_by_test_id('import-srp-confirm').click()
            await self.page.get_by_test_id('create-password-new').fill(self.password)
            await self.page.get_by_test_id('create-password-confirm').fill(self.password)
            await self.page.get_by_test_id('create-password-terms').click()
            await self.page.get_by_test_id('create-password-import').click()
            await asyncio.sleep(1)
            await self.page.get_by_test_id('onboarding-complete-done').click()
            await self.page.get_by_test_id('pin-extension-next').click()
            await self.page.click_if_exists(method='test_id', value='pin-extension-done')
        except Exception as e:
            logger.warning(
                f"{self.profile_number}: в MetaMask уже имеется счет, делаем сброс и импортируем новый. {e}")
            await self.page.get_by_text('Forgot password?').click()
            for i, word in enumerate(seed_list):
                await self.page.get_by_test_id(f"import-srp__srp-word-{i}").fill(word)
            await self.page.get_by_test_id('create-vault-password').fill(self.password)
            await self.page.get_by_test_id('create-vault-confirm-password').fill(self.password)
            await self.page.get_by_test_id('create-new-vault-submit-button').click()

        await asyncio.sleep(1)
        await self.page.click_if_exists(method='test_id', value='popover-close')
        address = await self.get_address()
        seed_str = " ".join(seed_list)
        return address, seed_str, self.password

    async def get_address(self) -> str:
        """
        Возвращает адрес кошелька.
        :return: адрес кошелька
        """
        await self.page.get_by_test_id('account-options-menu-button').click()
        await self.page.get_by_test_id('account-list-menu-details').click()
        address = await self.page.locator('.qr-code__address-segments').inner_text()
        address = address.replace('\n', '')
        return address

    async def connect(self, locator: Locator, timeout: int = 30) -> None:
        """
        Подтверждает подключение к MetaMask.
        :param locator: локатор кнопки подключения, после нажатия которой появляется окно MetaMask.
        :param timeout: время ожидания в секундах, по умолчанию 30
        """
        await self.open_metamask()
        try:
            async with self.browser.expect_page(timeout=timeout * 1000) as page_catcher:
                await locator.click()
            metamask_page = await page_catcher.value
        except Exception as e:
            logger.warning(
                f"{self.profile_number}: не смогли поймать окно MetaMask, пробуем еще. {e}")
            # locator = ['notification', 'connect', 'confirm-transaction']
            async with self.browser.expect_page(timeout=timeout * 1000) as page_catcher:
                await locator.click()
            metamask_page = await page_catcher.value
            if not metamask_page:
                raise Exception(
                    f"Ошибка: {self.profile_number} не удалось подключиться к MetaMask")

        await metamask_page.wait_for_load_state('load')
        await metamask_page.get_by_test_id('confirm-btn').click()

    async def sign(self, locator: Locator, timeout: int = 30) -> None:
        """
        Подтверждает подпись в MetaMask.
        :param locator: локатор кнопки вызова подписи.
        :param timeout: время ожидания в секундах, по умолчанию 30
        """
        try:
            async with self.browser.expect_page(timeout=timeout * 1000) as page_catcher:
                await locator.click()
            metamask_page = await page_catcher.value
        except Exception as e:
            logger.warning(
                f"{self.profile_number}: не смогли поймать окно MetaMask. {e}")
            metamask_page = await self.browser.catch_page(['confirm-transaction'])
            if not metamask_page:
                raise Exception(
                    f"Ошибка: {self.profile_number} не удалось подписать сообщение в MetaMask")

        await metamask_page.wait_for_load_state('load')
        confirm_button = metamask_page.get_by_test_id('page-container-footer-next')
        if not await confirm_button.count():
            confirm_button = metamask_page.get_by_test_id('confirm-footer-button')
        await confirm_button.click()

    async def send_tx(self, locator: Locator, timeout: int = 30) -> None:
        """
        Подтверждает отправку транзакции в MetaMask.
        :param locator: локатор кнопки вызова транзакции.
        :param timeout: время ожидания в секундах, по умолчанию 30
        """
        try:
            async with self.browser.expect_page(timeout=timeout * 1000) as page_catcher:
                await locator.click()
            metamask_page = await page_catcher.value
        except Exception as e:
            logger.warning(
                f"{self.profile_number}: не смогли поймать окно MetaMask. {e}")
            metamask_page = await self.browser.catch_page(['notification', 'confirm-transaction'])
            if not metamask_page:
                raise Exception(
                    f"Ошибка: {self.profile_number} не удалось подтвердить транзакцию в MetaMask")

        await metamask_page.wait_for_load_state('load')
        confirm_button = metamask_page.get_by_test_id('confirm-footer-button')
        if not await confirm_button.count():
            confirm_button = metamask_page.get_by_test_id('page-container-footer-next')
        await confirm_button.click()

    async def select_chain(self, chain: Chain) -> None:
        """
        Выбирает сеть в MetaMask. Если сеть не найдена, добавляет новую из параметра chain.
        :param chain: объект сети Chain
        """
        await self.open_metamask()
        await self.page.get_by_test_id("network-display").wait_for(timeout=5000, state='visible')
        chain_button = self.page.get_by_test_id("network-display")
        if chain.metamask_name == await chain_button.inner_text():
            return

        await chain_button.click()
        await asyncio.sleep(1)
        enabled_networks = self.page.locator('div[data-rbd-droppable-id="characters"]')
        if await enabled_networks.get_by_text(chain.metamask_name, exact=True).count():
            await enabled_networks.get_by_text(chain.metamask_name, exact=True).click()
        else:
            close_button = await self.page.wait_for_selector(
                'xpath=/html/body/div[3]/div[3]/div/section/header/div[2]/button',
                timeout=1000
            )
            await close_button.click()
            await self.set_chain(chain)
            await self.select_chain(chain)

    async def set_chain(self, chain: Chain) -> None:
        """
        Добавляет новую сеть в MetaMask. Берет параметры из объекта Chain.
        :param chain: объект сети
        """

        await self.page.goto(self._url + "#settings/networks/add-network")
        await self.page.get_by_test_id('network-form-network-name').wait_for(timeout=15000, state='visible')
        await self.page.get_by_test_id('network-form-network-name').fill(chain.metamask_name)
        await self.page.get_by_test_id('test-add-rpc-drop-down').click()
        sel = await self.page.wait_for_selector(
            'xpath=/html/body/div[3]/div[3]/div/section/div/div[1]/div[2]/div[2]',
            timeout=1000
        )
        await sel.click()
        await self.page.get_by_test_id('rpc-url-input-test').fill(chain.rpc)
        sel = await self.page.wait_for_selector(
            'xpath=/html/body/div[3]/div[3]/div/section/div/div[2]/button',
            timeout=1000
        )
        await sel.click()
        if await self.page.get_by_test_id('network-form-chain-id-error').count():
            raise Exception(
                f"Ошибка: {self.profile_number} MetaMask не принимает RPC {chain.rpc}, попробуйте другой")
        await self.page.get_by_test_id('network-form-chain-id').fill(str(chain.chain_id))
        await self.page.get_by_test_id('network-form-ticker-input').fill(chain.native_token)
        sel = await self.page.wait_for_selector(
            'xpath=/html/body/div[3]/div[3]/div/section/div/div[2]/button',
            timeout=1000
        )
        await sel.click()

    async def change_chain_data(self, chain: Chain) -> None:
        """
        Меняет параметры сети в MetaMask. Берет данные из объекта Chain.
        :param chain: объект сети
        """
        await self.open_metamask()
        await self.page.get_by_test_id('network-display').click()

        hex_id = hex(chain.chain_id)
        if not await self.page.get_by_test_id(f'network-list-item-options-button-{hex_id}').count():
            logger.info(
                f'{self.profile_number}: Сеть {chain.metamask_name} не найдена в списке установленных. Устанавливаем.')
            await self.page.get_by_role('button', name='Close').first.click()
            await self.set_chain(chain)
            return

        await self.page.get_by_test_id(f'network-list-item-options-button-{hex_id}').click()
        await self.page.get_by_test_id('network-list-item-options-edit').click()

        if await self.page.get_by_test_id('network-form-network-name').get_attribute('value') != chain.metamask_name:
            await self.page.get_by_test_id('network-form-network-name').fill(chain.metamask_name)

        rpc_element = self.page.locator('//button[@data-testid="test-add-rpc-drop-down"]/../..')
        if await rpc_element.get_attribute('data-original-title') != chain.rpc:
            await rpc_element.click()
            rpc_without_https = chain.rpc.replace('https://', '')
            if await self.page.get_by_role('tooltip').get_by_text(rpc_without_https).count():
                await self.page.get_by_role('tooltip').get_by_text(rpc_without_https).click()
            else:
                await self.page.get_by_role('button', name='Add RPC URL').click()
                await self.page.get_by_test_id('rpc-url-input-test').fill(chain.rpc)
                await self.page.get_by_role('button', name='Add URL').click()

        if await self.page.get_by_test_id('network-form-ticker-input').get_attribute('value') != chain.native_token:
            await self.page.get_by_test_id('network-form-ticker-input').fill(chain.native_token)

        await self.page.get_by_role('button', name='Save').or_(
            self.page.get_by_role('button', name='Сохранить')).click()
        logger.info(
            f'{self.profile_number}: Данные сети {chain.metamask_name} успешно изменены')


class MetamaskExcel(Metamask):
    def __init__(self, excel: Excel, **kwargs):
        Metamask.__init__(self, **kwargs)
        self.excel = excel

    async def reg_new_and_write_to_excel(self):
        if self.seed:
            raise MetamaskCreateException(
                f'Ошибка создания кошелька. В таблице уже есть Seed. Полфиль #{self.profile_number}')

        address, seed, password = await self.create_wallet()
        self.excel.set_cell('Address', address)
        self.excel.set_cell('Seed', seed)
        self.excel.set_cell('Password', password)

    async def auth_or_import_or_reg(self):
        try:
            await self.auth_metamask()
        except Exception as err:
            logger.warning(err)
            if self.seed:
                await self.import_wallet()
            else:
                await self.reg_new_and_write_to_excel()
