import pathlib

import keyring
from models.patterns import Singleton


class Config(Singleton):
    okx_api_key_main = keyring.get_password("okx_api_key", "main")
    okx_secret_key_main = keyring.get_password("okx_secret_key", "main")
    okx_passphrase_main = keyring.get_password("okx_passphrase", "main")

    set_proxy = False
    check_proxy = False
    is_mobile_proxy = False
    link_change_ip = ""

    metamask_url = "chrome-extension://nkbihfbeogaeaoehlefnkodbefgpgknn/home.html"
    excel_path = "path"

    PATH_TO_CONFIG = pathlib.Path(__file__).parent
    PATH_TO_DATA = PATH_TO_CONFIG / "data"
    PATH_TO_ABI = PATH_TO_DATA / "ABIs"


config = Config()
