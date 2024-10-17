from __future__ import annotations

import json
from typing import Optional, TYPE_CHECKING

from eth_typing import ChecksumAddress
from loguru import logger

from config import PATH_TO_ABI
from utils.utils import to_checksum

if TYPE_CHECKING:
    from models import Chain


class ContractRaw:
    """
    Класс для хранения информации о контракте.

    address - адрес контракта

    abi_name - название файла с abi контракта, без расширения файла

    chain - сеть, на которой находится контракт
    """

    def __init__(self, address: str | ChecksumAddress, abi_name: str, chain: Chain):
        self.address = to_checksum(address)
        self.abi_name = abi_name
        self.chain = chain
        self._abi: Optional[list[dict]] = None

    def __str__(self):
        return self.address

    def __eq__(self, other) -> bool:
        if isinstance(other, ContractRaw):
            return self.address == other.address
        elif isinstance(other, str):
            if other.startswith('0x'):
                return self.address == to_checksum(other)
        logger.error(f'Ошибка сравнения контрактов {type(other)}')
        return False

    def get_abi(self) -> list[dict]:
        """
        Возвращает abi контракта из файла
        :return: abi контракта
        """
        if not self._abi:
            self._abi = json.load(open(PATH_TO_ABI / f'{self.abi_name}.json'))
        return self._abi
