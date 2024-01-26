# RemoveLiquidity.py
# Author: Ian Moore ( utiliwire@gmail.com )
# Date: May 2023

from ..Process import Process
from ...math.model import TokenDeltaModel
from ...math.model import EventSelectionModel

class RemoveLiquidity(Process):
    
    """ Remove liquidity process

        Parameters
        ----------
        self.ev : EventSelectionModel
            EventSelectionModel object to randomly generate buy vs sell events
        self.tDel : TokenDeltaModel
            TokenDeltaModel to randomly generate token amounts        
    """       

    def __init__(self, ev = None, tDel = None):
        self.ev = EventSelectionModel() if ev  == None else ev
        self.tDel = TokenDeltaModel(50) if tDel == None else tDel
            
    def apply(self, lp, token_in, user_nm, amount_in):    
        
        """ apply

            Removes liquidity using only X or Y amounts
                
            Parameters
            -------
            lp : Exchange
                LP exchange
            token_in : ERC20
                specified ERC20 token               
            user_nm : str
                account name
            amount_in : float
               token amount to be add to liquidity 
                
            Returns
            -------
            reserve amounts : dictionary
                dictionary of reserve amounts                
        """          
        
        amount_in = self.tDel.delta() if amount_in == None else amount_in
        if(token_in.token_name == lp.token0):
            liq = amount_in*lp.total_supply/lp.reserve0
            amount1 = liq*lp.reserve1/lp.total_supply
            #liq = LPQuote().get_liquidity(lp, token_in, amount_in)
            #amount1 = LPQuote().get_amount(lp, token_in, amount_in)
            amount0, amount1 = lp.remove_liquidity(user_nm, liq, amount_in, amount1)
        elif(token_in.token_name == lp.token1): 
            liq = amount_in*lp.total_supply/lp.reserve1
            amount0 = liq*lp.reserve0/lp.total_supply
            #liq = LPQuote().get_liquidity(lp, token_in, amount_in)
            #amount0 = LPQuote().get_amount(lp, token_in, amount_in)
            amount0, amount1 = lp.remove_liquidity(user_nm, liq, amount0, amount_in)  

        return {lp.token0:amount0, lp.token1:amount1}    
    
 
        
