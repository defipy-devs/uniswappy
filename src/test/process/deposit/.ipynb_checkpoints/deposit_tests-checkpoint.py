TEST_PATH = "python/test/defi/process/deposit"

import os
import sys
import unittest  
import numpy as np 
sys.path.append(os.getcwd().replace(TEST_PATH,""))

from python.prod.cpt.erc import ERC20
from python.prod.cpt.factory import Factory
from python.prod.cpt.vault import IndexVault
from python.prod.defi.process.deposit import SwapDeposit

USER0 = 'user0'
USER1 = 'user1' 

class Test_SwapDeposit(unittest.TestCase):
   
    def setup_lp(self, eth, tkn):
        eth_amount = 1000
        tkn_amount = 100000
        factory = Factory("ETH pool factory", "0x2")
        lp_tkn = factory.create_exchange(eth, tkn, symbol="LP_TKN", address="0x011")
        lp_tkn.add_liquidity(USER0, eth_amount, tkn_amount, eth_amount, tkn_amount)
        return lp_tkn
    
          
    def test_deposit1(self):
        lp_burn = 300
        tkn = ERC20("TKN", "0x111")
        eth = ERC20("ETH", "0x09")        
        lp_tkn = self.setup_lp(eth, tkn)
        dep = SwapDeposit().apply(lp_tkn, tkn, USER0, 100)
        self.assertEqual(lp_tkn.reserve0, 1000.0)
        self.assertEqual(lp_tkn.reserve1, 100100.025)
        
    def test_deposit2(self):
        lp_burn = 300
        tkn = ERC20("TKN", "0x111")
        eth = ERC20("ETH", "0x09")        
        lp_tkn = self.setup_lp(eth, tkn)
        dep = SwapDeposit().apply(lp_tkn, eth, USER0, 10)
        self.assertEqual(lp_tkn.reserve0, 1010.025) 
        self.assertEqual(lp_tkn.reserve1, 100000.0)
               
        

if __name__ == '__main__':
    unittest.main()
