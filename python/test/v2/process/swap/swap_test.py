# Copyright [2023] [Ian Moore]
# Distributed under the MIT License (license terms are at http://opensource.org/licenses/MIT).
# Email: defipy.devs@gmail.com

TEST_PATH = "python/test/process/liquidity"

import os
import sys
import unittest   
sys.path.append(os.getcwd().replace(TEST_PATH,""))

from python.prod.erc import ERC20
from python.prod.cpt.factory import UniswapFactory
from python.prod.process.swap import Swap
from python.prod.utils.data import UniswapExchangeData

USER0 = 'user0'
USER1 = 'user1' 
LP_AMT = 1500

class Test_Swap(unittest.TestCase):
   
    def setup_lp(self, eth, tkn):
        eth_amount = 1000
        tkn_amount = 100000
        factory = UniswapFactory("ETH pool factory", "0x2")
        exchg_data = UniswapExchangeData(tkn0 = eth, tkn1 = tkn, symbol="LP", address="0x011")
        lp_tkn = factory.deploy(exchg_data)
        lp_tkn.add_liquidity(USER0, eth_amount, tkn_amount, eth_amount, tkn_amount)
        return lp_tkn
    
    def test_swap1(self):
        tkn = ERC20("TKN", "0x111")
        eth = ERC20("ETH", "0x09")        
        lp_tkn = self.setup_lp(eth, tkn)
        out = Swap().apply(lp_tkn, tkn, USER0, 1000)
        self.assertEqual(round(lp_tkn.get_reserve(eth),6), 990.12842)
      
    def test_swap2(self):
        tkn = ERC20("TKN", "0x111")
        eth = ERC20("ETH", "0x09")        
        lp_tkn = self.setup_lp(eth, tkn)
        out = Swap().apply(lp_tkn, eth, USER0, 10)
        self.assertEqual(round(lp_tkn.get_reserve(tkn),6), 99012.841966)

if __name__ == '__main__':
    unittest.main()                  