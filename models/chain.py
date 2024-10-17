from loguru import logger


class Chain:
    """
    Класс для хранения информации о сети

    name - название сети, в формате snake_case, при инициализации
    в класс Chains должно совпадать с именем переменной

    rpc - адрес провайдера в формате https://mainnet.infura.io/v3

    chain_id - id сети, например 1 для Ethereum

    tx_type - тип транзакции, по умолчанию 2 (0 - Legacy, 2 - EIP-1559)

    native_token - тикер нативного токена сети, по умолчанию 'ETH'
    """

    def __init__(
            self,
            name: str,
            rpc: str,
            *,
            chain_id: int,
            tx_type: int = 2,
            native_token: str = 'ETH'
    ):
        self.name = name
        self.rpc = rpc
        self.chain_id = chain_id
        self.tx_type = tx_type
        self.native_token = native_token

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
