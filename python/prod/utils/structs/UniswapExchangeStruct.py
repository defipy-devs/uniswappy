from dataclasses import dataclass
from .ExchangeStruct import ExchangeStruct 
from ...erc import ERC20

@dataclass
class UniswapExchangeStruct(ExchangeStruct):
    tkn0: ERC20
    tkn1: ERC20 