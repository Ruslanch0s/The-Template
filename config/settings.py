import os

from dotenv import load_dotenv

from config.chains import Chains
from models.patterns import Singleton


class Config(Singleton):
    load_dotenv()  # загрузка переменных окружения из файла .env

    # откуда брать аккаунты
    accounts_source = 'excel'  # txt, excel

    # type work
    is_browser_run = False  # Запускать браузер

    # формат даты в excel, не меняйте если не знаете что делаете
    date_format = '%d/%m/%Y %H:%M:%S'

    # случайный порядок аккаунтов
    is_random = False  # Если True, то аккаунты будут выбираться случайно, иначе по порядку

    # пауза между запуском профилей в секундах от и до
    pause_between_profile = [10, 20]

    # укажите сколько раз прокрутить все аккаунты
    cycle = 10000

    # нужно ли устанавливать прокси в профиль ADS
    set_proxy = False
    # нужно ли проверять прокси перед использованием
    check_proxy = False
    # поставьте True, если используете мобильный прокси
    is_mobile_proxy = False
    # адрес для запроса смены ip адреса мобильного прокси
    link_change_ip = ""

    # в какой сети работает в ончейн (не относится к метамаску)
    start_chain = Chains.ETHEREUM

    # id чата в телеграме, куда отправлять сообщения
    chat_id = '12345678'

    # адрес расширения в браузере ADS
    metamask_url = "chrome-extension://nkbihfbeogaeaoehlefnkodbefgpgknn/home.html"

    # ниже системные переменные, не меняйте их

    bot_token = os.getenv("BOT_TOKEN")

    DEFAULT_TIMEOUT = 360  # таймаут выполнения активности, пока не реализовано

    okx_api_key_main = os.getenv("OKX_API_KEY_MAIN")
    okx_secret_key_main = os.getenv("OKX_SECRET_KEY_MAIN")
    okx_passphrase_main = os.getenv("OKX_PASSPHRASE_MAIN")

    PATH_CONFIG = os.path.join(os.getcwd(), 'config')
    PATH_DATA = os.path.join(PATH_CONFIG, "data")
    PATH_ABI = os.path.join(PATH_DATA, "ABIs")
    PATH_LOG = os.path.join(os.getcwd(), "logs")
    PATH_EXCEL = os.path.join(PATH_DATA, "accounts.xlsx")


config = Config()
