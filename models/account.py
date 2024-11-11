from typing import Optional


class Account:
    def __init__(
            self,
            profile_number: int,
            password: Optional[str] = None,
            private_key: Optional[str] = None,
            seed: Optional[str] = None,
            proxy: Optional[str] = None
    ) -> None:
        self.profile_number = profile_number
        self.private_key = private_key
        self.password = password
        self.seed = seed
        self.proxy = proxy