# ERC20.py
# Author: Ian Moore ( utiliwire@gmail.com )
# Date: May 2023

GWEI_PRECISION = 18

class ERC20:
    
    """ ERC20 token

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
    def __init__(self, name: str, addr: str, decimal: int = None) -> None:
        self.token_name = name
        self.token_addr = addr
        self.token_supply = 1_000_000_000
        self.token_total = 0
        self.token_decimal = GWEI_PRECISION if decimal == None else decimal
        self.type = 'standard'

    def deposit(self, _from, value):
        
        """ deposit

            Reset token LP
                
            Parameters
            -------
            _from : str
                user address   
            value : str
                delta to add to total                
        """           
        
        self.token_total += value

    def transfer(self, _to, value):
        
        """ transfer

            Reset token LP
                
            Parameters
            -------
            _to : str
                user address   
            value : str
                delta to remove from total                
        """         
        
        self.token_total -= value
        
