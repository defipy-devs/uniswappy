# deposit_test.py
# Author: Ian Moore ( utiliwire@gmail.com )
# Date: Aug 2023

TEST_PATH = "python/test/process/deposit"

import os
import sys
import unittest  
import pytest
import numpy as np 
sys.path.append(os.getcwd().replace(TEST_PATH,""))

from python.prod.erc import ERC20
from python.prod.cpt.factory import UniswapFactory
from python.prod.process.deposit import SwapDeposit
from python.prod.utils.data import UniswapExchangeData

USER0 = 'user0'
USER1 = 'user1' 

class Test_SwapDeposit(unittest.TestCase):
   
    def setup_lp(self, eth, tkn):
        eth_amount = 1000
        tkn_amount = 100000
        factory = UniswapFactory("ETH pool factory", "0x2")
        exchg_data = UniswapExchangeData(tkn0 = eth, tkn1 = tkn, symbol="LP", address="0x011")
        lp_tkn = factory.deploy(exchg_data)
        lp_tkn.add_liquidity(USER0, eth_amount, tkn_amount, eth_amount, tkn_amount)
        return lp_tkn
    
          
    def test_deposit1(self):
        lp_burn = 300
        tkn = ERC20("TKN", "0x111")
        eth = ERC20("ETH", "0x09")        
        lp_tkn = self.setup_lp(eth, tkn)
        deposit_amt = SwapDeposit().apply(lp_tkn, tkn, USER0, 100)

        self.assertEqual(round(deposit_amt,6), 100)
        self.assertEqual(round(lp_tkn.reserve0,6), 1000.0)
        self.assertEqual(round(lp_tkn.reserve1,6), 100100.0)
        
    def test_deposit2(self):
        lp_burn = 300
        tkn = ERC20("TKN", "0x111")
        eth = ERC20("ETH", "0x09")        
        lp_tkn = self.setup_lp(eth, tkn)
        deposit_amt = SwapDeposit().apply(lp_tkn, eth, USER0, 10)

        self.assertEqual(round(deposit_amt,6), 10)    
        self.assertEqual(round(lp_tkn.reserve0,6), 1010.0) 
        self.assertEqual(round(lp_tkn.reserve1,6), 100000.0)
               
if __name__ == '__main__':
    unittest.main()
