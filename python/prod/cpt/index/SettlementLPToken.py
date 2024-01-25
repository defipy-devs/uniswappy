# SettlementLPToken.py
# Author: Ian Moore ( utiliwire@gmail.com )
# Date: Sept 2023

import math

class SettlementLPToken():
    
    """ Determine settlement amount of LP token given a certain amount of token    
    """  
    
    def __init__(self):
        pass
     
    def apply(self, lp, tkn, itkn_amt): 
        return self.calc_lp_settlement(lp, tkn, itkn_amt)
    
    def calc_lp_settlement(self, lp, token_in, itkn_amt):

        if(token_in.token_name == lp.token1):
            x = lp.reserve0
            y = lp.reserve1
        else: 
            x = lp.reserve1
            y = lp.reserve0

        L = lp.total_supply
        if(L == 0): 
            return 0
        else:
            gamma = 997

            a1 = x*y/L
            a2 = L
            a = a1/a2
            b = (1000*itkn_amt*x - itkn_amt*gamma*x + 1000*x*y + x*y*gamma)/(1000*L);
            c = itkn_amt*x;

            dL = (b*a2 - a2*math.sqrt(b*b - 4*a1*c/a2)) / (2*a1);
            return dL      
            