# Copyright [2024] [Ian Moore]
# Distributed under the MIT License (license terms are at http://opensource.org/licenses/MIT).
# Email: defipy.devs@gmail.com

from ...utils.data import UniswapExchangeData
from ...utils.tools.v3 import UniV3Utils
from ...utils.tools.v3 import UniV3Helper
import math

class Join():
    
    """ Process to join x and y amounts to pool              
    """       

    def __init__(self):
        pass

    def apply(self, lp, user_nm, amount0, amount1, lwr_tick = None, upr_tick = None):
        """ apply

            Join x and y amounts to pool
                
            Parameters
            -------
            lp : Exchange
                LP exchange            
            user_nm : str
                account name
            amount0 : float
               x token amount 
            amount1 : float
               y token amount       
            lwr_tick : int
               Lower tick of the position in which to add liquidity   
            upr_tick : int
               Upper tick of the position in which to add liquidity   
                     
            Returns
            -------
            out : dictionary
                join output               
        """ 

        if(lp.version == UniswapExchangeData.VERSION_V2):
            out = lp.add_liquidity(user_nm, amount0, amount1, amount0, amount1)
            
        elif(lp.version == UniswapExchangeData.VERSION_V3):
            init_price = UniV3Utils.encodePriceSqrt(amount1, amount0)
            sqrtP = init_price/2**96
            Ly = UniV3Helper().calc_Ly(sqrtP, amount1, lwr_tick, upr_tick)
            Lx = UniV3Helper().calc_Lx(sqrtP, amount0, lwr_tick, upr_tick)
            L_mint = min(Ly, Lx)    
            lp.initialize(init_price)
            out = lp.mint(user_nm, lwr_tick, upr_tick, L_mint)
             
        return out  