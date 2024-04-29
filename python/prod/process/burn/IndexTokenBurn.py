# Copyright [2023] [Ian Moore]
# Distributed under the MIT License (license terms are at http://opensource.org/licenses/MIT).
# Email: defipy.devs@gmail.com

from ..Process import Process
from ..swap import Swap
from ...cpt.vault import IndexVault
from ...math.model import TokenDeltaModel
from ...math.model import EventSelectionModel

class IndexTokenBurn(Process):

    """ Index token burn process

        Parameters
        ----------
        ivault : IndexVault
            Index vault
    """       
    
    def __init__(self, ivault):
        self.ivault = IndexVault('iVault', "0x7") if ivault  == None else ivault
            
    def apply(self, lp_tkn, token, user_nm, lp_burn_amt): 
        
        """ apply

            Burn index token from vault and swap out its parent token from its respective LP
                
            Parameters
            -------
            lp_tkn : Exchange
                LP exchange
            token : ERC20
                specified ERC20 token               
            user_nm : str
                account name
            lp_burn_amt : float
               token amount to be burned 
                
            Returns
            -------
            result : float
                amount of burned token                   
        """           
        
        tkn_amts = self.ivault.burn_lp_token(user_nm, lp_tkn, token, lp_burn_amt)
        result = -1

        if(bool(tkn_amts)):
            trading_token = self.get_trading_token(lp_tkn, token)
            out = Swap().apply(lp_tkn, trading_token, user_nm, tkn_amts[trading_token.token_name])
            result = out+tkn_amts[token.token_name]
            
        self.ivault.update_accounts(lp_tkn, token)    
        
        return result  
    
    def get_trading_token(self, lp, token):
        
        """ get_trading_token

            Get opposing token from specified token
                
            Parameters
            -------
            lp : Exchange
                LP exchange
            token : ERC20
                specified ERC20 token      
                
            Returns
            -------
            trading_token : ERC20 
                opposing ERC20 token                   
        """         
        
        tokens = lp.factory.exchange_to_tokens[lp.name]
        trading_token = tokens[lp.token1] if token.token_name == lp.token0 else tokens[lp.token0]
        return trading_token  
        
