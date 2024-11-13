from loguru import logger
from playwright.sync_api import Locator

from core.ads.ads import Ads
from config import config
from models.account import Account
from models.chain import Chain
from utils.utils import random_sleep, generate_password, write_text_to_file


class Metamask:
    def __init__(self, ads: Ads, account: Account):
        self._url = config.metamask_url
        self.ads = ads
        self.password = account.password
        self.seed = account.seed

    def open_metamask(self):
        """
        Открывает metamask
        :return:
        """
        self.ads.open_url(self._url)

    def create_wallet(self):
        """
        Создает кошелек в metamask
        :return:
        """
        self.open_metamask()
        self.ads.page.get_by_test_id('onboarding-terms-checkbox').click()
        self.ads.page.get_by_test_id('onboarding-create-wallet').click()
        self.ads.page.get_by_test_id('metametrics-no-thanks').click()

        # генерируем пароль и вводим в 2 поля
        if not self.password:
            self.password = generate_password()
        self.ads.page.get_by_test_id('create-password-new').fill(self.password)
        self.ads.page.get_by_test_id('create-password-confirm').fill(self.password)
        self.ads.page.get_by_test_id('create-password-terms').click()
        self.ads.page.get_by_test_id('create-password-wallet').click()

        self.ads.page.get_by_test_id('secure-wallet-recommended').click()
        self.ads.page.get_by_test_id('recovery-phrase-reveal').click()

        seed = []
        for i in range(12):
            test_id = f"recovery-phrase-chip-{i}"
            word = self.ads.page.get_by_test_id(test_id).inner_text()
            seed.append(word)

        self.ads.page.get_by_test_id('recovery-phrase-next').click()
        for i in range(12):
            if self.ads.page.get_by_test_id(f'recovery-phrase-input-{i}').count():
                self.ads.page.get_by_test_id(f'recovery-phrase-input-{i}').fill(seed[i])
        self.ads.page.get_by_test_id('recovery-phrase-confirm').click()
        random_sleep(3, 5)
        self.ads.page.get_by_test_id('onboarding-complete-done').click()
        self.ads.page.get_by_test_id('pin-extension-next').click()
        self.ads.click_if_exists(method='test_id', value='pin-extension-done')
        random_sleep(3, 3)
        self.ads.click_if_exists(method='test_id', value='popover-close')

        address = self.get_address()

        seed_str = " ".join(seed)

        write_text_to_file("new_wallets.txt",
                           f"{self.ads.profile_number} {address} {self.password} {seed_str}")

    def auth_metamask(self) -> None:
        """
        Открывает страницу расширения метамаск и авторизуется вводя пароль.
        Ссылка на метамаск настраивается в config/settings.py
        Пароль должен быть указан в файле passwords.txt или в excel файле.
        :return: None
        """
        self.open_metamask()
        if not self.password:
            raise Exception(f"{self.ads.profile_number} не указан пароль для авторизации в metamask")

        if self.ads.page.get_by_test_id('unlock-password').count():
            self.ads.page.get_by_test_id('unlock-password').fill(self.password)
            self.ads.page.get_by_test_id('unlock-submit').click()
            random_sleep(3, 5)

            self.ads.click_if_exists(method='test_id', value='popover-close')

        if self.ads.page.get_by_test_id('account-options-menu-button').count():
            logger.info(f"{self.ads.profile_number} успешно авторизован в metamask")
        else:
            logger.error(f"{self.ads.profile_number} ошибка авторизации в metamask")

    def import_wallet(self):
        """
        Импортирует кошелек в metamask
        :return:
        """
        self.open_metamask()

        seed_list = self.seed.split(" ")
        if not self.password:
            self.password = generate_password()

        if self.ads.page.get_by_test_id('onboarding-create-wallet').count():
            self.ads.page.get_by_test_id('onboarding-terms-checkbox').click()
            self.ads.page.get_by_test_id('onboarding-import-wallet').click()
            self.ads.page.get_by_test_id('metametrics-no-thanks').click()
            for i, word in enumerate(seed_list):
                self.ads.page.get_by_test_id(f"import-srp__srp-word-{i}").fill(word)
            self.ads.page.get_by_test_id('import-srp-confirm').click()
            self.ads.page.get_by_test_id('create-password-new').fill(self.password)
            self.ads.page.get_by_test_id('create-password-confirm').fill(self.password)
            self.ads.page.get_by_test_id('create-password-terms').click()
            self.ads.page.get_by_test_id('create-password-import').click()
            random_sleep(3, 5)
            self.ads.page.get_by_test_id('onboarding-complete-done').click()
            self.ads.page.get_by_test_id('pin-extension-next').click()
            self.ads.click_if_exists(method='test_id', value='pin-extension-done')

        else:
            self.ads.page.get_by_text('Forgot password?').click()
            for i, word in enumerate(seed_list):
                self.ads.page.get_by_test_id(f"import-srp__srp-word-{i}").fill(word)
            self.ads.page.get_by_test_id('create-vault-password').fill(self.password)
            self.ads.page.get_by_test_id('create-vault-confirm-password').fill(self.password)
            self.ads.page.get_by_test_id('create-new-vault-submit-button').click()

        random_sleep(3, 3)
        self.ads.click_if_exists(method='test_id', value='popover-close')
        address = self.get_address()
        seed_str = " ".join(seed_list)
        write_text_to_file("new_wallets.txt",
                           f"{self.ads.profile_number} {address} {self.password} {seed_str}")

    def get_address(self) -> str:
        """
        Возвращает адрес кошелька
        :return: адрес кошелька
        """
        self.ads.page.get_by_test_id('account-options-menu-button').click()
        self.ads.page.get_by_test_id('account-list-menu-details').click()
        address = self.ads.page.get_by_test_id('address-copy-button-text').inner_text()
        self.ads.page.get_by_role('button', name='Close').first.click()
        return address

    def connect(self, locator: Locator, timeout: int = 30) -> None:
        """
        Подтверждает подключение к metamask.
        :param locator: локатор кнопки подключения, после нажатия которой появляется окно метамаска.
        :return: None
        """

        try:
            with self.ads.context.expect_page(timeout=timeout) as page_catcher:
                locator.click()
            metamask_page = page_catcher.value
        except:
            metamask_page = self.ads.catch_page(['connect', 'confirm-transaction'])
            if not metamask_page:
                raise Exception(f"Error: {self.ads.profile_number} Ошибка подключения метамаска")

        metamask_page.wait_for_load_state('load')

        confirm_button = metamask_page.get_by_test_id('page-container-footer-next')
        if not confirm_button.count():
            confirm_button = metamask_page.get_by_test_id('confirm-footer-button')

        confirm_button.click()
        random_sleep(1, 3)
        if not metamask_page.is_closed():
            confirm_button.click()

    def sign(self, locator: Locator, timeout: int = 30) -> None:
        """
        Подтверждает подпись в metamask.
        :param locator: локатор кнопки вызова подписи.
        :return: None
        """
        try:
            with self.ads.context.expect_page(timeout=timeout) as page_catcher:
                locator.click()
            metamask_page = page_catcher.value
        except:
            metamask_page = self.ads.catch_page(['confirm-transaction'])
            if not metamask_page:
                raise Exception(f"Error: {self.ads.profile_number} Ошибка подписи сообщения в метамаске)")

        metamask_page.wait_for_load_state('load')

        confirm_button = metamask_page.get_by_test_id('page-container-footer-next')
        if not confirm_button.count():
            confirm_button = metamask_page.get_by_test_id('confirm-footer-button')

        confirm_button.click()

    def send_tx(self, locator: Locator, timeout: int = 30) -> None:
        """
        Подтверждает отправку транзакции в metamask.
        :param locator: локатор кнопки вызова транзакции
        :param timeout: время ожидания в секундах, по умолчанию 30
        :return None
        """
        try:
            with self.ads.context.expect_page(timeout=timeout) as page_catcher:
                locator.click()
            metamask_page = page_catcher.value
        except:
            metamask_page = self.ads.catch_page(['confirm-transaction'])
            if not metamask_page:
                raise Exception(f"Error: {self.ads.profile_number} Ошибка подтверждения транзакции метамаска")

        metamask_page.wait_for_load_state('load')

        confirm_button = metamask_page.get_by_test_id('page-container-footer-next')
        if not confirm_button.count():
            confirm_button = metamask_page.get_by_test_id('confirm-footer-button')

        confirm_button.click()

    def select_chain(self, chain: Chain) -> None:
        """
        Выбирает сеть в metamask.
        :param chain: объект сети
        :return: None
        """
        self.open_metamask()
        chain_button = self.ads.page.get_by_test_id("network-display")
        if chain.name in chain_button.inner_text():
            return
        chain_button.click()
        random_sleep(1, 3)

        if self.ads.page.get_by_text(chain.name).count():
            self.ads.page.get_by_text(chain).click()
        else:
            self.ads.page.get_by_role('button', name='Close').first.click()
            self.set_chain(chain)

    def set_chain(self, chain: Chain) -> None:
        """
        Добавляет новую сеть в metamask
        :param chain: объект сети
        :return: None
        """
        self.ads.open_url(self._url + "#settings/networks/add-network")
        random_sleep(1, 3)
        self.ads.page.get_by_test_id('network-form-network-name').fill(chain.name)
        self.ads.page.get_by_test_id('network-form-rpc-url').fill(chain.rpc)
        self.ads.page.get_by_test_id('network-form-chain-id').fill(str(chain.chain_id))
        self.ads.page.get_by_test_id('network-form-ticker-input').fill(chain.native_token)
        random_sleep(1, 3)
        self.ads.page.get_by_role('button', name='Save').or_(
            self.ads.page.get_by_role('button', name='Сохранить')).click()
        self.ads.page.get_by_role('heading', name='Switch to').or_(
            self.ads.page.get_by_role('button', name='Сменить на')).click()
