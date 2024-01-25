# liquidity_leak_test.py
# Author: Ian Moore ( utiliwire@gmail.com )
# Date: Aug 2023

TEST_PATH = "python/test/process/liquidity"

import os
import sys
import unittest   
sys.path.append(os.getcwd().replace(TEST_PATH,""))

from python.prod.cpt.factory import Factory
from python.prod.erc import ERC20
from python.prod.erc import LPERC20
from python.prod.process.liquidity import AddLiquidity
from python.prod.process.liquidity import RemoveLiquidity
from python.prod.cpt.index import RebaseIndexToken
from python.prod.cpt.quote import LPQuote
import numpy as np 

USER_NM = 'user0'
DAI_AMT = 10000
SYS_AMT = 100000

class Test_LiquidityLeak(unittest.TestCase):
   
    def setup_lp(self, factory, tkn1, tkn2, lp_nm):
        return factory.create_exchange(tkn1, tkn2, symbol=lp_nm, address="0x012")      

    def setup(self, sys1, dai1):
        factory = Factory("SYS pool factory", "0x2")
        lp = self.setup_lp(factory, sys1, dai1, 'LP')
        lp.add_liquidity(USER_NM, SYS_AMT, DAI_AMT, SYS_AMT, DAI_AMT)           
        return lp

    
    def test_liquidity_leak0(self):
        
        sys1 = ERC20("SYS", "0x09") 
        dai1 = ERC20("DAI", "0x111")
        lp = self.setup(sys1, dai1)
        
        pre_sys_amt = LPQuote(False).get_amount_from_lp(lp, sys1, 1)
        pre_lp_amt = lp.liquidity_providers[USER_NM]
        
        N_RUNS = 100
        for k in range(N_RUNS):
            lp1_amt = 100
            dai_amount1 = LPQuote(True).get_amount_from_lp(lp, dai1, lp1_amt) 
            price_idai = dai_amount1/lp1_amt 
            AddLiquidity(price_idai).apply(lp, dai1, USER_NM, lp1_amt) 
            RemoveLiquidity().apply(lp, dai1, USER_NM, abs(lp1_amt))          
           
        post_sys_amt = LPQuote(False).get_amount_from_lp(lp, sys1, 1)
        post_lp_amt = lp.liquidity_providers[USER_NM]
        
        self.assertEqual(round(pre_sys_amt,8), round(post_sys_amt,8))   
        self.assertEqual(round(pre_lp_amt,8), round(post_lp_amt,8)) 

       
      
        
if __name__ == '__main__':
    unittest.main()                  