import time
from pathlib import Path

from camoufox.sync_api import Camoufox

from config.settings import config

with Camoufox(
        addons=[
            str(Path(config.camfox_profiles_dir, 'addons', 'ether_metamask-12.9.3'))
        ],
        window=(1920, 1080),
        geoip=True,
        proxy={
            'server': 'http://198.23.239.134:6540',
            'username': 'puxtbrxz',
            'password': 'tdym3r4xte8q'
        },
        persistent_context=True,
        user_data_dir=config.camfox_profiles_dir / Path('2'),
) as browser:
    page = browser.new_page()
    page.goto("https://www.browserscan.net")
    time.sleep(5000)
