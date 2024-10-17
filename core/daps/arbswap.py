from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from loguru import logger

from config import Tokens
from config.contracts import Contracts
from models import Token, Amount, TokenTypes

if TYPE_CHECKING:
    from core.onchain import Onchain


class Arbswap:

    def __init__(self, onchain: Onchain):
        self.onchain = onchain

    def swap(self, src_token: Token, dst_token: Token, amount: Amount | int | float) -> Optional[str]:
        """
        Обмен через arbswap
        :param src_token: токен из которого делаем обмен
        :param dst_token: токен в который делаем обмен
        :param amount: сумма обмена
        :return: хэш транзакции
        """
        # приводим сумму к объекту Amount
        if isinstance(amount, (int, float)):
            amount = Amount(amount, decimals=src_token.decimals)

        balance = self.onchain.get_balance(src_token)

        if balance.wei < amount.wei:
            print(f'Not enough balance: {balance.ether_float} {src_token.symbol}')
            return

        self.onchain.approve(src_token, amount, Contracts.ARBSWAP_UNI_ROUTER)

        if src_token.type == TokenTypes.STABLE and dst_token.type == TokenTypes.STABLE:
            tx = self._build_stable_swap(src_token, dst_token, amount)
        else:
            tx = self._build_swap_tx(src_token, dst_token, amount)

        hash = self.onchain.sing_and_send(tx)
        message = f'swap {amount.ether_float} {src_token.symbol} to {dst_token.symbol}'
        logger.info(f'Транзакция отправлена {message} tx hash: {hash}')
        return hash

    def _build_stable_swap(self, src_token: Token, dst_token: Token, amount: Amount | int | float) -> \
            Optional[dict]:
        """
        Построение транзакции обмена стейблкоинов
        :param src_token: исходный стейблкоин
        :param dst_token: целевой стейблкоин
        :param amount: сумма обмена
        :return: параметры транзакции
        """

        min_return = Amount(amount.wei * 0.95, decimals=dst_token.decimals, wei=True)
        # подготавливаем транзакцию
        tx_params = self.onchain.prepare_tx()
        contract = self.onchain.get_contract(Contracts.ARBSWAP_UNI_ROUTER)
        tx = contract.functions.swap(
            src_token.address,
            dst_token.address,
            amount.wei,
            min_return.wei,
            0
        ).build_transaction(tx_params)
        return tx

    def _build_swap_tx(self, src_token: Token, dst_token: Token, amount: Amount | int | float) -> Optional[
        str]:
        """
        Построение транзакции обмена токенов
        :param src_token: исходный токен
        :param dst_token: целевой токен
        :param amount: сумма обмена
        :return: параметры транзакции
        """
        # подменяем ETH на WETH для поиска пула ликвидности
        _src_token = self.onchain.replace_eth_to_weth(src_token)
        _dst_token = self.onchain.replace_eth_to_weth(dst_token)

        # получаем адрес пула ликвидности
        swap_factory_contract = self.onchain.get_contract(Contracts.ARBSWAP_SWAP_FACTORY)
        pool_contract_address = swap_factory_contract.functions.getPair(
            _src_token.address,
            _dst_token.address
        ).call()

        # получаем резервы пула ликвидности и считаем цену обмена
        pool_contract = self.onchain.get_contract(contract_address=pool_contract_address,
                                                  abi_name='arbswap_swap_pair')
        reserve0, reserve1, _ = pool_contract.functions.getReserves().call()
        if int(_src_token.address, 16) > int(_dst_token.address, 16):
            reserve0, reserve1 = reserve1, reserve0
        change_price = reserve1 / reserve0
        amount_out = amount.wei * change_price * 0.947
        min_return = Amount(amount_out, decimals=dst_token.decimals, wei=True)

        # подготавливаем транзакцию
        tx_params = self.onchain.prepare_tx(value=amount if src_token == Tokens.ETH else None)
        contract = self.onchain.get_contract(Contracts.ARBSWAP_UNI_ROUTER)
        tx = contract.functions.swap(
            src_token.address,
            dst_token.address,
            amount.wei,
            min_return.wei,
            1
        ).build_transaction(tx_params)
        return tx
