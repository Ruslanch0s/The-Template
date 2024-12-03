from typing import Optional

from loguru import logger


class Chain:
    """
    Класс для хранения информации о сети. Информацию о сети можно искать тут https://chainid.network/chains.json

    - name - название сети, в формате snake_case, при инициализации в класс Chains должно совпадать с именем переменной
    - param rpc:  адрес провайдера в формате https://1rpc.io/ethereum, можно взять на https://chainlist.org/
    - chain_id: id сети, например 1 для Ethereum, можно искать тут https://chainid.network/chains.json
    - tx_type: тип транзакции, по умолчанию 2 (0 - Legacy, 2 - EIP-1559),  можно искать тут https://chainid.network/chains.json
    - native_token: тикер нативного токена сети, по умолчанию 'ETH'
    - metamask_name: название сети в metamask, по умолчанию берется из параметра name
    - okx_name: название сети в OKX, список сетей можно получить запустив метод bot.okx.get_chains()
    """

    def __init__(
            self,
            name: str,
            rpc: str,
            *,
            chain_id: int,
            metamask_name: Optional[str] = None,
            tx_type: int = 2,
            native_token: str = 'ETH',
            okx_name: Optional[str] = None
    ):
        self.name = name
        self.rpc = rpc
        self.chain_id = chain_id
        self.metamask_name = metamask_name if metamask_name else name
        self.tx_type = tx_type
        self.native_token = native_token
        self.okx_name = okx_name if okx_name else name

    def __str__(self):
        return self.rpc

    def __eq__(self, other):
        if isinstance(other, Chain):
            return self.name == other.name
        elif isinstance(other, str):
            return self.name.lower() == other.lower()
        else:
            logger.error(f'Ошибка сравнения сетей {type(other)}')
            return False


if __name__ == '__main__':
    pass
