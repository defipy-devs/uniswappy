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

import math
from decimal import Decimal, getcontext
getcontext().prec = 50
from ...utils.data import UniswapExchangeData
from ...utils.tools.v3 import TickMath
from ...utils.tools.v3 import UniV3Helper
from ...utils.tools.v3 import FullMath

class SettlementLPToken():
    
    """ Determine settlement amount of LP token given a certain amount of token    
    """  
    
    def __init__(self):
        pass
     
    def apply(self, lp, tkn, itkn_amt, lwr_tick = None, upr_tick = None): 
        
        """ apply

            Apply LP calculation settlement; given token amount, what is the liquidity amount
                
            Parameters
            -----------------
            lp : UniswapExchange
                Uniswap LP    
            tkn: ERC20
                Token asset from CPT pair       
            itkn_amt: float
                Token reserve amount to be priced in terms of liquidity                 

            Returns
            -----------------
            lp_amount: float
                Liquidity amount given reserve token amount
                   
        """          
        if(lp.version == UniswapExchangeData.VERSION_V2):
            settlement = self.calc_univ2_lp_settlement(lp, tkn, itkn_amt)
        elif(lp.version == UniswapExchangeData.VERSION_V3):   
            settlement = self.calc_univ3_lp_settlement(lp, tkn, itkn_amt, lwr_tick, upr_tick)
        
        return settlement
    
    def calc_univ2_lp_settlement(self, lp, token_in, itkn_amt):

        (x, y) = self.get_reserves(lp, token_in)
        L = lp.get_liquidity()

        x = lp.convert_to_machine(x)
        y = lp.convert_to_machine(y)
        L = lp.convert_to_machine(L)
        itkn_amt = lp.convert_to_machine(itkn_amt)
        
        if(L == 0): 
            return 0
        else:
            gamma = 997
        
            a1 = FullMath.divRoundingUp(x*y,L)
            a2 = L
            a = FullMath.divRoundingUp(a1,a2)
            b = FullMath.divRoundingUp(1000*itkn_amt*x - itkn_amt*gamma*x + 1000*x*y + x*y*gamma,1000*L)
            c = itkn_amt*x;
            
            radicand = b*b - FullMath.divRoundingUp(4*a1*c,a2)
            dL = FullMath.divRoundingUp(b*a2 - a2*math.isqrt(radicand), 2*a1)
            return dL

    def calc_univ3_lp_settlement(self, lp, token_in, itkn_amt, lwr_tick, upr_tick):
        # Full Decimal path to avoid catastrophic cancellation in discriminant
        L = Decimal(str(lp.get_liquidity()))
        Q96 = Decimal(str(2**96))
        itkn_amt = Decimal(str(itkn_amt))
        fee = Decimal(997)

        if(token_in.token_name == lp.token0):
            sqrtp_cur = Decimal(str(lp.slot0.sqrtPriceX96)) / Q96
            sqrtp_pa = Decimal(str(TickMath.getSqrtRatioAtTick(lwr_tick))) / Q96
            sqrtp_pb = Decimal(str(TickMath.getSqrtRatioAtTick(upr_tick))) / Q96
            dPy = sqrtp_cur - sqrtp_pa
            dPx = Decimal(1) / sqrtp_cur - Decimal(1) / sqrtp_pb
        elif(token_in.token_name == lp.token1):
            sqrtp_cur = Q96 / Decimal(str(lp.slot0.sqrtPriceX96))
            sqrtp_pa = Q96 / Decimal(str(TickMath.getSqrtRatioAtTick(lwr_tick)))
            sqrtp_pb = Q96 / Decimal(str(TickMath.getSqrtRatioAtTick(upr_tick)))
            dPx = Decimal(1) / sqrtp_cur - Decimal(1) / sqrtp_pa
            dPy = sqrtp_cur - sqrtp_pb

        a = fee * dPy * sqrtp_cur * dPx - Decimal(1000) * dPx * (sqrtp_cur**2) - fee * dPy
        b = (-fee * dPy * sqrtp_cur * itkn_amt
             + Decimal(1000) * itkn_amt * (sqrtp_cur**2)
             + L * fee * dPy
             + Decimal(1000) * L * dPx * (sqrtp_cur**2))
        c = -Decimal(1000) * L * itkn_amt * (sqrtp_cur**2)

        discriminant = b * b - 4 * a * c
        return float((-b + discriminant.sqrt()) / (2 * a))

    def get_reserves(self, lp, token_in):
        tokens = lp.factory.token_from_exchange[lp.name]

        if(token_in.token_name == lp.token1):
            x = lp.get_reserve(tokens[lp.token0])
            y = lp.get_reserve(tokens[lp.token1])
        else: 
            x = lp.get_reserve(tokens[lp.token1])
            y = lp.get_reserve(tokens[lp.token0])

        return (x, y)  
        
            