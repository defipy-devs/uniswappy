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