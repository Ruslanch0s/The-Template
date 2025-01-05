from models.chain import Chain
from models.exceptions import ChainNameError


class Chains:
    """
    Класс для хранения списка сетей.
    Название переменных Chains и значение name в объекте Chain должны совпадать.
    Информацию для добавление сети можно взять из https://chainlist.org/ (рекомендую 1rpc)
    и из https://chainid.network/chains.json, либо https://api.debank.com/chain/list
    Информацию о eip1559 можно посмотреть тут https://api.debank.com/chain/list

    Сети из данного списка можно использовать в скрипте вставляя в выбор или добавление сети
    метамаска, а так же для подключение к RPC ноде в Web3 транзакциях.

    Объект Chain содержит следующие поля:

    обязательные:

    - name - название сети, в формате snake_case, при инициализации в класс Chains должно совпадать с именем переменной
    - param rpc: адрес провайдера в формате https://1rpc.io/ethereum, можно взять на https://chainlist.org/
    - chain_id: id сети, например 1 для Ethereum, можно искать тут https://chainid.network/chains.json

    опциональные:

    - tx_type: тип транзакции, по умолчанию 2 (0 - Legacy, 2 - EIP-1559), можно искать тут https://api.debank.com/chain/list
    - native_token: тикер нативного токена сети, по умолчанию 'ETH'
    - metamask_name: название сети в metamask, по умолчанию берется из параметра name
    - okx_name: название сети в OKX, список сетей можно получить запустив метод bot.okx.get_chains()

    """
    # аргумент для хранения списка сетей
    _chains = None

    ETHEREUM = Chain(
        name='ethereum',
        rpc='https://1rpc.io/eth',
        chain_id=1,
        metamask_name='Ethereum Mainnet',
        tx_type=2,
        native_token='ETH',
        okx_name='ERC20'
    )

    LINEA = Chain(
        name='linea',
        rpc='https://1rpc.io/linea',
        chain_id=59144,
        metamask_name='Linea Mainnet',
        tx_type=2,
        native_token='ETH',
        okx_name='Linea'
    )

    ARBITRUM_ONE = Chain(
        name='arbitrum_one',
        rpc='https://1rpc.io/arb',
        chain_id=42161,
        metamask_name='Arbitrum One',
        tx_type=2,
        native_token='ETH',
        okx_name='Arbitrum One'
    )

    BSC = Chain(
        name='bsc',
        rpc='https://1rpc.io/bnb',
        chain_id=56,
        metamask_name='Binance Smart Chain',
        tx_type=0,
        native_token='BNB',
        okx_name='BSC'
    )

    OP = Chain(
        name='op',
        rpc='https://1rpc.io/op',
        chain_id=10,
        native_token='ETH',
        metamask_name='Optimism Mainnet',
        tx_type=2,
        okx_name='Optimism'
    )

    POLYGON = Chain(
        name='polygon',
        rpc='https://1rpc.io/matic',
        chain_id=137,
        native_token='POL',
        metamask_name='Polygon',
        tx_type=2,
        okx_name='Polygon'
    )

    AVALANCHE = Chain(
        name='avalanche',
        rpc='https://1rpc.io/avax/c',
        chain_id=43114,
        native_token='AVAX',
        metamask_name='Avalanche',
        tx_type=2,
        okx_name='Avalanche C'
    )

    ZKSYNC = Chain(
        name='zksync',
        rpc='https://1rpc.io/zksync2-era',
        chain_id=324,
        native_token='ETH',
        metamask_name='zkSync',
        tx_type=2,
        okx_name='zkSync Era'
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
            raise ChainNameError(f'Сеть {name} не найдена, добавьте ее в config/Chains, имена должны совпадать')


    @classmethod
    def get_chains_list(cls) -> list[Chain]:
        """
        Возвращает список сетей, можно использовать для итерации по сетям.
        :return: список сетей
        """
        if not cls._chains:
            cls._chains = [chain for chain in cls.__dict__.values() if isinstance(chain, Chain)]
        return cls._chains


if __name__ == '__main__':
    pass
