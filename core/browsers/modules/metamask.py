import time

from loguru import logger
from playwright.sync_api import Locator

from config import config
from core.browsers.ads import Ads
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

    def open_metamask(self):
        """
        Открывает metamask, ждет появления кнопок подтверждающих прогрузку страницы.
        :return:
        """
        self.ads.open_url(self._url)
        time.sleep(1)

    def create_wallet(self) -> tuple[str, str, str]:
        """
        Создает кошелек в metamask, возвращает адрес кошелька, seed фразу и пароль в виде кортежа.
        :return: tuple (address, seed, password)
        """
        self.open_metamask()
        try:
            self.ads.page.get_by_test_id('onboarding-terms-checkbox').wait_for(
                timeout=5000, state='visible')
        except:
            raise Exception(
                f"Ошибка создания кошелька {self.ads.profile_number} вероятно в метамаске уже есть счет, обнулите расширение")

        self.ads.page.get_by_test_id('onboarding-terms-checkbox').click()
        self.ads.page.get_by_test_id('onboarding-create-wallet').click()
        self.ads.page.get_by_test_id('metametrics-no-thanks').click()

        # генерируем пароль и вводим в 2 поля
        if not self.password:
            self.password = generate_password()
        self.ads.page.get_by_test_id('create-password-new').fill(self.password)
        self.ads.page.get_by_test_id('create-password-confirm').fill(
            self.password)
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
            if self.ads.page.get_by_test_id(
                    f'recovery-phrase-input-{i}').count():
                self.ads.page.get_by_test_id(
                    f'recovery-phrase-input-{i}').fill(seed[i])
        self.ads.page.get_by_test_id('recovery-phrase-confirm').click()
        time.sleep(1)
        self.ads.page.get_by_test_id('onboarding-complete-done').click()
        self.ads.page.get_by_test_id('pin-extension-next').click()
        self.ads.click_if_exists(method='test_id', value='pin-extension-done')
        time.sleep(1)
        self.ads.click_if_exists(method='test_id', value='popover-close')

        address = self.get_address()

        seed_str = " ".join(seed)

        return address, seed_str, self.password

    def auth_metamask(self) -> None:
        """
        Открывает страницу расширения метамаск и авторизуется вводя пароль.
        Ссылка на метамаск настраивается в config/settings.py
        Пароль должен быть указан в файле passwords.txt или в excel файле.
        :return: None
        """
        self.open_metamask()
        if not self.password:
            raise Exception(
                f"{self.ads.profile_number} не указан пароль для авторизации в metamask")

        try:
            self.ads.page.get_by_test_id('unlock-password').wait_for(
                timeout=5000, state='visible')
            self.ads.page.get_by_test_id('unlock-password').fill(self.password)
            self.ads.page.get_by_test_id('unlock-submit').click()
            time.sleep(1)
            self.ads.click_if_exists(method='test_id', value='popover-close')
        except:
            logger.warning(
                f"{self.ads.profile_number} не смогли авторизоваться в metamask, вероятно уже авторизованы")

        if self.ads.page.get_by_test_id('account-options-menu-button').count():
            logger.info(
                f"{self.ads.profile_number} успешно авторизован в metamask")
        else:
            logger.error(
                f"{self.ads.profile_number} ошибка авторизации в metamask, не смогли войти в кошелек")

    def import_wallet(self) -> tuple[str, str, str]:
        """
        Импортирует кошелек в metamask, используя seed фразу. Возвращает адрес кошелька и пароль в виде кортежа.
        :return: tuple (address, seed, password)
        """
        self.open_metamask()

        seed_list = self.seed.split(" ")
        if not self.password:
            self.password = generate_password()
        try:
            self.ads.page.get_by_test_id('onboarding-create-wallet').wait_for(
                timeout=5000, state='visible')
            self.ads.page.get_by_test_id('onboarding-terms-checkbox').click()
            self.ads.page.get_by_test_id('onboarding-import-wallet').click()
            self.ads.page.get_by_test_id('metametrics-no-thanks').click()
            for i, word in enumerate(seed_list):
                self.ads.page.get_by_test_id(f"import-srp__srp-word-{i}").fill(
                    word)
            self.ads.page.get_by_test_id('import-srp-confirm').click()
            self.ads.page.get_by_test_id('create-password-new').fill(
                self.password)
            self.ads.page.get_by_test_id('create-password-confirm').fill(
                self.password)
            self.ads.page.get_by_test_id('create-password-terms').click()
            self.ads.page.get_by_test_id('create-password-import').click()
            time.sleep(1)
            self.ads.page.get_by_test_id('onboarding-complete-done').click()
            self.ads.page.get_by_test_id('pin-extension-next').click()
            self.ads.click_if_exists(method='test_id',
                                     value='pin-extension-done')
        except:
            logger.warning(
                f"{self.ads.profile_number} в метамаске уже имеется счет, делаем сброс и импортируем новый")
            self.ads.page.get_by_text('Forgot password?').click()
            for i, word in enumerate(seed_list):
                self.ads.page.get_by_test_id(f"import-srp__srp-word-{i}").fill(
                    word)
            self.ads.page.get_by_test_id('create-vault-password').fill(
                self.password)
            self.ads.page.get_by_test_id('create-vault-confirm-password').fill(
                self.password)
            self.ads.page.get_by_test_id(
                'create-new-vault-submit-button').click()

        time.sleep(1)
        self.ads.click_if_exists(method='test_id', value='popover-close')
        address = self.get_address()
        seed_str = " ".join(seed_list)
        return address, seed_str, self.password

    def get_address(self) -> str:
        """
        Возвращает адрес кошелька
        :return: адрес кошелька
        """
        self.ads.page.get_by_test_id('account-options-menu-button').click()
        self.ads.page.get_by_test_id('account-list-menu-details').click()
        address = self.ads.page.locator(
            '.qr-code__address-segments').inner_text().replace('\n', '')
        # self.ads.page.get_by_role('button', name='Close').first.click()
        return address

    def connect(self, locator: Locator, timeout: int = 30) -> None:
        """
        Подтверждает подключение к metamask.
        :param locator: локатор кнопки подключения, после нажатия которой появляется окно метамаска.
        :return: None
        """
        try:
            with self.ads.context.expect_page(
                    timeout=timeout * 1000) as page_catcher:
                locator.click()
            metamask_page = page_catcher.value
        except Exception as e:
            logger.warning(
                f"{self.ads.profile_number} Wargning: не смогли поймать окно метамаск, пробуем еще {e}")
            metamask_page = self.ads.catch_page(
                ['notification', 'connect', 'confirm-transaction'])
            if not metamask_page:
                raise Exception(
                    f"Error: {self.ads.profile_number} Ошибка подключения метамаска")

        metamask_page.wait_for_load_state('load')

        metamask_page.get_by_test_id('confirm-btn').click()

    def sign(self, locator: Locator, timeout: int = 30) -> None:
        """
        Подтверждает подпись в metamask.
        :param locator: локатор кнопки вызова подписи.
        :return: None
        """
        try:
            with self.ads.context.expect_page(
                    timeout=timeout * 1000) as page_catcher:
                locator.click()
            metamask_page = page_catcher.value
        except:
            metamask_page = self.ads.catch_page(['confirm-transaction'])
            if not metamask_page:
                raise Exception(
                    f"Error: {self.ads.profile_number} Ошибка подписи сообщения в метамаске)")

        metamask_page.wait_for_load_state('load')

        confirm_button = metamask_page.get_by_test_id(
            'page-container-footer-next')
        if not confirm_button.count():
            confirm_button = metamask_page.get_by_test_id(
                'confirm-footer-button')

        confirm_button.click()

    def send_tx(self, locator: Locator, timeout: int = 30) -> None:
        """
        Подтверждает отправку транзакции в metamask.
        :param locator: локатор кнопки вызова транзакции
        :param timeout: время ожидания в секундах, по умолчанию 30
        :return None
        """
        try:
            with self.ads.context.expect_page(
                    timeout=timeout * 1000) as page_catcher:
                locator.click()
            metamask_page = page_catcher.value
        except:
            metamask_page = self.ads.catch_page(
                ['notification', 'confirm-transaction'])
            if not metamask_page:
                raise Exception(
                    f"Error: {self.ads.profile_number} Ошибка подтверждения транзакции метамаска")

        metamask_page.wait_for_load_state('load')
        confirm_button = metamask_page.get_by_test_id('confirm-footer-button')
        if not confirm_button.count():
            confirm_button = metamask_page.get_by_test_id(
                'page-container-footer-next')

        confirm_button.click()

    def select_chain(self, chain: Chain) -> None:
        """
        Выбирает сеть в metamask. Если сеть не найдена, добавляет новую из параметра chain
        :param chain: объект сети Chain
        :return: None
        """
        self.open_metamask()
        self.ads.page.get_by_test_id("network-display").wait_for(timeout=5000,
                                                                 state='visible')
        chain_button = self.ads.page.get_by_test_id("network-display")
        if chain.metamask_name == chain_button.inner_text():
            return

        chain_button.click()
        time.sleep(1)
        enabled_networks = self.ads.page.locator(
            'div[data-rbd-droppable-id="characters"]')
        if enabled_networks.get_by_text(chain.metamask_name,
                                        exact=True).count():
            enabled_networks.get_by_text(chain.metamask_name,
                                         exact=True).click()
        else:
            close_button = self.ads.page.wait_for_selector(
                'xpath=/html/body/div[3]/div[3]/div/section/header/div[2]/button',
                timeout=1000
            )
            close_button.click()
            self.set_chain(chain)
            self.select_chain(chain)

    def set_chain(self, chain: Chain) -> None:
        """
        Добавляет новую сеть в metamask. Берет параметры из объекта Chain.
        :param chain: объект сети
        :return: None
        """
        self.ads.open_url(self._url + "#settings/networks/add-network")
        time.sleep(1)
        self.ads.page.get_by_test_id('network-form-network-name').wait_for(
            timeout=5000, state='visible')
        self.ads.page.get_by_test_id('network-form-network-name').fill(
            chain.metamask_name)
        self.ads.page.get_by_test_id('test-add-rpc-drop-down').click()
        self.ads.page.wait_for_selector(
            'xpath=/html/body/div[3]/div[3]/div/section/div/div[1]/div[2]/div[2]',
            timeout=1000
        ).click()
        self.ads.page.get_by_test_id('rpc-url-input-test').fill(chain.rpc)
        self.ads.page.wait_for_selector(
            'xpath=/html/body/div[3]/div[3]/div/section/div/div[2]/button',
            timeout=1000
        ).click()
        if self.ads.page.get_by_test_id('network-form-chain-id-error').count():
            raise Exception(
                f"Error: {self.ads.profile_number} metamask не принимает rpc {chain.rpc}, попробуйте другой")
        # todo: проверить ошибку на этапе повторного добавления сети
        self.ads.page.get_by_test_id('network-form-chain-id').fill(
            str(chain.chain_id))
        self.ads.page.get_by_test_id('network-form-ticker-input').fill(
            chain.native_token)
        # self.ads.page.get_by_test_id('test-explorer-drop-down').click()
        # self.ads.page.wait_for_selector(
        #     'xpath=/html/body/div[3]/div[3]/div/section/div/div[1]/div[5]/div[2]/div/div/button',
        #     timeout=1000
        # ).click()
        # self.ads.page.get_by_test_id('explorer-url-input').fill(
        #     chain.explorer_url)
        # '/html/body/div[3]/div[3]/div/section/div/div[2]/button'

        self.ads.page.wait_for_selector(
            'xpath=/html/body/div[3]/div[3]/div/section/div/div[2]/button',
            timeout=1000
        ).click()

    def change_chain_data(self, chain: Chain) -> None:
        """
        Меняет параметры сети в Metamask. Берет данные из объекта Chain.

        :param chain: объект сети с параметрами:
            - metamask_name (str): Имя сети в Metamask.
            - chain_id (int): Идентификатор сети (целое число).
            - rpc (str): URL RPC-сервера для подключения.
            - native_token (str): Тикер нативного токена сети.
        :return: None
        """
        self.open_metamask()
        self.ads.page.get_by_test_id('network-display').click()

        # Преобразуем chain_id в шестнадцатеричное число для упрощения поиска элемента
        hex_id = hex(chain.chain_id)

        # Находим нужную сеть и открываем настройки
        if not self.ads.page.get_by_test_id(
                f'network-list-item-options-button-{hex_id}').count():
            logger.info(
                f'{self.ads.profile_number} Сеть {chain.metamask_name} не найдена в списке установленных. Устанавливаем.')
            self.ads.page.get_by_role('button', name='Close').first.click()
            self.set_chain(chain)
            return

        self.ads.page.get_by_test_id(
            f'network-list-item-options-button-{hex_id}').click()
        self.ads.page.get_by_test_id('network-list-item-options-edit').click()

        # Если имя не совпадает с chain.metamask_name, меняем
        if self.ads.page.get_by_test_id(
                'network-form-network-name').get_attribute(
            'value') != chain.metamask_name:
            self.ads.page.get_by_test_id('network-form-network-name').fill(
                chain.metamask_name)

        # Если rpc не совпадает с chain.rpc, меняем
        rpc_element = self.ads.page.locator(
            '//button[@data-testid="test-add-rpc-drop-down"]/../..')
        if rpc_element.get_attribute('data-original-title') != chain.rpc:
            rpc_element.click()
            # Чтобы rpc находилось в списке, убираем "https://"
            rpc_without_https = chain.rpc.replace('https://', '')
            if self.ads.page.get_by_role('tooltip').get_by_text(
                    rpc_without_https).count():
                self.ads.page.get_by_role('tooltip').get_by_text(
                    rpc_without_https).click()
            else:
                self.ads.page.get_by_role('button', name='Add RPC URL').click()
                self.ads.page.get_by_test_id('rpc-url-input-test').fill(
                    chain.rpc)
                self.ads.page.get_by_role('button', name='Add URL').click()

        # Если токен не совпадает с chain.native_token, меняем
        if self.ads.page.get_by_test_id(
                'network-form-ticker-input').get_attribute(
            'value') != chain.native_token:
            self.ads.page.get_by_test_id('network-form-ticker-input').fill(
                chain.native_token)

        # Сохраняем изменения
        self.ads.page.get_by_role('button', name='Save').or_(
            self.ads.page.get_by_role('button', name='Сохранить')).click()
        logger.info(
            f'{self.ads.profile_number} Данные сети {chain.metamask_name} успешно изменены')
