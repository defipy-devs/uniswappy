# AddLiquidity.py
# Author: Ian Moore ( utiliwire@gmail.com )
# Date: May 2023

from ..Process import Process
from ...math.model import TokenDeltaModel
from ...math.model import EventSelectionModel

class AddLiquidity(Process):
     
    """ Add liquidity process

        Parameters
        ----------
        self.ev : EventSelectionModel
            EventSelectionModel object to randomly generate buy vs sell events
        self.tDel : TokenDeltaModel
            TokenDeltaModel to randomly generate token amounts        
    """     

    def __init__(self, init_price = None, ev = None, tDel = None):
        self.ev = EventSelectionModel() if ev  == None else ev
        self.tDel = TokenDeltaModel(50) if tDel == None else tDel
        self.init_price = 1 if init_price == None else init_price
            
    def apply(self, lp, token_in, user_nm, amount_in):    
        
        """ apply

            Adds liquidity using only X or Y amounts
                
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
            (amount_in, amount_out) : float, float
                token swap amounts                
        """          
        
        amount_in = tDel.delta() if amount_in == None else amount_in
        if(token_in.token_name == lp.token0):
            balance0 = amount_in         
            if(lp.reserve1 > 0):
                balance1 = lp.quote(amount_in, lp.reserve0, lp.reserve1)
            else:
                balance1 = self.init_price*balance0               
            
            lp.add_liquidity(user_nm, balance0, balance1, balance0, balance1)
        elif(token_in.token_name == lp.token1):
            balance1 = amount_in
            if(lp.reserve0 > 0):
                balance0 = lp.quote(amount_in, lp.reserve1, lp.reserve0)
            else:
                balance0 = self.init_price*balance1            
            
            lp.add_liquidity(user_nm, balance0, balance1, balance0, balance1) 

        return {lp.token0:balance0, lp.token1:balance1}    
    
 
        
