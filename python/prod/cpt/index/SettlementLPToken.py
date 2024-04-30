# Copyright [2023] [Ian Moore]
# Distributed under the MIT License (license terms are at http://opensource.org/licenses/MIT).
# Email: defipy.devs@gmail.com

import numpy as np

class SettlementLPToken():
    
    """ Determine settlement amount of LP token given a certain amount of token    
    """  
    
    def __init__(self):
        pass
     
    def apply(self, lp, tkn, itkn_amt): 
        
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
        
        return self.calc_lp_settlement(lp, tkn, itkn_amt)
    
    def calc_lp_settlement(self, lp, token_in, itkn_amt):

        tokens = lp.factory.token_from_exchange[lp.name]

        if(token_in.token_name == lp.token1):
            x = lp.get_reserve(tokens[lp.token0])
            y = lp.get_reserve(tokens[lp.token1])
        else: 
            x = lp.get_reserve(tokens[lp.token1])
            y = lp.get_reserve(tokens[lp.token0])

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
            