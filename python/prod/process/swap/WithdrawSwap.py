# WithdrawSwap.py
# Author: Ian Moore ( utiliwire@gmail.com )
# Date: Aug 2023

from ..Process import Process
from .Swap import Swap
from ..liquidity import RemoveLiquidity
from ...math.model import TokenDeltaModel
from ...math.model import EventSelectionModel
import math

class WithdrawSwap(Process):
    
    """ Process to withdraw liquidity from LP and swap opposing token which is added to specifed token to receive         
        a single amount of specified token

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
            
    def apply(self, lp, token_out, user_nm, amount_out):    
        
        """ apply

            Withdraw liquidity from LP and swap opposing token which is added to specifed token to receive                 
            a single amount of specified token
                
            Parameters
            -------
            lp : Exchange
                LP exchange
            token_out : ERC20
                specified ERC20 token               
            user_nm : str
                account name
            amount_out : float
               token amount to be swap 
                
            Returns
            -------
            amount_out : float
                amount of withdrawn token               
        """          
        
        amount_out = tDel.delta() if amount_out == None else amount_out
    
        # Step 1: withdrawal
        p_out = self.calc_withdraw_portion(lp, token_out, amount_out)
        removeLiq = RemoveLiquidity()
        res = removeLiq.apply(lp, token_out, user_nm, p_out*amount_out)

        # Step 2: swap
        trading_token = self.get_trading_token(lp, token_out)
        out = Swap().apply(lp, trading_token, user_nm, res[trading_token.token_name])  
        withdrawn = out + p_out*amount_out 
        return withdrawn 
 
    def calc_lp_settlement(self, lp, token_in, itkn_amt):

        if(token_in.token_name == lp.token1):
            x = lp.reserve0
            y = lp.reserve1
        else: 
            x = lp.reserve1
            y = lp.reserve0

        L = lp.total_supply
        gamma = 997

        a1 = x*y/L
        a2 = L
        a = a1/a2
        b = (1000*itkn_amt*x - itkn_amt*gamma*x + 1000*x*y + x*y*gamma)/(1000*L);
        c = itkn_amt*x;

        dL = (b*a2 - a2*math.sqrt(b*b - 4*a1*c/a2)) / (2*a1);
        return dL

    def calc_withdraw_portion(self, lp, token_in, amt):

        if(token_in.token_name == lp.token1):
            x = lp.reserve0
            y = lp.reserve1
        else: 
            x = lp.reserve1
            y = lp.reserve0

        L = lp.total_supply
        gamma = 997/1000

        dL = self.calc_lp_settlement(lp, token_in, amt) 
        dx = dL*x/L
        dy = dL*y/L
        aswap = (gamma*dx)*(y-dy)/(x-dx+gamma*dx)

        return dy/amt      

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
        
