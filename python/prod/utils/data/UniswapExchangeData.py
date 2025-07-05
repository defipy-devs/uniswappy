# ─────────────────────────────────────────────────────────────────────────────
# Apache 2.0 License (DeFiPy)
# ─────────────────────────────────────────────────────────────────────────────
# Copyright 2023–2025 Ian Moore
# Email: defipy.devs@gmail.com
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License

from dataclasses import dataclass
from .ExchangeData import ExchangeData
from ...erc import ERC20

DEFAULT_VERSION = 'V2'
DEFAULT_TYPE = 'DEC'

@dataclass
class UniswapExchangeData(ExchangeData):

    VERSION_V2 = DEFAULT_VERSION
    VERSION_V3 = 'V3'

    TYPE_DEC = DEFAULT_TYPE
    TYPE_GWEI = 'GWEI'    
        
    tkn0: ERC20
    tkn1: ERC20 
    version: str = DEFAULT_VERSION
    precision: str = DEFAULT_TYPE
    tick_spacing: int = None   
    fee: int = None