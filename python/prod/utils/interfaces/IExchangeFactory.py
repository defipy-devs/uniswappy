# Copyright [2024] [Ian Moore]
# Distributed under the MIT License (license terms are at http://opensource.org/licenses/MIT).
# Email: defipy.devs@gmail.com

from abc import *
from .IExchange import IExchange 

class IExchangeFactory(ABC):
    
    @abstractmethod        
    def deploy(self, agents):
        pass
    
    @abstractmethod        
    def get_exchange(self, exchange: IExchange):
        pass
    
    @abstractmethod        
    def get_token(self, exchange: IExchange):
        pass    