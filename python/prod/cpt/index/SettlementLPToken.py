# Copyright [2023] [Ian Moore]
# Distributed under the MIT License (license terms are at http://opensource.org/licenses/MIT).
# Email: defipy.devs@gmail.com

import numpy as np
import math
from ...utils.data import UniswapExchangeData
from ...utils.tools.v3 import TickMath


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
        if(L == 0): 
            return 0
        else:
            gamma = 997

            a1 = x*y/L
            a2 = L
            a = a1/a2
            b = (1000*itkn_amt*x - itkn_amt*gamma*x + 1000*x*y + x*y*gamma)/(1000*L);
            c = itkn_amt*x;

            dL = (b*a2 - a2*np.sqrt(b*b - 4*a1*c/a2)) / (2*a1);
            return dL  

    def calc_univ3_lp_settlement(self, lp, token_in, itkn_amt, lwr_tick, upr_tick):
    
        L = lp.get_liquidity()
        if(token_in.token_name == lp.token0):
            sqrtp_cur = lp.slot0.sqrtPriceX96/2**96
            sqrtp_pa = TickMath.getSqrtRatioAtTick(lwr_tick)/2**96
            sqrtp_pb = TickMath.getSqrtRatioAtTick(upr_tick)/2**96 
            dPy = (sqrtp_cur - sqrtp_pa)
            dPx = (1/sqrtp_cur - 1/sqrtp_pb)          
        elif(token_in.token_name == lp.token1):
            sqrtp_cur = 2**96/lp.slot0.sqrtPriceX96
            sqrtp_pa = 2**96/TickMath.getSqrtRatioAtTick(lwr_tick)
            sqrtp_pb = 2**96/TickMath.getSqrtRatioAtTick(upr_tick)
            dPx = (1/sqrtp_cur - 1/sqrtp_pa)
            dPy = (sqrtp_cur - sqrtp_pb)
    
        fee = 997
        
        a = fee*dPy*sqrtp_cur*dPx - 1000*dPx*(sqrtp_cur**2) - fee*dPy  
        b = -fee*dPy*sqrtp_cur*itkn_amt + 1000*itkn_amt*(sqrtp_cur**2) + L*fee*dPy + 1000*L*dPx*(sqrtp_cur**2)
        c = -1000*L*itkn_amt*(sqrtp_cur**2)
    
        return (-b + math.sqrt(b*b - 4*a*c)) / (2*a)  

    def get_reserves(self, lp, token_in):
        tokens = lp.factory.token_from_exchange[lp.name]

        if(token_in.token_name == lp.token1):
            x = lp.get_reserve(tokens[lp.token0])
            y = lp.get_reserve(tokens[lp.token1])
        else: 
            x = lp.get_reserve(tokens[lp.token1])
            y = lp.get_reserve(tokens[lp.token0])

        return (x, y)  
            