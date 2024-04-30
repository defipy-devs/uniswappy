# Copyright [2023] [Ian Moore]
# Distributed under the MIT License (license terms are at http://opensource.org/licenses/MIT).
# Email: defipy.devs@gmail.com

from ...erc import ERC20
from ...process.swap import WithdrawSwap

class RebaseIndexToken():
    
    """ 
        Determine rebase amount of index token given a certain amount of liquidity from LP (inverse of SettlementLPToken)  
    """      

    
    def __init__(self):
        self.fac = ERC20("DAI", "0x09")
     
    def apply(self, lp, tkn, liq_amt): 
       
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
        
        return self.calc_tkn_settlement(lp, tkn, liq_amt)
    
    def calc_tkn_settlement(self, lp, token_in, dL):

        tokens = lp.factory.token_from_exchange[lp.name]

        if(token_in.token_name == lp.token1):
            x = lp.get_reserve(tokens[lp.token0])
            y = lp.get_reserve(tokens[lp.token1])
        else: 
            x = lp.get_reserve(tokens[lp.token1])
            y = lp.get_reserve(tokens[lp.token0])

        L = lp.get_liquidity()
        a0 = dL*x/L
        a1 = dL*y/L
        gamma = 997/1000

        dy1 = a1
        dy2 = gamma*a0*(y - a1)/(x - a0 + gamma*a0)
        itkn_amt = dy1 + dy2

        return itkn_amt if itkn_amt > 0 else 0     
            