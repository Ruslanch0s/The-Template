import pytest

from config import Chains
from models.exceptions import ChainNameError


def test_chains_get_chains():
    assert Chains.LINEA == Chains.get_chain('Linea')
    assert Chains.LINEA != Chains.get_chain('Ethereum')
    assert Chains.LINEA == Chains.get_chain('Linea'.upper())
    assert Chains.LINEA == Chains.get_chain('Linea'.lower())
    assert Chains.LINEA == Chains.get_chain('Linea').name
    assert Chains.ARBITRUM_ONE == Chains.get_chain(Chains.ARBITRUM_ONE.name)
    assert Chains.ARBITRUM_ONE != Chains.get_chain(Chains.ETHEREUM.name)

    with pytest.raises(ChainNameError):
        Chains.get_chain('777')

    with pytest.raises(TypeError):
        Chains.get_chain(777)


