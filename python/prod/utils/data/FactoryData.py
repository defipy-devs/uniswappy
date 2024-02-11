# Copyright [2024] [Ian Moore]
# Distributed under the MIT License (license terms are at http://opensource.org/licenses/MIT).
# Email: defipy.devs@gmail.com

from dataclasses import dataclass

@dataclass
class FactoryData:
    token_from_exchange: {}
    parent_lp: None
    name: str = None
    address: str = None
    
   