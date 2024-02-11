# Copyright [2024] [Ian Moore]
# Distributed under the MIT License (license terms are at http://opensource.org/licenses/MIT).
# Email: defipy.devs@gmail.com

from abc import *

class IExchange(ABC):
    
    @abstractmethod        
    def summary(self, agents):
        pass
    
    @abstractmethod        
    def get_price(self, agents):
        pass
    
    @abstractmethod        
    def get_reserve(self, agents):
        pass    