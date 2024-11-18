from models.chain import Chain
from models.exceptions import ChainNameError


class Chains:
    """
    Класс для хранения списка сетей.
    Название переменных Chains и значение name в объекте Chain должны совпадать.
    Информацию для добавление сети можно взять из https://chainlist.org/ (рекомендую 1rpc).
    Сети из данного списка можно использовать в скрипте вставляя в выбор или добавление сети
    метамаска, а так же для подключение к RPC ноде в Web3 транзакциях.

    Объект Chain содержит следующие поля:

    обязательные:

    - name - имя сети
    - rpc - адрес ноды
    - chain_id - id сети

    опциональные:

    - tx_type - тип транзакции, по умолчанию 2 (0 - Legacy, 2 - EIP-1559)
    - native_token - тикер нативного токена сети, по умолчанию 'ETH'
    - metamask_name - название сети в metamask, по умолчанию берется из параметра name


    """
    ETHEREUM = Chain(
        name='ethereum',
        metamask_name='Ethereum Mainnet',
        rpc='https://1rpc.io/ethereum',
        chain_id=1
    )

    LINEA = Chain(
        name='linea',
        metamask_name='Linea Mainnet',
        rpc='https://1rpc.io/linea',
        chain_id=59144
    )
    ARBITRUM_ONE = Chain(
        name='arbitrum_one',
        metamask_name='Arbitrum One',
        rpc='https://1rpc.io/arb',
        chain_id=42161
    )

    TAIKO = Chain(
        name='taiko',
        rpc='https://taiko.drpc.org',
        chain_id=167000
    )

    BSC = Chain(
        name='bsc',
        rpc='https://1rpc.io/bnb',
        chain_id=56,
        native_token='BNB'
    )

    @classmethod
    def get_chain(cls, name: str) -> Chain:
        """
        Находит сеть по имени, сначала ищет по названию переменной с сетью, если
        не находит, ищет среди имен объектов класса Chain.
        :param name: имя сети
        :return: объект сети Chain, если не находит, бросает исключение ChainNameError
        """
        if not isinstance(name, str):
            raise TypeError(f'Ошибка поиска сети, для поиска нужно передать str, передано:  {type(name)}')

        name = name.upper()
        try:
            chain = getattr(cls, name)
            return chain
        except AttributeError:
            for chain in cls.__dict__.values():
                if isinstance(chain, Chain):
                    if chain.name.upper() == name:
                        return chain
            raise ChainNameError(f'Chain {name} not found')


if __name__ == '__main__':
    pass
