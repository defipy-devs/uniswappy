# Copyright [2023] [Ian Moore]
# Distributed under the MIT License (license terms are at http://opensource.org/licenses/MIT).
# Email: defipy.devs@gmail.com

TEST_PATH = "python/test/process/liquidity"

import os
import sys
import unittest   
sys.path.append(os.getcwd().replace(TEST_PATH,""))

from python.prod.cpt.factory import UniswapFactory
from python.prod.erc import ERC20
from python.prod.process.liquidity import AddLiquidity
from python.prod.process.liquidity import RemoveLiquidity
from python.prod.utils.data import UniswapExchangeData

USER0 = 'user0'
USER1 = 'user1' 
LP_AMT = 1500

class Test_Liquidity(unittest.TestCase):
   
    def setup_lp(self, eth, tkn):
        eth_amount = 1000
        tkn_amount = 100000
        factory = UniswapFactory("ETH pool factory", "0x2")
        exchg_data = UniswapExchangeData(tkn0 = eth, tkn1 = tkn, symbol="LP", address="0x011")
        lp_tkn = factory.deploy(exchg_data)
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
