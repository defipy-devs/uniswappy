# withdraw_test.py
# Author: Ian Moore ( imoore@syscoin.org )
# Date: Aug 2023

TEST_PATH = "python/test/defi/process/liquidity"

import os
import sys
import unittest   
sys.path.append(os.getcwd().replace(TEST_PATH,""))

from python.prod.cpt.erc import ERC20
from python.prod.cpt.factory import Factory
from python.prod.cpt.vault import IndexVault
from python.prod.defi.process.swap import Swap
from python.prod.defi.process.swap import WithdrawSwap
import numpy as np 

USER0 = 'user0'
USER1 = 'user1' 
LP_AMT = 1500

class Test_Withdraw(unittest.TestCase):
   
    def setup_lp(self, eth, tkn):
        eth_amount = 1000
        tkn_amount = 100000
        factory = Factory("ETH pool factory", "0x2")
        lp_tkn = factory.create_exchange(eth, tkn, symbol="LP_TKN", address="0x011")
        lp_tkn.add_liquidity(USER0, eth_amount, tkn_amount, eth_amount, tkn_amount)
        return lp_tkn
        
    def test_withdraw1(self):
        tkn = ERC20("TKN", "0x111")
        eth = ERC20("ETH", "0x09")        
        lp_tkn = self.setup_lp(eth, tkn)
        expected_amount_out = WithdrawSwap().apply(lp_tkn, eth, USER0, 1)
        self.assertEqual(round(expected_amount_out,6), 1.0)        
        
    def test_withdraw2(self):
        tkn = ERC20("TKN", "0x111")
        eth = ERC20("ETH", "0x09")        
        lp_tkn = self.setup_lp(eth, tkn)
        expected_amount_out = WithdrawSwap().apply(lp_tkn, tkn, USER0, 100)
        self.assertEqual(round(expected_amount_out,6), 100)  

if __name__ == '__main__':
    unittest.main()                  