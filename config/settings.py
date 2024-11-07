import os

import dotenv
from dotenv import load_dotenv

from models.patterns import Singleton


class Config(Singleton):
    load_dotenv()

    # откуда брать аккаунты
    accounts_source = 'excel'  # txt, excel

    date_format = '%d/%m/%Y %H:%M:%S'

    is_random = True

    pause_between_profile = [10, 20]

    cycle = 10  # укажите сколько раз прокрутить все аккаунты, ставьте -1 если бесконечно

    set_proxy = False
    check_proxy = False
    is_mobile_proxy = False
    link_change_ip = ""

    metamask_url = "chrome-extension://nkbihfbeogaeaoehlefnkodbefgpgknn/home.html"

    bot_token = os.getenv("BOT_TOKEN")
    chat_id = '12345678'

    okx_api_key_main = os.getenv("OKX_API_KEY_MAIN")
    okx_secret_key_main = os.getenv("OKX_SECRET_KEY_MAIN")
    okx_passphrase_main = os.getenv("OKX_PASSPHRASE_MAIN")

    DEFAULT_TIMEOUT = 360
    PATH_CONFIG = os.path.join(os.getcwd(), 'config')
    PATH_DATA = os.path.join(PATH_CONFIG, "data")
    PATH_ABI = os.path.join(PATH_DATA, "ABIs")
    PATH_LOG = os.path.join(os.getcwd(), "logs")
    PATH_EXCEL = os.path.join(PATH_DATA, "accounts.xlsx")


config = Config()
