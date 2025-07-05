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

class IndexERC20(ERC20):
    
    """ Index ERC20 token

        Parameters
        ----------
        token_name : str
            Token name 
        token_addr : str
            Token address  
        token_total : float
            Token holdings 
    """  

    def __init__(self, name, addr, parent_tkn, parent_lp):
        self.token_name = name
        self.token_addr = addr
        self.parent_lp = parent_lp
        self.parent_tkn = parent_tkn
        self.token_supply = 0
        self.token_total = 0
        self.type = 'index'
        
        
    def rebase(self): 
        
        """ rebase

            Rebase token 
                
            Parameters
            -------
            _to : str
                user address   
            value : str
                reset token value                
        """         
        
        self.token_total = new_total
        
