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

class Test_UniV3Tick(unittest.TestCase):

    def setup_deploy(self, factory, tkn1, tkn2, tick_spacing, fee):
        exchg_data = UniswapExchangeData(tkn0 = tkn1, tkn1 = tkn2, symbol="LP", 
                                           address="0x011", version = UniswapExchangeData.VERSION_V3, 
                                           precision = UniswapExchangeData.TYPE_GWEI,
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

    def test_init_tick(self):
        (_, _, lp) = self.setup_lp_mint()   
        assert lp.slot0.tick == -23028   

    def test_transferToken0_only(self):
        (_, _, lp) = self.setup_lp_mint() 
        (amt0, amt1) = lp.mint(USER_ACCT, -22980, 0, 10000)
        assert amt0 != 0
        assert amt1 == 0  

    def test_maxTick_maxLeverage(self):
        upr_tick = getMaxTick(TICK_SPACINGS[FeeAmount.MEDIUM])
        tick_spacing = TICK_SPACINGS[FeeAmount.MEDIUM]
        (_, _, lp) = self.setup_lp_mint() 
        (amt0, amt1) = lp.mint(USER_ACCT, upr_tick - tick_spacing, upr_tick, 2**102)   
        assert amt0 == 828011525
        assert amt1 == 0    

    def test_maxTick(self):
        upr_tick = getMaxTick(TICK_SPACINGS[FeeAmount.MEDIUM])
        (_, _, lp) = self.setup_lp_mint() 
        (amt0, amt1) = lp.mint(USER_ACCT,  -22980, upr_tick, 10000)  
        assert amt0 == 31549
        assert amt1 == 0  

    def test_remove_aboveCurrentPrice(self):
        (_, _, lp) = self.setup_lp_mint() 
        lp.mint(USER_ACCT, -240, 0, 10000)
        lp.burn(USER_ACCT, -240, 0, 10000)
        (_, _, _, amt0, amt1) = lp.collect(
            USER_ACCT, -240, 0, MAX_UINT128, MAX_UINT128
        )
        assert amt0 == 120
        assert amt1 == 0 

    def test_addLiquidity_toLiquidityGross(self):
        tick_spacing = TICK_SPACINGS[FeeAmount.MEDIUM]
        (_, _, lp) = self.setup_lp_mint() 
        lp.mint(USER_ACCT, -240, 0, 100)
        assert lp.ticks[-240].liquidityGross == 100
        assert lp.ticks[0].liquidityGross == 100
        # No liquidityGross === tick doesn't exist
        assert not lp.ticks.__contains__(tick_spacing)
        assert not lp.ticks.__contains__(tick_spacing * 2)
        lp.mint(USER_ACCT, -240, tick_spacing, 150)
        assert lp.ticks[-240].liquidityGross == 250
        assert lp.ticks[0].liquidityGross == 100
        assert lp.ticks[tick_spacing].liquidityGross == 150
        # No liquidityGross === tick doesn't exist
        assert not lp.ticks.__contains__(tick_spacing * 2)
        lp.mint(USER_ACCT, 0, tick_spacing * 2, 60)
        assert lp.ticks[-240].liquidityGross == 250
        assert lp.ticks[0].liquidityGross == 160
        assert lp.ticks[tick_spacing].liquidityGross == 150
        assert lp.ticks[tick_spacing * 2].liquidityGross == 60  

    def test_removeLiquidity_fromLiquidityGross(self):
        (_, _, lp) = self.setup_lp_mint() 
        lp.mint(USER_ACCT, -240, 0, 100)
        lp.mint(USER_ACCT, -240, 0, 40)
        lp.burn(USER_ACCT, -240, 0, 90)
        assert lp.ticks[-240].liquidityGross == 50
        assert lp.ticks[0].liquidityGross == 50 

    def test_clearTickLower_ifLastPositionRemoved(self):
        (_, _, lp) = self.setup_lp_mint() 
        lp.mint(USER_ACCT, -240, 0, 100)
        lp.burn(USER_ACCT, -240, 0, 100)
        # tick cleared == not in ticks
        assert not lp.ticks.__contains__(-240) 

    def test_clearTickUpper_ifLastPositionRemoved(self):
        (_, _, lp) = self.setup_lp_mint() 
        lp.mint(USER_ACCT, -240, 0, 100)
        lp.burn(USER_ACCT, -240, 0, 100)
        # tick cleared == not in ticks
        assert not lp.ticks.__contains__(0)

    def test_clearsTick_ifNotUser(self):
        tick_spacing = TICK_SPACINGS[FeeAmount.MEDIUM]
        (_, _, lp) = self.setup_lp_mint() 
        lp.mint(USER_ACCT, -240, 0, 100)
        lp.mint(USER_ACCT, -tick_spacing, 0, 250)
        lp.burn(USER_ACCT, -240, 0, 100)
        # tick cleared == not in ticks
        assert not lp.ticks.__contains__(-240)
        tickInfo = lp.ticks[-tick_spacing]
        assert tickInfo.liquidityGross == 250
        assert tickInfo.feeGrowthOutside0X128 == 0
        assert tickInfo.feeGrowthOutside1X128 == 0 

    # Including current price
    def test_transferCurrentPriceTokens(self):
        tick_spacing = TICK_SPACINGS[FeeAmount.MEDIUM]
        lwr_tick = getMinTick(TICK_SPACINGS[FeeAmount.MEDIUM])
        upr_tick = getMaxTick(TICK_SPACINGS[FeeAmount.MEDIUM])        
        (_, _, lp) = self.setup_lp_mint() 
        (amt0, amt1) = lp.mint(
            USER_ACCT, lwr_tick + tick_spacing, upr_tick - tick_spacing, 100
        )
        assert amt0 == 317
        assert amt1 == 32

    def test_initializes_lowerTick(self):
        tick_spacing = TICK_SPACINGS[FeeAmount.MEDIUM]
        lwr_tick = getMinTick(TICK_SPACINGS[FeeAmount.MEDIUM])
        upr_tick = getMaxTick(TICK_SPACINGS[FeeAmount.MEDIUM])          
        (_, _, lp) = self.setup_lp_mint() 
        lp.mint(USER_ACCT, lwr_tick + tick_spacing, upr_tick - tick_spacing, 100)
        liquidityGross = lp.ticks[lwr_tick + tick_spacing].liquidityGross
        assert liquidityGross == 100 

    def test_initializes_upperTick(self):
        tick_spacing = TICK_SPACINGS[FeeAmount.MEDIUM]
        lwr_tick = getMinTick(TICK_SPACINGS[FeeAmount.MEDIUM])
        upr_tick = getMaxTick(TICK_SPACINGS[FeeAmount.MEDIUM])          
        (_, _, lp) = self.setup_lp_mint() 
        lp.mint(USER_ACCT, lwr_tick + tick_spacing, upr_tick - tick_spacing, 100)
        liquidityGross = lp.ticks[upr_tick - tick_spacing].liquidityGross
        assert liquidityGross == 100  

    def test_works_minMaxTick(self):
        lwr_tick = getMinTick(TICK_SPACINGS[FeeAmount.MEDIUM])
        upr_tick = getMaxTick(TICK_SPACINGS[FeeAmount.MEDIUM])          
        (_, _, lp) = self.setup_lp_mint() 
        (amt0, amt1) = lp.mint(USER_ACCT, lwr_tick, upr_tick, 10000)
        assert amt0 == 31623
        assert amt1 == 3163                   
                                                                      
    def test_removing_includesCurrentPrice(self):
        tick_spacing = TICK_SPACINGS[FeeAmount.MEDIUM]
        lwr_tick = getMinTick(TICK_SPACINGS[FeeAmount.MEDIUM])
        upr_tick = getMaxTick(TICK_SPACINGS[FeeAmount.MEDIUM])          
        (_, _, lp) = self.setup_lp_mint() 
        lp.mint(USER_ACCT, lwr_tick + tick_spacing, upr_tick - tick_spacing, 100)
        lp.burn(USER_ACCT, lwr_tick + tick_spacing, upr_tick - tick_spacing, 100)
        (_, _, _, amt0, amt1) = lp.collect(
            USER_ACCT,
            lwr_tick + tick_spacing,
            upr_tick - tick_spacing,
            MAX_UINT128,
            MAX_UINT128,
        )
        assert amt0 == 316
        assert amt1 == 31

    def test_transfer_onlyToken1(self):
        tick_spacing = TICK_SPACINGS[FeeAmount.MEDIUM]
        lwr_tick = getMinTick(TICK_SPACINGS[FeeAmount.MEDIUM])
        upr_tick = getMaxTick(TICK_SPACINGS[FeeAmount.MEDIUM])          
        (_, _, lp) = self.setup_lp_mint() 
        (amt0, amt1) = lp.mint(USER_ACCT, -46080, -23040, 10000)
        assert amt0 == 0
        assert amt1 == 2162

    def test_minTick_maxLeverage(self):
        tick_spacing = TICK_SPACINGS[FeeAmount.MEDIUM]
        lwr_tick = getMinTick(TICK_SPACINGS[FeeAmount.MEDIUM])
        upr_tick = getMaxTick(TICK_SPACINGS[FeeAmount.MEDIUM])          
        (_, _, lp) = self.setup_lp_mint() 
        (amt0, amt1) = lp.mint(USER_ACCT, lwr_tick, lwr_tick + tick_spacing, 2**102)
        assert amt0 == 0
        assert amt1 == 828011520

    def test_works_minTick(self):
        tick_spacing = TICK_SPACINGS[FeeAmount.MEDIUM]
        lwr_tick = getMinTick(TICK_SPACINGS[FeeAmount.MEDIUM])
        upr_tick = getMaxTick(TICK_SPACINGS[FeeAmount.MEDIUM])          
        (_, _, lp) = self.setup_lp_mint() 
        (amt0, amt1) = lp.mint(USER_ACCT, lwr_tick, -23040, 10000)
        assert amt0 == 0
        assert amt1 == 3161


    def test_removing_belowCurrentPrice(self):
        tick_spacing = TICK_SPACINGS[FeeAmount.MEDIUM]
        lwr_tick = getMinTick(TICK_SPACINGS[FeeAmount.MEDIUM])
        upr_tick = getMaxTick(TICK_SPACINGS[FeeAmount.MEDIUM])          
        (_, _, lp) = self.setup_lp_mint() 
        lp.mint(USER_ACCT, -46080, -46020, 10000)
        lp.burn(USER_ACCT, -46080, -46020, 10000)
        (_, _, _, amt0, amt1) = lp.collect(
            USER_ACCT, -46080, -46020, MAX_UINT128, MAX_UINT128
        )
        assert amt0 == 0
        assert amt1 == 3                           
         
if __name__ == '__main__':
    unittest.main()    