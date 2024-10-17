from config import Chains


def test_chain():
    assert Chains.LINEA == 'Linea'
    assert Chains.LINEA == 'Linea'.lower()
    assert Chains.LINEA == 'Linea'.upper()
    assert Chains.LINEA != 'Ethereum'
    assert Chains.LINEA != Chains.ETHEREUM

