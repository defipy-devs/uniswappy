# Copyright [2023] [Ian Moore]
# Distributed under the MIT License (license terms are at http://opensource.org/licenses/MIT).
# Email: defipy.devs@gmail.com

from ..Process import Process
from ...math.model import TokenDeltaModel
from ...math.model import EventSelectionModel
from ...utils.data import UniswapExchangeData


class RemoveLiquidity(Process):
    
    """ Remove liquidity process

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
            
    def apply(self, lp, token_in, user_nm, amount_in, lwr_tick = None, upr_tick = None):    
        
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
            lwr_tick : int
                lower tick of the position in which to add liquidity   
            upr_tick : int
                upper tick of the position in which to add liquidity                
                
            Returns
            -------
            reserve amounts : dictionary
                dictionary of reserve amounts                
        """          
        
        amount_in = self.tDel.delta() if amount_in == None else amount_in
        tokens = lp.factory.token_from_exchange[lp.name]  

        if(lp.version == UniswapExchangeData.VERSION_V2):

            res0 = lp.get_reserve(tokens[lp.token0])
            res1 = lp.get_reserve(tokens[lp.token1])
            tot_liq = lp.get_liquidity()
            
            if(token_in.token_name == lp.token0):
                liq = amount_in*tot_liq/res0
                amount1 = liq*res1/tot_liq
                amount0, amount1 = lp.remove_liquidity(user_nm, liq, amount_in, amount1) 
            elif(token_in.token_name == lp.token1): 
                liq = amount_in*tot_liq/res1
                amount0 = liq*res0/tot_liq
                amount0, amount1 = lp.remove_liquidity(user_nm, liq, amount0, amount_in) 

        elif(lp.version == UniswapExchangeData.VERSION_V3):  

            tot_liq = lp.get_liquidity()
            sqrt_P = lp.slot0.sqrtPriceX96/2**96

            if(token_in.token_name == lp.token0):
                liq = amount_in*sqrt_P
                (_, _, _, _, amount0, amount1) = lp.burn(user_nm, lwr_tick, upr_tick, liq)
            elif(token_in.token_name == lp.token1): 
                liq = amount_in/sqrt_P
                (_, _, _, _, amount0, amount1) = lp.burn(user_nm, lwr_tick, upr_tick, liq)        
        
            
        return {lp.token0:amount0, lp.token1:amount1}    
    
 
        
