from abc import *

from ...erc import LPERC20

class IExchange(ABC, LPERC20):
    
    @abstractmethod        
    def summary(self, agents):
        pass
    
    @abstractmethod        
    def get_price(self, agents):
        pass
    
    @abstractmethod        
    def get_reserve(self, agents):
        pass    