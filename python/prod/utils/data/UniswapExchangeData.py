from dataclasses import dataclass
from .ExchangeData import ExchangeData
from ...erc import ERC20

@dataclass
class UniswapExchangeData(ExchangeData):
    tkn0: ERC20
    tkn1: ERC20 