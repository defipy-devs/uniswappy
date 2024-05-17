# Copyright [2023] [Ian Moore]
# Distributed under the MIT License (license terms are at http://opensource.org/licenses/MIT).
# Email: defipy.devs@gmail.com

from ..Process import Process
from .Swap import Swap
from ..liquidity import RemoveLiquidity
from ...math.model import TokenDeltaModel
from ...math.model import EventSelectionModel
from ...utils.data import UniswapExchangeData
from ...cpt.index import SettlementLPToken
import math

class WithdrawSwap(Process):
    
    """ Process to withdraw liquidity from LP and swap opposing token which is added to specifed token to receive         
        a single amount of specified token

        Parameters
        ----------
        ev : EventSelectionModel
            EventSelectionModel object to randomly generate buy vs sell events
        tDel : TokenDeltaModel
            TokenDeltaModel to randomly generate token amounts        
    """       

    def __init__(self, ev = None, tDel = None):
        self.ev = EventSelectionModel() if ev  == None else ev
        self.tDel = TokenDeltaModel(50) if tDel == None else tDel
            
    def apply(self, lp, token_out, user_nm, amount_out, lwr_tick = None, upr_tick = None):    
        
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
            lwr_tick : int
                lower tick of the position in which to add liquidity   
            upr_tick : int
                upper tick of the position in which to add liquidity                 
                
            Returns
            -------
            amount_out : float
                amount of withdrawn token               
        """          
        
        amount_out = tDel.delta() if amount_out == None else amount_out
    
        
        if(lp.version == UniswapExchangeData.VERSION_V2):
            # Step 1: withdrawal
            p_out = self._calc_withdraw_portion(lp, token_out, amount_out, lwr_tick, upr_tick)
            removeLiq = RemoveLiquidity()
            res = removeLiq.apply(lp, token_out, user_nm, p_out*amount_out)
    
            # Step 2: swap
            trading_token = self.get_trading_token(lp, token_out)
            out = Swap().apply(lp, trading_token, user_nm, res[trading_token.token_name])  
            withdrawn = out + p_out*amount_out 
            #withdrawn = p_out*amount_out 

        elif(lp.version == UniswapExchangeData.VERSION_V3): 

            p_out = self._calc_withdraw_portion(lp, token_out, amount_out, lwr_tick, upr_tick)
            
             # Step 1: withdrawal
            removeLiq = RemoveLiquidity()
            res = removeLiq.apply(lp, token_out, user_nm, p_out*amount_out, lwr_tick, upr_tick)
        
            # Step 2: swap
            trading_token = self.get_trading_token(lp, token_out)
            out = Swap().apply(lp, trading_token, user_nm, res[trading_token.token_name]) 
            withdrawn = abs(out)  + p_out*amount_out 

        return withdrawn 


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
        
        tokens = lp.factory.token_from_exchange[lp.name]
        trading_token = tokens[lp.token1] if token.token_name == lp.token0 else tokens[lp.token0]
        return trading_token        
 
    def _calc_withdraw_portion(self, lp, token_in, amt, lwr_tick, upr_tick):

        (x, y) = self._get_reserves(lp, token_in)
        L = lp.get_liquidity()
        gamma = 997/1000

        dL = SettlementLPToken().apply(lp, token_in, amt, lwr_tick, upr_tick)
        dx = dL*x/L
        dy = dL*y/L
        aswap = (gamma*dx)*(y-dy)/(x-dx+gamma*dx)

        return dy/amt 

    def _get_reserves(self, lp, token_in):
        tokens = lp.factory.token_from_exchange[lp.name]
        if(lp.version == UniswapExchangeData.VERSION_V2):
            if(token_in.token_name == lp.token1):
                x = lp.get_reserve(tokens[lp.token0])
                y = lp.get_reserve(tokens[lp.token1])
            else: 
                x = lp.get_reserve(tokens[lp.token1])
                y = lp.get_reserve(tokens[lp.token0])
        elif(lp.version == UniswapExchangeData.VERSION_V3):   
            if(token_in.token_name == lp.token1):
                x = lp.get_virtual_reserve(tokens[lp.token0])
                y = lp.get_virtual_reserve(tokens[lp.token1])
            else: 
                x = lp.get_virtual_reserve(tokens[lp.token1])
                y = lp.get_virtual_reserve(tokens[lp.token0]) 
        return (x, y)        
    
        
