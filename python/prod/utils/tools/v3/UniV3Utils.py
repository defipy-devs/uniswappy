# Copyright [2024] [Ian Moore]
# Distributed under the MIT License (license terms are at http://opensource.org/licenses/MIT).
# Email: defipy.devs@gmail.com

# Modified version of MIT licenced original utils file from chainflip-io 
# - https://github.com/chainflip-io/chainflip-uniswapV3-python

import sys, traceback, math, copy
from decimal import *
import pytest

from .Shared import *

TEST_TOKEN0 = "Token0"
TEST_TOKEN1 = "Token1"

@dataclass
class UniV3Utils():

    TEST_TOKENS = [TEST_TOKEN0, TEST_TOKEN1]
    
    @dataclass
    class FeeAmount:
        LOW: int = 500
        MEDIUM: int = 3000
        HIGH: int = 10000
    
    def getMinTick(tickSpacing):
        return math.ceil(MIN_TICK / tickSpacing) * tickSpacing
    
    
    def getMaxTick(tickSpacing):
        return math.floor(MAX_TICK / tickSpacing) * tickSpacing
    
    
    def getMaxLiquidityPerTick(tickSpacing):
        denominator = (getMaxTick(tickSpacing) - getMinTick(tickSpacing)) // tickSpacing + 1
        return (2**128 - 1) // denominator
    
    TICK_SPACINGS = {FeeAmount.LOW: 10, FeeAmount.MEDIUM: 60, FeeAmount.HIGH: 200}   
    
    def encodePriceSqrt(reserve1, reserve0):
        # Workaround to get the same numbers as JS
        # This ratio doesn't output the same number as in JS using big number. This causes some
        # disparities in the expected results. Full ratios (1,1), (2,1) ...
        # Forcing values obtained by bigNumber.js when ratio is not exact.
        if reserve1 == 121 and reserve0 == 100:
            return 87150978765690771352898345369
        elif reserve1 == 101 and reserve0 == 100:
            return 79623317895830914510487008059
        elif reserve1 == 1 and reserve0 == 10:
            return 25054144837504793118650146401
        elif reserve1 == 1 and reserve0 == 2**127:
            return 6085630636
        elif reserve1 == 2**127 and reserve0 == 1:
            return 1033437718471923701407239276819587054334136928048
        else:
            return int(math.sqrt(reserve1 / reserve0) * 2**96)
    
    
    def expandTo18Decimals(number):
        # Converting to int because python cannot shl on a float
        return int(number * 10**18)
    
    
    # @dev This function will handle reverts (aka assert failures) in the tests. However, in python there is no revert
    # as in the blockchain. So we will create a hard copy of the current pool and call the same method there.
    def tryExceptHandler(fcn, assertMessage, *args):
    
        reverted = False
    
        try:
            # reference to object
            pool = fcn.__self__
            fcnName = fcn.__name__
    
            # hard copy to prevent state changes in the pool
            poolCopy = copy.deepcopy(pool)
    
            try:
                fcn = getattr(poolCopy, fcnName)
            except AttributeError:
                assert "Function not found in pool: " + fcnName
        except:
            # e.g. case when swapExact1ForZero is expected to revert
            print(
                "Non-pool class function passed - expect pool to be copied as part of the call"
            )
    
        try:
            fcn(*args)
        except AssertionError as msg:
            reverted = True
            _, _, tb = sys.exc_info()
            traceback.print_tb(tb)  # Fixed format
            tb_info = traceback.extract_tb(tb)
            filename, line, func, text = tb_info[-1]
    
            print("An error occurred on line {} in statement {}".format(line, text))
            if str(msg) != assertMessage:
                print(
                    "Reverted succesfully but not for the expected reason. \n Expected: '"
                    + str(assertMessage)
                    + "' but got: '"
                    + str(msg)
                    + "'"
                )
                assert False
            print("Succesful revert")
    
        if not reverted:
            print("Failed to revert: " + assertMessage)
            assert False
    
    
    def getPositionKey(address, lowerTick, upperTick):
        return hash((address, lowerTick, upperTick))
    
    
    def getLimitPositionKey(address, tick, isToken0):
        return hash((address, tick, isToken0))
    
    
    ### POOL SWAPS ###
    def swapExact0For1(pool, amount, recipient, sqrtPriceLimit):
        sqrtPriceLimitX96 = (
            sqrtPriceLimit
            if sqrtPriceLimit != None
            else getSqrtPriceLimitX96(TEST_TOKEN0)
        )
        return swap(pool, TEST_TOKEN0, [amount, 0], recipient, sqrtPriceLimitX96)
    
    
    def swap0ForExact1(pool, amount, recipient, sqrtPriceLimit):
        sqrtPriceLimitX96 = (
            sqrtPriceLimit
            if sqrtPriceLimit != None
            else getSqrtPriceLimitX96(TEST_TOKEN0)
        )
        return swap(pool, TEST_TOKEN0, [0, amount], recipient, sqrtPriceLimitX96)
    
    
    def swapExact1For0(pool, amount, recipient, sqrtPriceLimit):
        sqrtPriceLimitX96 = (
            sqrtPriceLimit
            if sqrtPriceLimit != None
            else getSqrtPriceLimitX96(TEST_TOKEN1)
        )
        return swap(pool, TEST_TOKEN1, [amount, 0], recipient, sqrtPriceLimitX96)
    
    
    def swap1ForExact0(pool, amount, recipient, sqrtPriceLimit):
        sqrtPriceLimitX96 = (
            sqrtPriceLimit
            if sqrtPriceLimit != None
            else getSqrtPriceLimitX96(TEST_TOKEN1)
        )
        return swap(pool, TEST_TOKEN1, [0, amount], recipient, sqrtPriceLimitX96)
    
    
    def swapToLowerPrice(pool, recipient, sqrtPriceLimit):
        return pool.swap(recipient, True, MAX_INT256, sqrtPriceLimit)
    
    
    def swapToHigherPrice(pool, recipient, sqrtPriceLimit):
        return pool.swap(recipient, False, MAX_INT256, sqrtPriceLimit)
    
    
    def swap(self, pool, inputToken, amounts, recipient, sqrtPriceLimitX96):
        [amountIn, amountOut] = amounts
        exactInput = amountOut == 0
        amount = amountIn if exactInput else amountOut
    
        if inputToken == TEST_TOKEN0:
            if exactInput:
                checkInt128(amount)
                return pool.swap(recipient, True, amount, sqrtPriceLimitX96)
            else:
                checkInt128(-amount)
                return pool.swap(recipient, True, -amount, sqrtPriceLimitX96)
        else:
            if exactInput:
                checkInt128(amount)
                return pool.swap(recipient, False, amount, sqrtPriceLimitX96)
            else:
                checkInt128(-amount)
                return pool.swap(recipient, False, -amount, sqrtPriceLimitX96)
    
    
    def getSqrtPriceLimitX96(inputToken):
        if inputToken == TEST_TOKEN0:
            return MIN_SQRT_RATIO + 1
        else:
            return MAX_SQRT_RATIO - 1
    
    
    ################
    
    
    def formatPrice(price):
        fraction = (price / (2**96)) ** 2
        return formatAsInSnapshot(fraction)
    
    
    def formatTokenAmount(amount):
        fraction = amount / (10**18)
        return formatAsInSnapshot(fraction)
    
    
    def formatAsInSnapshot(number):
        # To match snapshot formatting
        precision = int(f"{number:e}".split("e")[-1])
        # For token we want 4 extra decimals of precision
        if precision >= 0:
            precision = 4
        else:
            precision = -precision + 4
    
        return format(number, "." + str(precision) + "f")
    
    
    def formatPriceWithPrecision(price, precision):
        fraction = (price / (2**96)) ** 2
        return round(fraction, precision)
