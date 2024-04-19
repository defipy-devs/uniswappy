# Copyright [2023] [Ian Moore]
# Distributed under the MIT License (license terms are at http://opensource.org/licenses/MIT).
# Email: defipy.devs@gmail.com

TEST_PATH = "python/test/defi/process/liquidity"

import os
import sys
import unittest   
sys.path.append(os.getcwd().replace(TEST_PATH,""))

from python.prod.cpt.factory import UniswapFactory
from python.prod.erc import ERC20
from python.prod.utils.data import UniswapExchangeData
from python.prod.cpt.quote import LPQuote
from python.test.v3.utilities import *
import numpy as np 

USER_ACCT = 'user0'
USDC_AMT = 1000
DAI_AMT = 1000

class Test_UniV3Swaps(unittest.TestCase):

    def setup_deploy(self, factory, tkn1, tkn2, tick_spacing, fee):
        exchg_data = UniswapExchangeData(tkn0 = tkn1, tkn1 = tkn2, symbol="LP", 
                                           address="0x011", version = UniswapExchangeData.VERSION_V3, 
                                           tick_spacing = tick_spacing, fee = fee)
        return factory.deploy(exchg_data)
              
    
    def setup_lp(self, tkn1, tkn2):
        fee = FeeAmount.MEDIUM
        tick_spacing = TICK_SPACINGS[FeeAmount.MEDIUM]
        factory = UniswapFactory("TEST pool factory", "0x2")
        lp = self.setup_deploy(factory, tkn1, tkn2, tick_spacing, fee)  
        lp.initialize(encodePriceSqrt(1, 10))    
        return lp

    def setup_lp_mint(self):  
        lwr_tick = getMinTick(TICK_SPACINGS[FeeAmount.MEDIUM])
        upr_tick = getMaxTick(TICK_SPACINGS[FeeAmount.MEDIUM])
        usdc = ERC20("USDC", "0x09") 
        dai = ERC20("DAI", "0x111")
        lp = self.setup_lp(usdc, dai)
        (amt0, amt1)  = lp.mint(USER_ACCT, lwr_tick, upr_tick, 3161) 
        return (amt0, amt1, lp)        

    def test_lp_mint1(self): 
        (amt0, amt1, _) = self.setup_lp_mint()    
        assert amt0 == 9996
        assert amt1 == 1000 

                       
         
if __name__ == '__main__':
    unittest.main()    