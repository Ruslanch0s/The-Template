from models import Chain
from models.exceptions import ChainNameError


class Chains:
    """
    Класс для хранения списка сетей.
    Название переменных Chains и значение name в объекте Chain должны совпадать.
    """
    ETHEREUM = Chain(
        name='ethereum',
        rpc='https://1rpc.io/ethereum',
        chain_id=1
    )

    LINEA = Chain(
        name='linea',
        rpc='https://1rpc.io/linea',
        chain_id=59144
    )
    ARBITRUM_ONE = Chain(
        name='arbitrum_one',
        rpc='https://1rpc.io/arbitrum',
        chain_id=42161
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
