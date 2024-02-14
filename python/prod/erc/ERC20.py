# Copyright [2023] [Ian Moore]
# Distributed under the MIT License (license terms are at http://opensource.org/licenses/MIT).
# Email: defipy.devs@gmail.com

GWEI_PRECISION = 18

class ERC20:
    
    """ ERC20 token akjhsflkjbvjn cn vvk

        Parameters
        -----------------
        self.token_name : str
            Token name 
        self.token_addr : str
            Token address  
        self.token_total : float
            Token holdings 
    """   
    
    def __init__(self, name: str, addr: str, decimal: int = None):
        self.token_name = name
        self.token_addr = addr
        self.token_total = 0
        self.token_decimal = GWEI_PRECISION if decimal == None else decimal
        self.type = 'standard'

    def deposit(self, _from, value):
        
        """ deposit intlkaflkw nsdlkamnas

            Deposit token
                
            Parameters
            -----------------
            _from : str
                user address   
            value : str
                delta to add to total                
        """           
        
        self.token_total += value

    def transfer(self, _to, value):
        
        """ transfer intlkaflkwns dlkamnas

            Transfer token
                
            Parameters
            -----------------
            _to : str
                user address   
            value : str
                delta to remove from total                
        """         
        
        self.token_total -= value
        
