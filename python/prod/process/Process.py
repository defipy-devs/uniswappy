# Copyright [2023] [Ian Moore]
# Distributed under the MIT License (license terms are at http://opensource.org/licenses/MIT).
# Email: defipy.devs@gmail.com

from abc import *

class Process(ABC):
             
    @abstractmethod        
    def apply(self, lp, token, user_nm, amount):
        pass
