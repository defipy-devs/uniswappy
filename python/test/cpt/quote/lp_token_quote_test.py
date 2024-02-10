# liquidity_leak_test.py
# Author: Ian Moore ( utiliwire@gmail.com )
# Date: Aug 2023

TEST_PATH = "python/test/defi/process/liquidity"

import os
import sys
import unittest   
sys.path.append(os.getcwd().replace(TEST_PATH,""))

from python.prod.cpt.factory import UniswapFactory
from python.prod.erc import ERC20
from python.prod.utils.data import UniswapExchangeData
from python.prod.cpt.quote import LPQuote
import numpy as np 

USER_NM = 'user0'
DAI_AMT = 10000
SYS_AMT = 100000

class Test_LPTokenQuote(unittest.TestCase):
   
    def setup_lp(self, factory, tkn1, tkn2, lp_nm):
        exchg_data = UniswapExchangeData(tkn0 = tkn1, tkn1 = tkn2, symbol="LP", address="0x011")
        return factory.deploy(exchg_data)
              
    
    def setup(self, sys1, dai1):
          
        
        factory = UniswapFactory("SYS pool factory", "0x2")
        lp = self.setup_lp(factory, sys1, dai1, 'LP')
        lp.add_liquidity(USER_NM, SYS_AMT, DAI_AMT, SYS_AMT, DAI_AMT)           
               
        return lp

    
    def test_lp_token_quote0(self):
        
        sys1 = ERC20("SYS", "0x09") 
        dai1 = ERC20("DAI", "0x111")
        lp = self.setup(sys1, dai1)
               
        amt_lp = LPQuote(False).get_lp_from_amount(lp, sys1, 100)        
        self.assertEqual(round(amt_lp,8), round(15.83908989, 8))         
   
        
          
        
if __name__ == '__main__':
    unittest.main()                  