# ─────────────────────────────────────────────────────────────────────────────
# Apache 2.0 License (DeFiPy)
# ─────────────────────────────────────────────────────────────────────────────
# Copyright 2023–2025 Ian Moore
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
# limitations under the License.

from math import sqrt
from ...cpt.quote import LPQuote
from ...utils.tools.v3 import TickMath

class UniswapImpLoss:
    def __init__(self, lp, lp_init_amt, lwr_tick = None, upr_tick = None):
        self.lp = lp
        self.lp_init = lp_init_amt
        self.x_tkn_init = self._calc_dx(lp_init_amt, upr_tick)
        self.y_tkn_init = self._calc_dy(lp_init_amt, lwr_tick)

    def current_position_value(self, tkn, lwr_tick = None, upr_tick = None):
        """Calculate the current value of the LP position in terms of input token.""" 
        return LPQuote(False).get_amount_from_lp(self.lp, tkn, self.lp_init, lwr_tick, upr_tick)

    def hold_value(self, tkn):
        """Calculate the value if initial tokens were held."""
        tokens = self.lp.factory.token_from_exchange[self.lp.name]
        if(tkn.token_name == self.lp.token0):
            current_price = self.lp.get_price(tokens[self.lp.token1])
            val = self.y_tkn_init*current_price + self.x_tkn_init
        elif(tkn.token_name == self.lp.token1):   
            current_price = self.lp.get_price(tokens[self.lp.token0])
            val = self.x_tkn_init * current_price + self.y_tkn_init
        return val 

    def get_init_amt(self, tkn):
        if(tkn.token_name == self.lp.token0):
            return self.x_tkn_init
        elif(tkn.token_name == self.lp.token1):  
            return self.y_tkn_init

    def apply(self, lwr_tick = None, upr_tick = None, fees = False):

        if(fees):
            """Calculate returns based current position."""
            tokens = self.lp.factory.token_from_exchange[self.lp.name]
            x_tkn = tokens[self.lp.token0]
            v_hold = self.hold_value(x_tkn)
            v_pos = self.current_position_value(x_tkn, lwr_tick, upr_tick)
            iloss = (v_pos - v_hold)/v_hold
        else:
            """Calculate IL based on price ratio."""
            tokens = self.lp.factory.token_from_exchange[self.lp.name]
            x_tkn = tokens[self.lp.token0]
            y_tkn = tokens[self.lp.token1]
            initial_price = self.y_tkn_init / self.x_tkn_init
            current_price = self.lp.get_price(x_tkn)
            alpha = current_price / initial_price
            if(self.lp.version == 'V2'):
                iloss = self.calc_iloss(alpha)
            elif(self.lp.version == 'V3'):    
                r = self.calc_price_range(lwr_tick, upr_tick)
                iloss = self.calc_iloss(alpha, r)       

        return iloss

    def calc_iloss(self, alpha, r = None):
        if(r == None):
            return (2 * sqrt(alpha)) / (1 + alpha) - 1
        else:
            iloss = (2 * sqrt(alpha)) / (1 + alpha) - 1
            scale =  sqrt(r)/(sqrt(r)-1)
            return scale*iloss 

    def calc_price_range(self, lwr_tick, upr_tick):
        Q96 = 2**96
        sqrtp_cur = self.lp.slot0.sqrtPriceX96/Q96
        sqrtp_pb = TickMath.getSqrtRatioAtTick(upr_tick)/Q96
        sqrtp_pa = TickMath.getSqrtRatioAtTick(lwr_tick)/Q96
        ra = sqrtp_pa**2/sqrtp_cur**2
        rb = sqrtp_pb**2/sqrtp_cur**2    
        return sum([ra,rb])/2

    def _calc_dx(self, dL, upr_tick = None):
        if(self.lp.version == 'V2'):
            return self._calc_univ2_dx(dL)
        elif(self.lp.version == 'V3'): 
            return self._calc_univ3_dx(dL, upr_tick)

    def _calc_dy(self, dL, lwr_tick = None):
        if(self.lp.version == 'V2'):
            return self._calc_univ2_dy(dL)
        elif(self.lp.version == 'V3'): 
            return self._calc_univ3_dy(dL, lwr_tick)
        
    def _calc_univ2_dx(self, dL):
        tokens = self.lp.factory.token_from_exchange[self.lp.name]
        x_tkn = tokens[self.lp.token0]
        x = self.lp.get_reserve(x_tkn)
        L = self.lp.get_liquidity()
        return x*dL/L

    def _calc_univ2_dy(self, dL):
        tokens = self.lp.factory.token_from_exchange[self.lp.name]
        y_tkn = tokens[self.lp.token1]
        y = self.lp.get_reserve(y_tkn)
        L = self.lp.get_liquidity()
        return y*dL/L
    
    def _calc_univ3_dx(self, dL, upr_tick):
        Q96 = 2**96
        sqrtp_pb = TickMath.getSqrtRatioAtTick(upr_tick)/Q96
        sqrtp_cur = self.lp.slot0.sqrtPriceX96/Q96
        dPx = (1/sqrtp_cur - 1/sqrtp_pb)     
        return dL*dPx

    def _calc_univ3_dy(self, dL, lwr_tick):
        Q96 = 2**96
        sqrtp_pa = TickMath.getSqrtRatioAtTick(lwr_tick)/Q96
        sqrtp_cur = self.lp.slot0.sqrtPriceX96/Q96
        dPy = (sqrtp_cur - sqrtp_pa) 
        return dL*dPy