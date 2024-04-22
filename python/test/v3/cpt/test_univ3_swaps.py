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

USER_ACCT0 = 'user0'
USER_ACCT1 = 'user1'
USDC_AMT = 1000
DAI_AMT = 1000

class Test_UniV3Swaps(unittest.TestCase):

    def getSqrtPriceLimitX96(inputToken):
        if inputToken == 'Token0':
            return 4295128739 + 1
        else:
            return 4295128739 - 1 

    def swapExact1For0(lp, amount, recipient, sqrtPriceLimit):
        sqrtPriceLimitX96 = (
            sqrtPriceLimit
            if sqrtPriceLimit != None
            else getSqrtPriceLimitX96('Token1')
        )
        return swap(lp, 'Token1', [amount, 0], recipient, sqrtPriceLimitX96)

    def swapExact0For1(lp, amount, recipient, sqrtPriceLimit):
        sqrtPriceLimitX96 = (
            sqrtPriceLimit
            if sqrtPriceLimit != None
            else getSqrtPriceLimitX96('Token0')
        )
        
        return swap(lp, 'Token0', [amount, 0], recipient, sqrtPriceLimitX96)        

    def swap(lp, inputToken, amounts, recipient, sqrtPriceLimitX96):
        [amountIn, amountOut] = amounts
        exactInput = amountOut == 0
        amount = amountIn if exactInput else amountOut

        if inputToken == 'Token0':
            if exactInput:
                checkInt128(amount)
                return lp.swap(recipient, True, amount, sqrtPriceLimitX96)
            else:
                checkInt128(-amount)
                return lp.swap(recipient, True, -amount, sqrtPriceLimitX96)
        else:
            if exactInput:
                checkInt128(amount)
                return lp.swap(recipient, False, amount, sqrtPriceLimitX96)
            else:
                checkInt128(-amount)
                return lp.swap(recipient, False, -amount, sqrtPriceLimitX96)                       

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
        (amt0, amt1)  = lp.mint(USER_ACCT0, lwr_tick, upr_tick, 3161) 
        return (amt0, amt1, lp)   

    def setup_lp_mint_zero_tick(self, lp):
        lp.initialize(encodePriceSqrt(1, 1))
        tickSpacing = lp.tickSpacing
        [min, max] = [getMinTick(tickSpacing), getMaxTick(tickSpacing)]
        lp.mint(USER_ACCT0, min, max, initializeLiquidityAmount)             

    def test_fees_duringSwap(self):
        tick_spacing = TICK_SPACINGS[FeeAmount.MEDIUM]
        lwr_tick = getMinTick(TICK_SPACINGS[FeeAmount.MEDIUM])
        upr_tick = getMaxTick(TICK_SPACINGS[FeeAmount.MEDIUM])          
        (_, _, lp) = self.setup_lp_mint() 
        lp.setFeeProtocol(6, 6)

        lp.mint(
            USER_ACCT0, lwr_tick + tick_spacing, upr_tick - tick_spacing, expandTo18Decimals(1)
        )

        swapExact0For1(lp, expandTo18Decimals(1) // 10, USER_ACCT0, None)
        swapExact1For0(lp, expandTo18Decimals(1) // 100, USER_ACCT0, None) 
        #lp.swapExact0For1(USER_ACCT0, expandTo18Decimals(1) // 10,  None)
        #lp.swapExact1For0(USER_ACCT0, expandTo18Decimals(1) // 100, None) 

        assert lp.protocolFees.token0 == 50000000000000
        assert lp.protocolFees.token1 == 5000000000000    

    def test_protectedPositions_beforefeesAreOn(self):
        tick_spacing = TICK_SPACINGS[FeeAmount.MEDIUM]
        lwr_tick = getMinTick(TICK_SPACINGS[FeeAmount.MEDIUM])
        upr_tick = getMaxTick(TICK_SPACINGS[FeeAmount.MEDIUM])          
        (_, _, lp) = self.setup_lp_mint() 

        lp.mint(
            USER_ACCT0, lwr_tick + tick_spacing, upr_tick - tick_spacing, expandTo18Decimals(1)
        )

        swapExact0For1(lp, expandTo18Decimals(1) // 10, USER_ACCT0, None)
        swapExact1For0(lp, expandTo18Decimals(1) // 100, USER_ACCT0, None) 
        #lp.swapExact0For1(USER_ACCT0, expandTo18Decimals(1) // 10, None)
        #lp.swapExact1For0(USER_ACCT0, expandTo18Decimals(1) // 100,  None)      

        assert lp.protocolFees.token0 == 0
        assert lp.protocolFees.token1 == 0

    def test_notAllowPoke_uninitialized_position(self):
        tick_spacing = TICK_SPACINGS[FeeAmount.MEDIUM]
        lwr_tick = getMinTick(TICK_SPACINGS[FeeAmount.MEDIUM])
        upr_tick = getMaxTick(TICK_SPACINGS[FeeAmount.MEDIUM])          
        (_, _, lp) = self.setup_lp_mint() 
        lp.mint(
            USER_ACCT1, lwr_tick + tick_spacing, upr_tick - tick_spacing, expandTo18Decimals(1)
        )
        swapExact0For1(lp, expandTo18Decimals(1) // 10, USER_ACCT0, None)
        swapExact1For0(lp, expandTo18Decimals(1) // 100, USER_ACCT0, None)
        #lp.swapExact0For1(USER_ACCT0, expandTo18Decimals(1) // 10, None)
        #lp.swapExact1For0(USER_ACCT0, expandTo18Decimals(1) // 100, None)       
        lp.mint(USER_ACCT0, lwr_tick + tick_spacing, upr_tick - tick_spacing, 1)

        position = lp.positions[
            getPositionKey(USER_ACCT0, lwr_tick + tick_spacing, upr_tick - tick_spacing)
        ] 

        assert position.liquidity == 1
        assert position.feeGrowthInside0LastX128 == 102084710076281216349243831104605583
        assert position.feeGrowthInside1LastX128 == 10208471007628121634924383110460558
        assert position.tokensOwed0 == 0, "tokens owed 0 before"
        assert position.tokensOwed1 == 0, "tokens owed 1 before"    

        lp.burn(USER_ACCT0, lwr_tick + tick_spacing, upr_tick - tick_spacing, 1)
        position = lp.positions[
            getPositionKey(USER_ACCT0, lwr_tick + tick_spacing, upr_tick - tick_spacing)
        ]
        assert position.liquidity == 0
        assert position.feeGrowthInside0LastX128 == 102084710076281216349243831104605583
        assert position.feeGrowthInside1LastX128 == 10208471007628121634924383110460558
        assert position.tokensOwed0 == 3, "tokens owed 0 before"
        assert position.tokensOwed1 == 0, "tokens owed 1 before"                   
          

                       
         
if __name__ == '__main__':
    unittest.main()    