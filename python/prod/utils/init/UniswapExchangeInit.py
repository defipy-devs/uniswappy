from dataclasses import dataclass
from .ExchangeInit import ExchangeInit
from ...erc import ERC20

@dataclass
class UniswapExchangeInit(ExchangeInit):
    tkn0: ERC20
    tkn1: ERC20 