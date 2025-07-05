# ─────────────────────────────────────────────────────────────────────────────
# Apache 2.0 License (DeFiPy)
# ─────────────────────────────────────────────────────────────────────────────
# Copyright 2023–2025 Ian Moore
# Email: defipy.devs@gmail.com
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License

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