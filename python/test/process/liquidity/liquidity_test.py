# liquidity_test.py
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

USER0 = 'user0'
USER1 = 'user1' 
LP_AMT = 1500

class Test_Liquidity(unittest.TestCase):
   
    def setup_lp(self, eth, tkn):
        eth_amount = 1000
        tkn_amount = 100000
        factory = Factory("ETH pool factory", "0x2")
        lp_tkn = factory.create_exchange(eth, tkn, symbol="LP_TKN", address="0x011")
        lp_tkn.add_liquidity(USER0, eth_amount, tkn_amount, eth_amount, tkn_amount)
        return lp_tkn
            
    def test_liquidity1(self):
        tkn = ERC20("TKN", "0x111")
        eth = ERC20("ETH", "0x09")        
        lp_tkn = self.setup_lp(eth, tkn)
        liq = AddLiquidity().apply(lp_tkn, eth, USER0, 10)     
        self.assertEqual(lp_tkn.reserve0, 1010)
        self.assertEqual(lp_tkn.reserve1, 101000.0)

    def test_liquidity2(self):
        tkn = ERC20("TKN", "0x111")
        eth = ERC20("ETH", "0x09")        
        lp_tkn = self.setup_lp(eth, tkn)
        liq = AddLiquidity().apply(lp_tkn, tkn, USER0, 1000)  
        self.assertEqual(lp_tkn.reserve0, 1010.0)
        self.assertEqual(lp_tkn.reserve1, 101000.0)
        
    def test_liquidity3(self):
        tkn = ERC20("TKN", "0x111")
        eth = ERC20("ETH", "0x09")        
        lp_tkn = self.setup_lp(eth, tkn)
        print(lp_tkn.reserve0)
        liq = RemoveLiquidity().apply(lp_tkn, eth, USER0, 10) 
        self.assertEqual(lp_tkn.reserve0, 990.0)
        self.assertEqual(lp_tkn.reserve1, 99000.0)   
        
    def test_liquidity4(self):
        tkn = ERC20("TKN", "0x111")
        eth = ERC20("ETH", "0x09")        
        lp_tkn = self.setup_lp(eth, tkn)
        print(lp_tkn.reserve0)
        liq = RemoveLiquidity().apply(lp_tkn, tkn, USER0, 1000) 
        self.assertEqual(lp_tkn.reserve0, 990.0)
        self.assertEqual(lp_tkn.reserve1, 99000.0)         

if __name__ == '__main__':
    unittest.main()
