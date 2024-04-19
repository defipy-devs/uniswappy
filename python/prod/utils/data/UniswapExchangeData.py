# Copyright [2024] [Ian Moore]
# Distributed under the MIT License (license terms are at http://opensource.org/licenses/MIT).
# Email: defipy.devs@gmail.com

from dataclasses import dataclass
from .ExchangeData import ExchangeData
from ...erc import ERC20

DEFAULT_VERSION = 'V2'

@dataclass
class UniswapExchangeData(ExchangeData):
    tkn0: ERC20
    tkn1: ERC20 
    version: str = DEFAULT_VERSION
    tick_spacing: int = None   
    fee: int = None