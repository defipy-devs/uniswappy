# RebaseIndexToken.py
# Author: Ian Moore ( utiliwire@gmail.com )
# Date: Aug 2023

from ...erc import ERC20
from ...process.swap import WithdrawSwap

class RebaseIndexToken():
    
    """ Determine rebase amount of index token given a certain amount of liquidity from LP    
    """  
    
    def __init__(self):
        self.fac = ERC20("DAI", "0x09")
     
    def apply(self, lp, tkn, liq_amt): 
        return self.calc_tkn_settlement(lp, tkn, liq_amt)
    
    def calc_tkn_settlement(self, lp, token_in, dL):

        if(token_in.token_name == lp.token1):
            x = lp.reserve0
            y = lp.reserve1
        else: 
            x = lp.reserve1
            y = lp.reserve0

        L = lp.total_supply
        a0 = dL*x/L
        a1 = dL*y/L
        gamma = 997/1000

        dy1 = a1
        dy2 = gamma*a0*(y - a1)/(x - a0 + gamma*a0)
        itkn_amt = dy1 + dy2

        return itkn_amt if itkn_amt > 0 else 0     
            