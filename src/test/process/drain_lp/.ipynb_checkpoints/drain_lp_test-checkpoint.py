# drain_lp_test.py
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
from python.prod.cpt.index import RebaseIndexToken
from python.prod.defi.process.swap import WithdrawSwap
import numpy as np 

USER0 = 'user0'
USER1 = 'user1' 
LP_AMT = 1500

class Test_DrainLP(unittest.TestCase):
   
    def setup_lp(self, eth, tkn):
        eth_amount = 1000
        tkn_amount = 100000
        iVault = IndexVault('iVault', "0x7")
        factory = Factory("ETH pool factory", "0x2")
        lp_tkn = factory.create_exchange(eth, tkn, symbol="LP", address="0x011")
        lp_tkn.add_liquidity(USER0, eth_amount, tkn_amount, eth_amount, tkn_amount)
        return lp_tkn
        
    def test_drain_lp1(self):
        
        tkn = ERC20("TKN", "0x111")
        eth = ERC20("ETH", "0x09")        
        lp_tkn = self.setup_lp(eth, tkn)        
        
        amt_lp = 250
        N = int(lp_tkn.liquidity_providers[USER0]/amt_lp)

        aggr_withdrawn = 0
        for k in range(N-1):
            itkn_amt = RebaseIndexToken().apply(lp_tkn, tkn, amt_lp)
            aggr_withdrawn += WithdrawSwap().apply(lp_tkn, tkn, USER0, itkn_amt)
            lp_remaining = lp_tkn.liquidity_providers[USER0]

        tol = 1e-5
        itkn_amt = RebaseIndexToken().apply(lp_tkn, tkn, amt_lp-tol)
        aggr_withdrawn += WithdrawSwap().apply(lp_tkn, tkn, USER0, itkn_amt)
        
        self.assertEqual(round(lp_tkn.liquidity_providers[USER0], 7), 0.000010) 
        self.assertEqual(round(aggr_withdrawn,6), 100000.0)  
        self.assertEqual(round(lp_tkn.reserve0,6), 1000.0) 
        self.assertEqual(round(lp_tkn.reserve1,6), 0.0) 
        

if __name__ == '__main__':
    unittest.main()                  