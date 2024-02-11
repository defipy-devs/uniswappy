# Copyright [2023] [Ian Moore]
# Distributed under the MIT License (license terms are at http://opensource.org/licenses/MIT).
# Email: defipy.devs@gmail.com

from abc import *

class Vault(ABC):
             
    @abstractmethod        
    def rebase_index_tkn(self, lp_token, token):
        pass
    @abstractmethod     
    def deposit_lp_tkn(self, _to, token, amt):
        pass    
    @abstractmethod     
    def remove_lp_tkn(self, _to, token, amt):
        pass
    @abstractmethod 
    def get_tkn_pair_amount(self, lp_tkn, tkn, liq):
        pass     
    @abstractmethod 
    def get_token_type(self, lp_tkn, tkn, liq):
        pass      