# ─────────────────────────────────────────────────────────────────────────────
# Apache 2.0 License (DeFiPy)
# ─────────────────────────────────────────────────────────────────────────────
# Copyright 2023–2025 Ian Moore
# Email: defipy.devs@gmail.com
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License

from .ERC20 import ERC20

class LPERC20(ERC20):
    
    """ DAOSYS ERC20 token

        Parameters
        -----------------
        token_name : str
            Token name 
        token_addr : str
            Token address  
        token_total : float
            Token holdings 
        type : float
            Token type 
    """      

    def __init__(self, name: str, addr: str) -> None:
        self.token_name = name+'-LP'
        self.token_addr = addr
        self.token_supply = 1_000_000_000
        self.token_total = 0
        self.type = 'lp'
        
    def set_token_lp(self, token_total):
        
        """ set_token_lp

            Reset token LP
                
            Parameters
            -----------------
            token_total : float
                token total        
        """         
        
        self.token_total = token_total

    def add_token_lp(self, value):
        
        """ add_token_lp

            Add token delta to token total
                
            Parameters
            -----------------
            value : float
                token delta        
        """            
        
        self.token_total += value           
        
    def remove_token_lp(self, value):
        
        """ remove_token_lp

            Remove token delta to token total
                
            Parameters
            -----------------
            value : float
                token delta        
        """          
        
        self.token_total -= value        

