from pathlib import Path

from camoufox import Camoufox

from config import config


class CustomCamoufox(Camoufox):
    def __init__(
            self,
            profile_number: int,

            proxy_ip: str,
            proxy_port: str,
            proxy_login: str,
            proxy_password: str,

            addons: list[str] = None
    ):
        Camoufox.__init__(
            self,
            addons=[str(Path(config.camfox_profiles_dir, 'addons', addon)) for addon in addons] if addons else [],
            window=(1920, 1080),
            geoip=True,
            proxy={
                'server': f'http://{proxy_ip}:{proxy_port}',
                'username': proxy_login,
                'password': proxy_password
            },
            humanize=True,
            persistent_context=True,
            user_data_dir=Path(config.camfox_profiles_dir, str(profile_number)),
        )
