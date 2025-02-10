from loguru import logger
from playwright.sync_api import Locator

from config import config
from core.ads.ads import Ads
from models.account import Account
from models.chain import Chain
from utils.utils import generate_password


class Metamask:
    """
    Класс для работы с metamask v. 12.9.3
    """

    def __init__(self, ads: Ads, account: Account):
        self._url = config.metamask_url
        self.ads = ads
        self.password = account.password
        self.seed = account.seed

    def set_language(self):
        logger.info('Попытка установить язык EN')
        self.open_metamask()
        self.ads.page.get_by_test_id('account-options-menu-button').click(timeout=3000)
        self.ads.page.get_by_test_id('global-menu-settings').click(timeout=3000)
        self.ads.page.select_option('select.dropdown__select[data-testid="locale-select"]', value="en", timeout=3000)
        logger.info('Язык установлен')

    def open_metamask(self):
        """
        Открывает metamask, ждет появления кнопок подтверждающих прогрузку страницы.
        """
        self.ads.open_url(self._url, timeout=3000)

    def create_wallet(self) -> tuple[str, str, str]:
        """
        Создает кошелек в metamask, возвращает адрес кошелька, seed фразу и пароль в виде кортежа.
        :return: tuple (address, seed, password)
        """
        self.open_metamask()
        try:
            self.ads.page.get_by_test_id('onboarding-terms-checkbox').wait_for(timeout=3000, state='visible')
        except:
            raise Exception(
                f"Ошибка создания кошелька {self.ads.profile_number} вероятно в метамаске уже есть счет, обнулите расширение")

        self.ads.page.get_by_test_id('onboarding-terms-checkbox').click()
        self.ads.page.get_by_test_id('onboarding-create-wallet').click()
        self.ads.page.get_by_test_id('metametrics-no-thanks').click()

        # Генерируем пароль и вводим в 2 поля
        if not self.password:
            self.password = generate_password()
        self.ads.page.get_by_test_id('create-password-new').fill(self.password, timeout=3000)
        self.ads.page.get_by_test_id('create-password-confirm').fill(self.password, timeout=3000)
        self.ads.page.get_by_test_id('create-password-terms').click(timeout=3000)
        self.ads.page.get_by_test_id('create-password-wallet').click(timeout=3000)

        self.ads.page.get_by_test_id('secure-wallet-recommended').click(timeout=3000)
        self.ads.page.get_by_test_id('recovery-phrase-reveal').click(timeout=3000)

        seed = []
        for i in range(12):
            test_id = f"recovery-phrase-chip-{i}"
            word = self.ads.page.get_by_test_id(test_id).inner_text(timeout=3000)
            seed.append(word)

        self.ads.page.get_by_test_id('recovery-phrase-next').click(timeout=3000)
        for i in range(12):
            if self.ads.page.get_by_test_id(f'recovery-phrase-input-{i}').count():
                self.ads.page.get_by_test_id(f'recovery-phrase-input-{i}').fill(seed[i], timeout=3000)
        self.ads.page.get_by_test_id('recovery-phrase-confirm').click(timeout=3000)
        self.ads.page.get_by_test_id('onboarding-complete-done').click(timeout=3000)
        self.ads.page.get_by_test_id('pin-extension-next').click(timeout=3000)
        self.ads.click_if_exists(method='test_id', value='pin-extension-done')
        self.ads.click_if_exists(method='test_id', value='popover-close')

        address = self.get_address()
        seed_str = " ".join(seed)

        return address, seed_str, self.password

    def auth_metamask(self) -> None:
        """
        Открывает страницу расширения метамаск и авторизуется вводя пароль.
        Ссылка на метамаск настраивается в config/settings.py
        Пароль должен быть указан в файле passwords.txt или в excel файле.
        """
        if not self.password:
            raise Exception(f"{self.ads.profile_number} не указан пароль для авторизации в metamask")
        self.open_metamask()
        try:
            self.ads.page.get_by_test_id('unlock-password').wait_for(timeout=3000, state='visible')
            self.ads.page.get_by_test_id('unlock-password').fill(self.password, timeout=3000)
            self.ads.page.get_by_test_id('unlock-submit').click(timeout=3000)
            self.ads.click_if_exists(method='test_id', value='popover-close')
            self.ads.page.wait_for_selector(
                'xpath=/html/body/div[2]/div/div/section/div[2]/div/div[2]/div/button',
                timeout=2000
            ).click()
        except Exception as err:
            logger.warning(
                f"{self.ads.profile_number} не смогли авторизоваться в metamask, вероятно уже авторизованы. {err}")

        if self.ads.page.get_by_test_id('account-options-menu-button').count():
            logger.info(f"{self.ads.profile_number} успешно авторизован в metamask")
        else:
            raise Exception(f"{self.ads.profile_number} ошибка авторизации в metamask, не смогли войти в кошелек")

    def import_wallet(self) -> tuple[str, str, str]:
        """
        Импортирует кошелек в metamask, используя seed фразу. Возвращает адрес кошелька и пароль в виде кортежа.
        :return: tuple (address, seed, password)
        """
        logger.info('Попытка импорта кошелька в Metamask')
        self.open_metamask()

        seed_list = self.seed.split(" ")
        if not self.password:
            self.password = generate_password()
        try:
            self.ads.page.get_by_test_id('onboarding-create-wallet').wait_for(timeout=3000, state='visible')
            self.ads.page.get_by_test_id('onboarding-terms-checkbox').click(timeout=3000)
            self.ads.page.get_by_test_id('onboarding-import-wallet').click(timeout=3000)
            self.ads.page.get_by_test_id('metametrics-no-thanks').click(timeout=3000)
            for i, word in enumerate(seed_list):
                self.ads.page.get_by_test_id(f"import-srp__srp-word-{i}").fill(word, timeout=3000)
            self.ads.page.get_by_test_id('import-srp-confirm').click(timeout=3000)
            self.ads.page.get_by_test_id('create-password-new').fill(self.password, timeout=3000)
            self.ads.page.get_by_test_id('create-password-confirm').fill(self.password, timeout=3000)
            self.ads.page.get_by_test_id('create-password-terms').click(timeout=3000)
            self.ads.page.get_by_test_id('create-password-import').click(timeout=3000)
            self.ads.page.get_by_test_id('onboarding-complete-done').click(timeout=3000)
            self.ads.page.get_by_test_id('pin-extension-next').click(timeout=3000)
            self.ads.click_if_exists(method='test_id', value='pin-extension-done')
        except Exception as e:
            logger.warning(
                f"{self.ads.profile_number}: в MetaMask уже имеется счет, делаем сброс и импортируем новый. {e}")
            forgot_password = self.ads.page.wait_for_selector(
                'xpath=/html/body/div[1]/div/div[2]/div/div/div[3]/a',
                timeout=3000
            ).click()
            for i, word in enumerate(seed_list):
                self.ads.page.get_by_test_id(f"import-srp__srp-word-{i}").fill(word, timeout=3000)
            self.ads.page.get_by_test_id('create-vault-password').fill(self.password, timeout=3000)
            self.ads.page.get_by_test_id('create-vault-confirm-password').fill(self.password, timeout=3000)
            self.ads.page.get_by_test_id('create-new-vault-submit-button').click(timeout=3000)

        self.ads.click_if_exists(method='test_id', value='popover-close')
        address = self.get_address()
        seed_str = " ".join(seed_list)
        return address, seed_str, self.password

    def get_address(self) -> str:
        """
        Возвращает адрес кошелька
        :return: адрес кошелька
        """
        self.ads.page.get_by_test_id('account-options-menu-button').click(timeout=3000)
        self.ads.page.get_by_test_id('account-list-menu-details').click(timeout=3000)
        address = self.ads.page.locator('.qr-code__address-segments').inner_text(timeout=3000).replace('\n', '')
        self.ads.page.wait_for_selector(
            'xpath=/html/body/div[3]/div[3]/div/section/header/div[2]/button',
            timeout=3000
        ).click()
        return address

    def connect(self, locator: Locator, timeout: int = 3000) -> None:
        """
        Подтверждает подключение к metamask.
        :param locator: локатор кнопки подключения, после нажатия которой появляется окно метамаска.
        :param timeout: время ожидания в миллисекундах, по умолчанию 3000
        """
        try:
            with self.ads.context.expect_page(timeout=timeout) as page_catcher:
                locator.click(timeout=5000)
            metamask_page = page_catcher.value
        except Exception as e:
            logger.warning(
                f"{self.ads.profile_number}  Wargning: не смогли поймать окно метамаск, пробуем еще {e}")
            metamask_page = self.ads.catch_page(['notification', 'connect', 'confirm-transaction'], timeout=3000)
            if not metamask_page:
                raise Exception(f"Error: {self.ads.profile_number} Ошибка подключения метамаска")

        metamask_page.wait_for_load_state('load', timeout=3000)
        metamask_page.get_by_test_id('confirm-btn').click(timeout=3000)

    def sign(self, locator: Locator, timeout: int = 3000) -> None:
        """
        Подтверждает подпись в metamask.
        :param locator: локатор кнопки вызова подписи.
        :param timeout: время ожидания в миллисекундах, по умолчанию 3000
        """
        try:
            with self.ads.context.expect_page(timeout=timeout) as page_catcher:
                locator.click(timeout=3000)
            metamask_page = page_catcher.value
        except:
            metamask_page = self.ads.catch_page(['confirm-transaction'], timeout=3000)
            if not metamask_page:
                raise Exception(f"Error: {self.ads.profile_number} Ошибка подписи сообщения в метамаске)")

        metamask_page.wait_for_load_state('load', timeout=3000)
        confirm_button = metamask_page.get_by_test_id('page-container-footer-next')
        if not confirm_button.count():
            confirm_button = metamask_page.get_by_test_id('confirm-footer-button')
        confirm_button.click(timeout=3000)

    def send_tx(self, locator: Locator, timeout: int = 3000) -> None:
        """
        Подтверждает отправку транзакции в metamask.
        :param locator: локатор кнопки вызова транзакции
        :param timeout: время ожидания в миллисекундах, по умолчанию 3000
        """
        try:
            with self.ads.context.expect_page(timeout=timeout) as page_catcher:
                locator.click(timeout=5000)
            metamask_page = page_catcher.value
        except:
            metamask_page = self.ads.catch_page(['notification', 'confirm-transaction'], timeout=5000)
            if not metamask_page:
                raise Exception(f"Error: {self.ads.profile_number} Ошибка подтверждения транзакции метамаска")

        metamask_page.wait_for_load_state('load', timeout=5000)
        confirm_button = metamask_page.get_by_test_id('confirm-footer-button')
        if not confirm_button.count():
            confirm_button = metamask_page.get_by_test_id('page-container-footer-next')
        confirm_button.click(timeout=5000)

    def select_chain(self, chain: Chain) -> None:
        """
        Выбирает сеть в metamask. Если сеть не найдена, добавляет новую из параметра chain
        :param chain: объект сети Chain
        """
        self.open_metamask()
        self.ads.page.get_by_test_id("network-display").wait_for(timeout=3000, state='visible')
        chain_button = self.ads.page.get_by_test_id("network-display")
        if chain.metamask_name == chain_button.inner_text(timeout=3000):
            return

        chain_button.click(timeout=3000)
        enabled_networks = self.ads.page.locator('div[data-rbd-droppable-id="characters"]')
        if enabled_networks.get_by_text(chain.metamask_name, exact=True).count():
            enabled_networks.get_by_text(chain.metamask_name, exact=True).click(timeout=3000)
        else:
            self.set_chain(chain)
            self.select_chain(chain)

    def set_chain(self, chain: Chain) -> None:
        """
        Добавляет новую сеть в metamask. Берет параметры из объекта Chain.
        :param chain: объект сети
        """
        self.ads.page.get_by_role('button', name='Add a custom network').click(timeout=3000)
        self.ads.page.get_by_test_id('network-form-network-name').wait_for(timeout=3000, state='visible')
        self.ads.page.get_by_test_id('network-form-network-name').fill(chain.metamask_name, timeout=3000)
        self.ads.page.get_by_test_id('test-add-rpc-drop-down').click(timeout=3000)
        self.ads.page.get_by_role('button', name='Add RPC URL').click(timeout=3000)
        self.ads.page.get_by_test_id('rpc-url-input-test').fill(chain.rpc, timeout=3000)
        self.ads.page.get_by_role('button', name='Add URL').click(timeout=3000)
        if self.ads.page.get_by_test_id('network-form-chain-id-error').count():
            raise Exception(
                f"Error: {self.ads.profile_number} metamask не принимает rpc {chain.rpc}, попробуйте другой")
        self.ads.page.get_by_test_id('network-form-chain-id').fill(str(chain.chain_id), timeout=3000)
        self.ads.page.get_by_test_id('network-form-ticker-input').fill(chain.native_token, timeout=3000)
        self.ads.page.get_by_role('button', name='Save').or_(
            self.ads.page.get_by_role('button', name='Сохранить')).click(timeout=3000)

    def change_chain_data(self, chain: Chain) -> None:
        """
        Меняет параметры сети в Metamask. Берет данные из объекта Chain.
        :param chain: объект сети
        """
        self.open_metamask()
        self.ads.page.get_by_test_id('network-display').click(timeout=3000)

        hex_id = hex(chain.chain_id)
        if not self.ads.page.get_by_test_id(f'network-list-item-options-button-{hex_id}').count():
            logger.info(
                f'{self.ads.profile_number} Сеть {chain.metamask_name} не найдена в списке установленных. Устанавливаем.')
            self.ads.page.wait_for_selector(
                'xpath=/html/body/div[3]/div[3]/div/section/header/div[2]/button',
                timeout=3000
            ).click()
            self.set_chain(chain)
            return

        self.ads.page.get_by_test_id(f'network-list-item-options-button-{hex_id}').click(timeout=3000)
        self.ads.page.get_by_test_id('network-list-item-options-edit').click(timeout=3000)

        if self.ads.page.get_by_test_id('network-form-network-name').get_attribute(
                'value', timeout=3000) != chain.metamask_name:
            self.ads.page.get_by_test_id('network-form-network-name').fill(chain.metamask_name, timeout=3000)

        rpc_element = self.ads.page.locator('//button[@data-testid="test-add-rpc-drop-down"]/../..')
        if rpc_element.get_attribute('data-original-title', timeout=3000) != chain.rpc:
            rpc_element.click(timeout=3000)
            rpc_without_https = chain.rpc.replace('https://', '')
            if self.ads.page.get_by_role('tooltip').get_by_text(rpc_without_https).count():
                self.ads.page.get_by_role('tooltip').get_by_text(rpc_without_https).click(timeout=3000)
            else:
                self.ads.page.get_by_role('button', name='Add RPC URL').click(timeout=3000)
                self.ads.page.get_by_test_id('rpc-url-input-test').fill(chain.rpc, timeout=3000)
                self.ads.page.get_by_role('button', name='Add URL').click(timeout=3000)

        if self.ads.page.get_by_test_id('network-form-ticker-input').get_attribute(
                'value', timeout=3000) != chain.native_token:
            self.ads.page.get_by_test_id('network-form-ticker-input').fill(chain.native_token, timeout=3000)

        self.ads.page.get_by_role('button', name='Save').or_(
            self.ads.page.get_by_role('button', name='Сохранить')).click(timeout=3000)
        logger.info(f'{self.ads.profile_number} Данные сети {chain.metamask_name} успешно изменены')
