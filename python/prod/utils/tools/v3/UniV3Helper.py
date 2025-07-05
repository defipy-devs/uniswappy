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

import math
from decimal import Decimal
from . import TickMath

Q96 = 2**96
GWEI_PRECISION = 18

class UniV3Helper():

    
    """ Uniswap V3 helper functions             
    """       

    def __init__(self):
        pass

    def quote(self, lp, token_in, amt_tkn, lwr_tick, upr_tick):
        
        fee = 997 
        L = lp.get_liquidity()
        if(token_in.token_name == lp.token0):
            sqrtp_cur = Q96/lp.slot0.sqrtPriceX96
            sqrtp_pa = Q96/TickMath.getSqrtRatioAtTick(lwr_tick)
            sqrtp_pb = Q96/TickMath.getSqrtRatioAtTick(upr_tick)       
        elif(token_in.token_name == lp.token1):
            sqrtp_cur = lp.slot0.sqrtPriceX96/Q96
            sqrtp_pa = TickMath.getSqrtRatioAtTick(lwr_tick)/Q96
            sqrtp_pb = TickMath.getSqrtRatioAtTick(upr_tick)/Q96 
     
        sqrtp_next = sqrtp_cur + (fee*amt_tkn) / (L*1000)
        return L * (1/sqrtp_cur - 1/sqrtp_next), sqrtp_next    


    #def get_price_tick(self, human_price):  
    #    return math.floor(math.log((human_price)**2)/math.log(1.0001))   
    
    def get_price_tick(self, lp, pos = 0, human_price = None, tick_space = None):  

        """ get_tick_price
            Get tick price of select token in the exchange pair             
        """          
               
        sqrtPriceX96 = lp.slot0.sqrtPriceX96        
        human_price = (sqrtPriceX96/Q96)**2 if human_price == None else human_price
        tick_p = math.floor(math.log(human_price)/math.log(1.0001))

        tick_space = lp.tickSpacing if tick_space == None else tick_space
        if pos == -1:
            tick_p = tick_p - tick_space
        elif pos == 1:
            tick_p = tick_p + tick_space

        R = tick_p % lp.tickSpacing
        if R > int(lp.tickSpacing/2):
            tick_p += lp.tickSpacing-R
        else:
            tick_p -= R        
 
        return tick_p   
    
    def price_to_tick(self, p):
        return math.floor(math.log(p, 1.0001))    

    def tick_to_price(self, tick):
        return 1.0001**tick   

    def price_to_sqrtp(self, p):
        return int(math.sqrt(p) * Q96)    

    def sqrtp_to_price(self, sqrtp):
        #return sqrtp/(2**99)  
        return sqrtp/Q96  

    def dec2gwei(self, tkn_amt, precision=None):
        precision = GWEI_PRECISION if precision == None else precision
        return int(Decimal(str(tkn_amt))*Decimal(str(10**precision)))
    
    def gwei2dec(self, tkn_amt, precision=None):   
        precision = GWEI_PRECISION if precision == None else precision
        return float(Decimal(str(tkn_amt))/Decimal(str(10**precision)))      

    # see https://atiselsts.github.io/pdfs/uniswap-v3-liquidity-math.pdf
    def calc_Lx(self, p_sqrt_human, dx, lwr_tick, upr_tick):
        pa_sqrt_human = TickMath.getSqrtRatioAtTick(lwr_tick)/Q96
        pb_sqrt_human = TickMath.getSqrtRatioAtTick(upr_tick)/Q96
        assert p_sqrt_human <= pb_sqrt_human, "OOP"
        Lx = dx/(1/max(p_sqrt_human, pa_sqrt_human) - 1/pb_sqrt_human)
        return Lx
    
    def calc_Ly(self, p_sqrt_human, dy, lwr_tick, upr_tick, price_tick=None):
        pa_sqrt_human = TickMath.getSqrtRatioAtTick(lwr_tick)/Q96
        pb_sqrt_human = TickMath.getSqrtRatioAtTick(upr_tick)/Q96
        assert p_sqrt_human >= pa_sqrt_human, "OOP"
        Ly = dy/(min(p_sqrt_human, pb_sqrt_human) - pa_sqrt_human)
        return Ly
