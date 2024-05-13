# Copyright [2023] [Ian Moore]
# Distributed under the MIT License (license terms are at http://opensource.org/licenses/MIT).
# Email: defipy.devs@gmail.com

from ...erc import ERC20
from ...utils.data import UniswapExchangeData
from ...utils.tools.v3 import TickMath

class RebaseIndexToken():
    
    """ 
        Determine rebase amount of index token given a certain amount of liquidity from LP (inverse of SettlementLPToken)  
    """      

    
    def __init__(self):
        pass
     
    def apply(self, lp, tkn, liq_amt, lwr_tick = None, upr_tick = None): 
       
        """ apply

            Apply rebase token calculation settlement; given liquidity amount, what is the reserve amount
                
            Parameters
            -----------------
            lp : UniswapExchange
                Uniswap LP    
            tkn: ERC20
                Token asset from CPT pair       
            liq_amt: float
                Liquidity amount to be priced in in terms of reserve token                 

            Returns
            -----------------
            rebase_amount: float
                Reserve token amount, given liquidity amount
                   
        """        
        if(lp.version == UniswapExchangeData.VERSION_V2):
            settlement = self.calc_univ2_tkn_settlement(lp, tkn, liq_amt)
        elif(lp.version == UniswapExchangeData.VERSION_V3):   
            settlement = self.calc_univ3_tkn_settlement(lp, tkn, liq_amt, lwr_tick, upr_tick)
        
        return settlement
    
    def calc_univ2_tkn_settlement(self, lp, token_in, dL):
            
        (x, y) = self.get_reserves(lp, token_in)
        L = lp.get_liquidity()
        a0 = dL*x/L
        a1 = dL*y/L
        gamma = 997/1000

        dy1 = a1
        dy2 = gamma*a0*(y - a1)/(x - a0 + gamma*a0)
        itkn_amt = dy1 + dy2

        return itkn_amt if itkn_amt > 0 else 0  

    def calc_univ3_tkn_settlement(self, lp, token_in, dL, lwr_tick, upr_tick):
                
        L = lp.get_liquidity()
        L_diff = (L - dL) 
        if(token_in.token_name == lp.token0):
            sqrtp_pa = TickMath.getSqrtRatioAtTick(lwr_tick)/2**96
            sqrtp_pb = TickMath.getSqrtRatioAtTick(upr_tick)/2**96 
            sqrtp_cur = lp.slot0.sqrtPriceX96/2**96 
            dPy = (sqrtp_cur - sqrtp_pa)
            dPx = (1/sqrtp_cur - 1/sqrtp_pb)  
            dx = dL*dPx
            dy = dL*dPy    
            sqrtp_next = sqrtp_cur + (997*dy)/(L_diff*1000) 
            itkn_amt = dx + L_diff * (1/sqrtp_cur - 1/sqrtp_next)
        elif(token_in.token_name == lp.token1):
            sqrtp_cur = 2**96/lp.slot0.sqrtPriceX96
            sqrtp_pa = 2**96/TickMath.getSqrtRatioAtTick(lwr_tick)
            sqrtp_pb = 2**96/TickMath.getSqrtRatioAtTick(upr_tick)
            dPy = (1/sqrtp_cur - 1/sqrtp_pa)
            dPx = (sqrtp_cur - sqrtp_pb)
            dx = dL*dPx
            dy = dL*dPy
            sqrtp_next = sqrtp_cur + (997*dx)/(L_diff*1000) 
            itkn_amt = dy + L_diff * (1/sqrtp_cur - 1/sqrtp_next)

        return itkn_amt if itkn_amt > 0 else 0 
    

    def get_reserves(self, lp, token_in):
        tokens = lp.factory.token_from_exchange[lp.name]
        if(token_in.token_name == lp.token1):
            x = lp.get_reserve(tokens[lp.token0])
            y = lp.get_reserve(tokens[lp.token1])
        else: 
            x = lp.get_reserve(tokens[lp.token1])
            y = lp.get_reserve(tokens[lp.token0])
        return (x, y)          
            