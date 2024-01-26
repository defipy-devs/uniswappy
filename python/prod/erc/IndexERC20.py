# IndexERC20.py
# Author: Ian Moore ( utiliwire@gmail.com )
# Date: May 2023

from .ERC20 import ERC20

class IndexERC20(ERC20):
    
    """ Index ERC20 token

        Parameters
        ----------
        self.token_name : str
            Token name 
        self.token_addr : str
            Token address  
        self.token_total : float
            Token holdings 
            
        Reference
        ----------   
        https://docs.uniswap.org/protocol/V1/guides/connect-to-uniswap#token-interface
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
        
