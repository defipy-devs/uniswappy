# Copyright [2023] [Ian Moore]
# Distributed under the MIT License (license terms are at http://opensource.org/licenses/MIT).
# Email: defipy.devs@gmail.com

from ..Process import Process
from ..deposit import SwapDeposit
from ...math.model import TokenDeltaModel
from ...math.model import EventSelectionModel

class SwapIndexMint(Process):
    
    """ Process to swap-deposit single token into LP and mint its respective indexing token

        Parameters
        ----------
        ivault : IndexVault
            Index vault     
        opposing : boolean
            Boolean variable to determine whether to mint token opposing the one that was deposited                
    """     

    def __init__(self, ivault, opposing = None):
        self.ivault = IndexVault('iVault', "0x7") if ivault  == None else ivault
        self.opposing = False if opposing  == None else opposing
        self.mint_amt = 0
            
    def apply(self, lp_tkn, token, user_nm, amt, lwr_tick = None, upr_tick = None):    
        
        """ apply

            Swap-deposit single token into LP and mint its respective indexing token
                
            Parameters
            -------
            lp_tkn : Exchange
                LP exchange
            token : ERC20
                specified ERC20 token               
            user_nm : str
                account name
            amt : float
               token amount to be swapped and minted 
                
            Returns
            -------
            (amount_in, amount_out) : float, float
                token swap amounts                
        """           
        
        lp_amt0 = lp_tkn.total_supply
        out = SwapDeposit().apply(lp_tkn, token, user_nm, amt, lwr_tick, upr_tick)
        lp_amt1 = lp_tkn.total_supply
        lp_amt = lp_tkn.last_liquidity_deposit

        mint_token = token if not self.opposing else self.get_trading_token(lp_tkn, token)
        self.ivault.deposit_lp_tkn(user_nm, lp_tkn, lp_amt)
        self.ivault.rebase_index_tkn(lp_tkn, mint_token, lwr_tick, upr_tick) 
     
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
        
