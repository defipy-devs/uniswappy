# Copyright [2023] [Ian Moore]
# Distributed under the MIT License (license terms are at http://opensource.org/licenses/MIT).
# Email: defipy.devs@gmail.com

TEST_PATH = "python/test/process/swap"

import os
import sys
import unittest   
sys.path.append(os.getcwd().replace(TEST_PATH,""))

from python.prod.cpt.factory import UniswapFactory
from python.prod.erc import ERC20
from python.prod.utils.data import UniswapExchangeData
from python.prod.process.swap import WithdrawSwap
from python.prod.process.deposit import SwapDeposit
from python.prod.cpt.index import RebaseIndexToken
from python.prod.cpt.quote import LPQuote

USER_NM = 'user0'
DAI_AMT = 10000
SYS_AMT = 100000

class Test_SwapRevenue(unittest.TestCase):
   
    def setup_lp(self, factory, tkn1, tkn2, lp_nm):
        exchg_data = UniswapExchangeData(tkn0 = tkn1, tkn1 = tkn2, symbol="LP", address="0x011")
        return factory.deploy(exchg_data)
    
        
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

        return itkn_amt          
    
    def setup(self, sys1, dai1):    
        
        factory = UniswapFactory("SYS pool factory", "0x2")
        lp = self.setup_lp(factory, sys1, dai1, 'LP')
        lp.add_liquidity(USER_NM, SYS_AMT, DAI_AMT, SYS_AMT, DAI_AMT)           
                    
        return lp

    
    def test_swap_revenue0(self):
        
        sys1 = ERC20("SYS", "0x09") 
        dai1 = ERC20("DAI", "0x111")
        lp  = self.setup(sys1, dai1)
        
        pre_dai_amt = LPQuote(False).get_amount_from_lp(lp, dai1, 1)
        pre_lp_amt = lp.liquidity_providers[USER_NM]
        pre_sys_reserve = lp.reserve0

        N_RUNS = 100
        for k in range(N_RUNS):
            requested_liquidity_in = 500
            sys_settlement_amt = RebaseIndexToken().apply(lp, sys1, requested_liquidity_in) 
            dep = SwapDeposit().apply(lp, sys1, USER_NM, sys_settlement_amt)
            get_deposit = LPQuote(False).get_amount_from_lp(lp, sys1, lp.last_liquidity_deposit)
            out = WithdrawSwap().apply(lp, sys1, USER_NM, get_deposit)    
           
        post_dai_amt = LPQuote(False).get_amount_from_lp(lp, dai1, 1)
        post_lp_amt = lp.liquidity_providers[USER_NM]
        post_sys_reserve = lp.reserve0
        
        self.assertTrue(round(pre_sys_reserve,8) < round(post_sys_reserve,8))
        self.assertTrue(round(pre_dai_amt,8) == round(post_dai_amt,8))   
        self.assertTrue(round(pre_lp_amt,8) == round(post_lp_amt,8)) 
 
        
if __name__ == '__main__':
    unittest.main()                  