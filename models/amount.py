from __future__ import annotations

from decimal import Decimal

from web3.types import Wei


class Amount:
    wei: int | Wei
    ether: Decimal
    ether_float: float

    def __init__(self, amount: int | float | Decimal | Wei, decimals: int = 18, wei: bool = False):
        if wei:
            self.wei = int(amount)
            self.ether = Decimal(str(amount)) / 10 ** decimals
            self.ether_float = float(self.ether)
        else:
            self.wei = int(amount * 10 ** decimals)
            self.ether = Decimal(str(amount))
            self.ether_float = float(self.ether)

        self.decimals = decimals

