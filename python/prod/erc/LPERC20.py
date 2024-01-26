# LPERC20.py
# Author: Ian Moore ( utiliwire@gmail.com )
# Date: May 2023

from .ERC20 import ERC20

class LPERC20(ERC20):
    
    """ DAOSYS ERC20 token

        Parameters
        ----------
        self.token_name : str
            Token name 
        self.token_addr : str
            Token address  
        self.token_total : float
            Token holdings 
        self.type : float
            Token type 
            
        Reference
        ----------   
        https://docs.uniswap.org/protocol/V1/guides/connect-to-uniswap#token-interface
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
            -------
            token_total : float
                token total        
        """         
        
        self.token_total = token_total

    def add_token_lp(self, value):
        
        """ add_token_lp

            Add token delta to token total
                
            Parameters
            -------
            value : float
                token delta        
        """            
        
        self.token_total += value           
        
    def remove_token_lp(self, value):
        
        """ remove_token_lp

            Remove token delta to token total
                
            Parameters
            -------
            value : float
                token delta        
        """          
        
        self.token_total -= value        

