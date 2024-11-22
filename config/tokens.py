from config.chains import Chains
from models.token import Token, TokenTypes
from models.chain import Chain

from models.exceptions import TokenNameError
from utils.utils import to_checksum


class Tokens:
    """
    Класс для хранения токенов, названия переменных должны быть в формате SYMBOL_CHAIN_NAME
    Например: для токена WETH в сети Arbitrum One переменная будет называться WETH_ARBITRUM_ONE
    """
    ETH = Token(
        symbol='ETH',
        address='0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee',
        chain=Chains.ETHEREUM,
        type_token=TokenTypes.NATIVE,
    )


    WETH_ARBITRUM_ONE = Token(
        symbol='WETH',
        address='0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8',
        chain=Chains.ARBITRUM_ONE,
    )


    WETH_TAIKO = Token(
        symbol='WETH',
        address='0xa51894664a773981c6c112c43ce576f315d5b1b6',
        chain=Chains.TAIKO,
    )

    ANGLE_ETHEREUM = Token(
        symbol='ANGLE',
        address='0x31429d1856aD1377A8A0079410B297e1a9e214c2',
        chain=Chains.ETHEREUM,
        type_token=TokenTypes.ERC20,
        decimals=18
    )


    @classmethod
    def get_token_by_address(cls, address: str) -> Token:
        address = to_checksum(address)
        for token in cls.__dict__.values():
            if isinstance(token, Token):
                if token.address == address:
                    return token
        raise TokenNameError(f'Token with address {address} not found')

    @classmethod
    def get_token_by_symbol(cls, symbol: str, chain: Chain) -> Token:
        symbol_and_chain = f'{symbol.upper()}_{chain.name.upper()}'
        return getattr(cls, symbol_and_chain)

    @classmethod
    def add_token(cls, token: Token):
        setattr(cls, token.symbol, token)
        return token

    @classmethod
    def get_tokens(cls, chain: Chain) -> list[Token]:
        """
        Получение списка токенов для сети
        :param chain: объект Chain
        :return:  список токенов
        """
        tokens = []
        for token in cls.__dict__.values():
            if isinstance(token, Token):
                if token.chain == chain:
                    tokens.append(token)
        return tokens
