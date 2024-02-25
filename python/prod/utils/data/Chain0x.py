# Copyright [2024] [Ian Moore]
# Distributed under the MIT License (license terms are at http://opensource.org/licenses/MIT).
# Email: defipy.devs@gmail.com

from dataclasses import dataclass

@dataclass
class Chain0x:
    
    ETHEREUM = 'api.0x.org'
    ARBITRUM = 'arbitrum.api.0x.org'
    AVALANCHE = 'avalanche.api.0x.org'
    BASE = 'base.api.0x.org'
    BINANCE = 'bsc.api.0x.org'
    CELO = 'celo.api.0x.org'
    FANTOM = 'fantom.api.0x.org'
    OPTIMISM = 'optimism.api.0x.org'
    POLYGON = 'polygon.api.0x.org'    
    
    pass