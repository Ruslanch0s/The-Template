from config import Chains
from models import Token, TokenTypes
from utils.utils import to_checksum


def test_token():
    ETH = Token(
        symbol='ETH',
        address='0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee',
        chain=Chains.LINEA,
        type=TokenTypes.NATIVE,
        decimals=18,
    )
    WETH = Token(
        symbol='WETH',
        address='0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8',
        chain=Chains.ARBITRUM_ONE,
    )

    assert ETH == ETH
    assert ETH != WETH

    assert ETH == 'ETH'
    assert ETH == 'eth'
    assert ETH != 'WETH'

    assert ETH.address == to_checksum('0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee')
    assert ETH.address != '0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee'
    assert ETH == '0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee'
    assert ETH == to_checksum('0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee')
    assert ETH != '0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee0'
    assert ETH.symbol == 'ETH'
    assert ETH.symbol != 'WETH'

    assert ETH.abi_name == 'erc20'
    assert ETH._abi is None
    assert ETH.get_abi() == ETH._abi
    assert ETH._abi is not None
