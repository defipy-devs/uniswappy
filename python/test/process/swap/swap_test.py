# swap_test.py
# Author: Ian Moore ( utiliwire@gmail.com )
# Date: Aug 2023

TEST_PATH = "python/test/process/liquidity"

import os
import sys
import unittest   
sys.path.append(os.getcwd().replace(TEST_PATH,""))

from python.prod.erc import ERC20
from python.prod.cpt.factory import UniswapFactory
from python.prod.process.swap import Swap
from python.prod.process.swap import WithdrawSwap
import numpy as np 

USER0 = 'user0'
USER1 = 'user1' 
LP_AMT = 1500

class Test_Swap(unittest.TestCase):
   
    def setup_lp(self, eth, tkn):
        eth_amount = 1000
        tkn_amount = 100000
        factory = UniswapFactory("ETH pool factory", "0x2")
        lp_tkn = factory.create_exchange(eth, tkn, symbol="LP_TKN", address="0x011")
        lp_tkn.add_liquidity(USER0, eth_amount, tkn_amount, eth_amount, tkn_amount)
        return lp_tkn
    
    def test_swap1(self):
        tkn = ERC20("TKN", "0x111")
        eth = ERC20("ETH", "0x09")        
        lp_tkn = self.setup_lp(eth, tkn)
        out = Swap().apply(lp_tkn, tkn, USER0, 1000)
        self.assertEqual(round(lp_tkn.reserve0,6), 990.12842)
      
    def test_swap2(self):
        tkn = ERC20("TKN", "0x111")
        eth = ERC20("ETH", "0x09")        
        lp_tkn = self.setup_lp(eth, tkn)
        out = Swap().apply(lp_tkn, eth, USER0, 10)
        self.assertEqual(round(lp_tkn.reserve1,6), 99012.841966)

if __name__ == '__main__':
    unittest.main()                  