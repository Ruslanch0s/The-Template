from __future__ import annotations

import random
from typing import Optional

from eth_typing import ChecksumAddress
from loguru import logger
from web3 import Web3
from web3.contract import Contract

from config.tokens import Tokens
from models.account import Account
from models.token import Token, TokenTypes
from models.chain import Chain
from models.amount import Amount
from models.contract_raw import ContractRaw
from utils.utils import to_checksum


class Onchain:
    def __init__(self, account: Account, chain: Chain):
        self.account = account
        self.chain = chain
        self.w3 = Web3(Web3.HTTPProvider(chain.rpc))
        if self.account.private_key:
            if not self.account.address:
                self.account.address = self.w3.eth.account.from_key(self.account.private_key).address

    def _get_token_params(self, token_address: str | ChecksumAddress) -> tuple[str, int]:
        """
        Получение параметров токена (symbol, decimals) по адресу контракта токена
        :param token_address:  адрес контракта токена
        :return: кортеж (symbol, decimals)
        """
        token_contract_address = to_checksum(token_address)

        if token_contract_address == Tokens.ETH.address.lower():
            return Tokens.ETH.symbol, Tokens.ETH.decimals

        token_contract_raw = ContractRaw(token_contract_address, 'erc20', self.chain)
        token_contract = self._get_contract(token_contract_raw)
        decimals = token_contract.functions.decimals().call()
        symbol = token_contract.functions.symbol().call()
        return symbol, decimals

    def get_balance(
            self,
            token: Optional[Token | str | ChecksumAddress] = None,
            address: Optional[str | ChecksumAddress] = None

    ) -> Amount:
        """
        Получение баланса кошелька в нативных или erc20 токенах, в формате Amount.
        :param token: объект Token или адрес смарт контракта токена, если не указан, то нативный баланс
        :param address: адрес кошелька, если не указан, то берется адрес аккаунта
        :return: объект Amount с балансом
        """

        # если не указан адрес, то берем адрес аккаунта
        if not address:
            address = self.account.address

        # приводим адрес к формату checksum
        address = to_checksum(address)

        # если передан адрес контракта, то получаем параметры токена и создаем объект Token
        if isinstance(token, str):
            symbol, decimals = self._get_token_params(token)
            token = Token(symbol, token, self.chain, decimals)

        # если токен не передан или передан нативный токен
        if token is None or token.type_token == TokenTypes.NATIVE:
            # получаем баланс нативного токена
            balance = Amount(self.w3.eth.get_balance(address), wei=True)
        else:
            # получаем баланс erc20 токена
            contract = self._get_contract(token)
            erc20_balance_wei = contract.functions.balanceOf(address).call()
            balance = Amount(erc20_balance_wei, decimals=token.decimals, wei=True)
        return balance

    def _get_contract(self, contract_raw: ContractRaw) -> Contract:
        """
        Получение инициализированного объекта контракта
        :param contract_raw: объект ContractRaw
        :return: объект контракта
        """
        return self.w3.eth.contract(contract_raw.address, abi=contract_raw.abi)

    def _get_priority_fee(self) -> int:
        """
        Получение приоритетной ставки для транзакции за последние 30 блоков
        :return: приоритетная ставка
        """
        fee_history = self.w3.eth.fee_history(30, 'latest', [20])
        priority_fees = [priority_fee[0] for priority_fee in fee_history['reward']]
        median_index = len(priority_fees) // 2
        priority_fees.sort()
        median_priority_fee = priority_fees[median_index]
        random_multiplier = random.uniform(1.05, 1.1)
        return int(median_priority_fee * random_multiplier)

    def send_token(self,
                   amount: Amount | int | float,
                   to_address: str | ChecksumAddress,
                   token: Optional[Token, str, ChecksumAddress] = None
                   ) -> str:
        """
        Отправка любых типов токенов, если не указан адрес контракта, то отправка нативного токена
        :param amount: сумма перевода, может быть объектом Amount, int или float
        :param to_address: адрес получателя
        :param token: объект Token или адрес контракта токена
        :return: хэш транзакции
        """
        to_address = to_checksum(to_address)
        balance = self.get_balance(token)

        # если не указан токен, то отправляем нативный токен
        if not token:
            token = Tokens.ETH

        # если передан адрес контракта, то получаем параметры токена и создаем объект Token
        if isinstance(token, str):
            symbol, decimals = self._get_token_params(token)
            token = Token(symbol, token, self.chain, decimals)

        multiplier = random.uniform(1.05, 1.1)

        if not isinstance(amount, Amount):
            amount = Amount(amount, decimals=token.decimals)

        # если передан нативный токен
        if token.type_token == TokenTypes.NATIVE:
            tx = self._prepare_tx(amount, to_address)
            fee_spend = 21000 * tx['maxFeePerGas'] * multiplier
            if balance.wei - fee_spend - amount.wei < 0:
                logger.error(
                    f'{self.account.profile_number} Недостаточно средств для отправки транзакции, баланс: {balance.ether_float} ETH, сумма: {amount.ether_float} ETH')
                raise ValueError(
                    f'{self.account.profile_number} Недостаточно средств для отправки транзакции')
            tx['value'] = amount.wei

        else:
            if balance.wei < amount.wei:
                amount = balance
            contract = self._get_contract(token)
            tx_params = self._prepare_tx()
            tx = contract.functions.transfer(to_address, amount.wei).build_transaction(tx_params)

        hash = self._sing_and_send(tx)
        message = f'send {amount.ether_float} {token.symbol} to {to_address}'
        logger.info(f'Транзакция отправлена [{message}] tx hash: {hash}')
        return hash

    def _prepare_tx(self, value: Optional[Amount] = None,
                    to_address: Optional[str | ChecksumAddress] = None) -> dict:
        """
        Подготовка параметров транзакции
        :param value: сумма перевода ETH, если ETH нужно приложить к транзакции
        :param to_address:  адрес получателя, если транзакция НЕ на смарт контракт
        :return: параметры транзакции
        """
        random_multiplier = random.uniform(1.05, 1.1)
        base_fee = self.w3.eth.gas_price
        priority_fee = self._get_priority_fee()
        max_fee = int((base_fee + priority_fee) * random_multiplier)

        tx_params = {
            'from': self.account.address,
            'nonce': self.w3.eth.get_transaction_count(self.account.address),
            'maxFeePerGas': max_fee,
            'maxPriorityFeePerGas': priority_fee,
            'chainId': self.w3.eth.chain_id,
        }

        if value:
            tx_params['value'] = value.wei

        if to_address:
            tx_params['to'] = to_address

        return tx_params

    def _replace_eth_to_weth(self, token: Token) -> Token:
        """
        Замена ETH на WETH для поиска пула ликвидности
        :param token: объект Token
        :return: исходный объект Token или WETH вместо ETH
        """
        if token == Tokens.ETH:
            return Tokens.get_token_by_symbol('WETH', self.chain)
        return token

    def _get_allowance(self, token: Token, spender: str | ChecksumAddress | ContractRaw) -> Amount:
        """
        Получение разрешенной суммы токенов на снятие
        :param token: объект Token
        :param spender: адрес контракта, который получил разрешение на снятие токенов
        :return: объект Amount с разрешенной суммой
        """
        if isinstance(spender, ContractRaw):
            spender = spender.address

        if isinstance(spender, str):
            spender = Web3.to_checksum_address(spender)

        contract = self._get_contract(token)
        allowance = contract.functions.allowance(self.account.address, spender).call()
        return Amount(allowance, decimals=token.decimals, wei=True)

    def _approve(self, token: Token, amount: Amount | int | float,
                 spender: str | ChecksumAddress | ContractRaw) -> None:

        """
        Одобрение транзакции на снятие токенов
        :param token: токен, который одобряем
        :param amount: сумма одобрения
        :param spender: адрес контракта, который получит разрешение на снятие токенов
        :return: None
        """

        if token.type_token == TokenTypes.NATIVE:
            return

        if self._get_allowance(token, spender).wei >= amount.wei:
            return

        if isinstance(amount, (int, float)):
            amount = Amount(amount, decimals=token.decimals)

        if isinstance(spender, ContractRaw):
            spender = spender.address

        contract = self._get_contract(token)
        tx_params = self._prepare_tx()

        tx = contract.functions.approve(spender, amount.wei).build_transaction(tx_params)
        self._sing_and_send(tx)
        message = f'approve {amount.ether_float} {token.symbol} to {spender}'
        logger.info(f'Транзакция отправлена {message}')

    def _sing_and_send(self, tx: dict) -> str:
        """
        Подпись и отправка транзакции
        :param tx: параметры транзакции
        :return: хэш транзакции
        """
        random_multiplier = random.uniform(1.05, 1.1)
        tx['gas'] = int(self.w3.eth.estimate_gas(tx) * random_multiplier * 1.1)
        signed_tx = self.w3.eth.account.sign_transaction(tx, self.account.private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        return tx_receipt.transactionHash.hex()


if __name__ == '__main__':
    pass
