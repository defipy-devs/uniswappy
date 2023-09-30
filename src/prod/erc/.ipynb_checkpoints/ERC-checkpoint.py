from abc import *

class ERC(ABC):
             
    @abstractmethod        
    def deposit(self, _from, value):
        pass
    
    @abstractmethod        
    def transfer(self, _from, value):
        pass    