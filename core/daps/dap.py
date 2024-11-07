from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from models.token import Token
from models.amount import Amount

if TYPE_CHECKING:
    from core.onchain import Onchain


class Dap:

    def __init__(self, onchain: Onchain):
        self.onchain = onchain

    def swap(self, src_token: Token, dst_token: Token, amount: Amount | int | float) -> Optional[str]:
        pass