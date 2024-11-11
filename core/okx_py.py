from __future__ import annotations

from typing import Literal


from config import config

import okx.Funding as Funding
from loguru import logger

from utils.utils import random_sleep


class OKX:
    def __init__(self):
        self.funding_api = Funding.FundingAPI(
            config.okx_api_key_main,
            config.okx_secret_key_main,
            config.okx_passphrase_main,
            flag="0",
            debug=False
        )

    def get_currencies(self):
        """
        Получение списка доступных токенов и сетей.
        :return: список токенов
        """
        response = self.funding_api.get_currencies()
        data = response.get("data")
        if response.get("code") != "0":
            logger.error(f"Не удалось получить список токенов: {response.get('msg')}")
        for chain in data:
            print(chain)


    def withdraw(
            self,
            address: str,
            chain: Literal["ERC20", "Linea"],
            token: str,
            amount: float
    ) -> None:
        """
        Вывод средств с биржи OKX
        :param address:  Адрес кошелька
        :param chain: сеть токена
        :param token: токен
        :param amount: сумма
        :return: None
        """
        token_with_chain = token + "-" + chain
        fee = self._get_withdrawal_fee(token, token_with_chain)

        try:
            logger.info(f'{address}: Выводим с okx {amount} {token}')
            response = self.funding_api.withdrawal(
                ccy=token,
                amt=amount,
                dest=4,
                toAddr=address,
                fee=fee,
                chain=token_with_chain,
            )
            if response.get("code") != "0":
                raise Exception(
                    f'{address}: Не удалось вывести {amount} {token}: {response.get("msg")}')
            tx_id = response.get("data")[0].get("wdId")
            self._wait_confirm(tx_id)
            logger.info(f'{address}: Успешно выведено {amount} {token}')
        except Exception as error:
            logger.error(f'{address}: Не удалось вывести {amount} {token}: {error} ')
            raise error

    def _get_withdrawal_fee(self, token: str, token_with_chain: str):
        """
        Получение комиссии за вывод
        :param token: название токена
        :param token_with_chain: айди токен-сеть
        :return:
        """
        response = self.funding_api.get_currencies(token)
        for network in response.get("data"):
            if network.get("chain") == token_with_chain:
                return network.get("minFee")

        logger.error(f" не могу получить сумму комиссии, проверьте значения symbolWithdraw и network")
        return 0

    def _wait_confirm(self, tx_id: str) -> None:
        """
        Ожидание подтверждения транзакции вывода с OKX
        :param tx_id: id транзакции вывода
        :return: None
        """
        for _ in range(30):
            tx_info = self.funding_api.get_deposit_withdraw_status(wdId=tx_id)
            if tx_info.get("code") == "0":
                if 'Withdrawal complete' in tx_info.get("data")[0].get("state"):
                    logger.info(f"Транзакция {tx_id} завершена")
                    return
            random_sleep(10)
        logger.error(f"Ошибка транзакция {tx_id} не завершена")
        raise Exception(f"Транзакция {tx_id} не завершена")
