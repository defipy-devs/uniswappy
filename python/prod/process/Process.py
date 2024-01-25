# Process.py
# Author: Ian Moore ( utiliwire@gmail.com )
# Date: May 2023

from abc import *

class Process(ABC):
             
    @abstractmethod        
    def apply(self, lp, token, user_nm, amount):
        pass