import time

from core.bot import Bot
from models.chain import Chain

from utils.utils import random_sleep


class Reddio:
    def __init__(self, bot: Bot):
        self.bot = bot

    def _set_network(self):
        chain = Chain(
            name='RED',
            rpc='https://reddio-dev.reddio.com',
            chain_id=50341,
            metamask_name='Reddio Devnet',
            explorer_url='reddio-devnet.l2scan.co'
        )
        self.bot.metamask.select_chain(chain=chain)

    def _connect_wallet(self):
        connect_button = (self.bot.ads.page.wait_for_selector(
            'xpath=/html/body/div[1]/div/main/div/div[9]/div/div/div[1]/div[1]/button',
            timeout=1000))
        connect_button.click()
        locator_metamask = self.bot.ads.page.locator(
            'xpath=/html/body/div[2]/div/div/div[2]/div/div/div/div/div[1]/div[2]/div[2]/div[3]')
        self.bot.metamask.connect(locator=locator_metamask)

    def check_login(self):
        self.bot.ads.open_url('https://testnet.reddio.com/')
        connect_button = self.bot.ads.page.wait_for_selector(
            'xpath=/html/body/div[1]/div/main/div/div[9]/div/div/div[1]/div[1]/button',
            timeout=1000)
        text_button = connect_button.inner_text()
        if text_button == 'Added':
            return True

    def start(self):
        if not self.check_login():
            self._set_network()
            self._connect_wallet()
        if not self.check_login():
            return

        random_sleep(1, 3)
        self.bot.ads.page.wait_for_selector(
            'xpath=/html/body/div[1]/div/main/div/div[9]/div/div/div[1]/div[2]/button',
            timeout=1000
        ).click()


        print('GOOO')
        time.sleep(1000)
