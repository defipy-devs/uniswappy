# SwapDeposit.py
# Author: Ian Moore ( utiliwire@gmail.com )
# Date: Aug 2023

from ..Process import Process
from ..liquidity import AddLiquidity
from ..swap import Swap
from ...math.model import TokenDeltaModel
from ...math.model import EventSelectionModel
import math


class SwapDeposit(Process):
    
    """ Process to swap approx. half of single token X for token Y (and vice verse) and deposit proceeds
        plus remaining other approximated half

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

            Swap approx. half of single token X for token Y (and vice verse) and deposit proceeds
            plus remaining other approximated half
                
            Parameters
            -------
            lp : Exchange
                LP exchange
            token_in : ERC20
                specified ERC20 token               
            user_nm : str
                account name
            amount_in : float
               token amount to be swap 
                
            Returns
            -------
            (amount_in, amount_out) : float, float
                token swap amounts                
        """          
        
        amount_in = tDel.delta() if amount_in == None else amount_in
        
        # Step 1: swap
        p_in = self.calc_deposit_portion(lp, token_in, amount_in)
        amount_out = Swap().apply(lp, token_in, user_nm, p_in*amount_in)
        trading_token = self.get_trading_token(lp, token_in)
        
        # Step 2: deposit   
        if(token_in.token_name == lp.token1):
            balance0 = amount_out 
            balance1 = lp.quote(balance0, lp.reserve0, lp.reserve1)
            deposited = balance1 + p_in*amount_in
        elif(token_in.token_name == lp.token0):
            balance1 = amount_out
            balance0 = lp.quote(balance1, lp.reserve1, lp.reserve0) 
            deposited = balance0 + p_in*amount_in
        lp.add_liquidity(user_nm, balance0, balance1, balance0, balance1) 
                            
        return deposited  

    
    def calc_deposit_portion(self, lp, token_in, dx):

        if(token_in.token_name == lp.token0):
            tkn_supply = lp.reserve0
        else:    
            tkn_supply = lp.reserve1

        a = 997*(dx**2)/(1000*tkn_supply)
        b = dx*(1997/1000)
        c = -dx

        alpha = -(b - math.sqrt(b*b - 4*a*c)) / (2*a)
        return alpha 
        
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
        
