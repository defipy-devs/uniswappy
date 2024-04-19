from .Shared import *
import math
from . import SafeMath, FullMath


### @title defs based on Q64.96 sqrt price and liquidity
### @notice Contains the math that uses square root of price as a Q64.96 and liquidity to compute deltas

### @notice Gets the next sqrt price given a delta of token0
### @dev Always rounds up, because in the exact output case (increasing price) we need to move the price at least
### far enough to get the desired output amount, and in the exact input case (decreasing price) we need to move the
### price less in order to not send too much output.
### The most precise formula for this is liquidity * sqrtPX96 / (liquidity +- amount * sqrtPX96),
### if this is impossible because of overflow, we calculate liquidity / (liquidity / sqrtPX96 +- amount).
### @param sqrtPX96 The starting price, i.e. before accounting for the token0 delta
### @param liquidity The amount of usable liquidity
### @param amount How much of token0 to add or remove from virtual reserves
### @param add Whether to add or remove the amount of token0
### @return The price after adding or removing amount, depending on add
def getNextSqrtPriceFromAmount0RoundingUp(sqrtPX96, liquidity, amount, add):
    checkInputTypes(uint160=sqrtPX96, uint128=liquidity, uint256=amount, bool=add)
    ## we short circuit amount == 0 because the result is otherwise not guaranteed to equal the input price
    if amount == 0:
        return sqrtPX96
    numerator1 = liquidity << FixedPoint96_RESOLUTION

    if add:
        product = amount * sqrtPX96
        # Modified overflow check compared so to Solidity - product might overflow
        if product < MAX_UINT256:
            ##if product / amount == sqrtPX96:
            denominator = numerator1 + product
            if denominator >= numerator1:
                # Result should be casted into UINT160 without overflowing
                # Adding assert to detect wrong behaviour
                result = FullMath.mulDivRoundingUp(numerator1, sqrtPX96, denominator)
                # result = math.ceil((numerator1 * sqrtPX96) / denominator)
                checkUInt160(result)
                return result
        result = math.ceil(numerator1 / SafeMath.add((numerator1 // sqrtPX96), amount))
        # Adding assert to detect wrong behaviour
        assert result <= MAX_UINT160, "Overflow when casting to UINT160"
        return result

    else:
        ## if the product overflows, we know the denominator underflows
        ## in addition, we must check that the denominator does not underflow
        product = amount * sqrtPX96
        assert product < MAX_UINT256 and numerator1 > product
        denominator = numerator1 - product
        result = FullMath.mulDivRoundingUp(numerator1, sqrtPX96, denominator)
        assert result <= MAX_UINT160, "Overflow when casting to UINT160"
        return result


### @notice Gets the next sqrt price given a delta of token1
### @dev Always rounds down, because in the exact output case (decreasing price) we need to move the price at least
### far enough to get the desired output amount, and in the exact input case (increasing price) we need to move the
### price less in order to not send too much output.
### The formula we compute is within <1 wei of the lossless version: sqrtPX96 +- amount / liquidity
### @param sqrtPX96 The starting price, i.e., before accounting for the token1 delta
### @param liquidity The amount of usable liquidity
### @param amount How much of token1 to add, or remove, from virtual reserves
### @param add Whether to add, or remove, the amount of token1
### @return The price after adding or removing `amount`
def getNextSqrtPriceFromAmount1RoundingDown(sqrtPX96, liquidity, amount, add):
    checkInputTypes(uint160=sqrtPX96, uint128=liquidity, uint256=amount, bool=add)
    ## if we're adding (subtracting), rounding down requires rounding the quotient down (up)
    ## in both cases, avoid a mulDiv for most inputs
    if add:
        quotient = (
            (amount << FixedPoint96_RESOLUTION) // liquidity
            if amount <= MAX_UINT160
            else FullMath.mulDiv(amount, FixedPoint96_Q96, liquidity)
        )

        result = sqrtPX96 + quotient

        checkUInt160(result)
        return result
    else:
        quotient = (
            FullMath.divRoundingUp(amount << FixedPoint96_RESOLUTION, liquidity)
            if amount <= MAX_UINT160
            else FullMath.mulDivRoundingUp(amount, FixedPoint96_Q96, liquidity)
        )

        assert sqrtPX96 > quotient
        ## always fits 160 bits
        result = sqrtPX96 - quotient

        checkUInt160(result)
        return result


### @notice Gets the next sqrt price given an input amount of token0 or token1
### @dev Throws if price or liquidity are 0, or if the next price is out of bounds
### @param sqrtPX96 The starting price, i.e., before accounting for the input amount
### @param liquidity The amount of usable liquidity
### @param amountIn How much of token0, or token1, is being swapped in
### @param zeroForOne Whether the amount in is token0 or token1
### @return sqrtQX96 The price after adding the input amount to token0 or token1
def getNextSqrtPriceFromInput(sqrtPX96, liquidity, amountIn, zeroForOne):
    checkInputTypes(
        uint160=sqrtPX96, uint128=liquidity, uint256=amountIn, bool=zeroForOne
    )
    assert sqrtPX96 > 0
    assert liquidity > 0

    ## round to make sure that we don't pass the target price
    return (
        getNextSqrtPriceFromAmount0RoundingUp(sqrtPX96, liquidity, amountIn, True)
        if zeroForOne
        else getNextSqrtPriceFromAmount1RoundingDown(
            sqrtPX96, liquidity, amountIn, True
        )
    )


### @notice Gets the next sqrt price given an output amount of token0 or token1
### @dev Throws if price or liquidity are 0 or the next price is out of bounds
### @param sqrtPX96 The starting price before accounting for the output amount
### @param liquidity The amount of usable liquidity
### @param amountOut How much of token0, or token1, is being swapped out
### @param zeroForOne Whether the amount out is token0 or token1
### @return sqrtQX96 The price after removing the output amount of token0 or token1
def getNextSqrtPriceFromOutput(sqrtPX96, liquidity, amountOut, zeroForOne):
    checkInputTypes(
        uint160=sqrtPX96, uint128=liquidity, uint256=amountOut, bool=zeroForOne
    )
    assert sqrtPX96 > 0
    assert liquidity > 0

    ## round to make sure that we pass the target price
    return (
        getNextSqrtPriceFromAmount1RoundingDown(sqrtPX96, liquidity, amountOut, False)
        if zeroForOne
        else getNextSqrtPriceFromAmount0RoundingUp(
            sqrtPX96, liquidity, amountOut, False
        )
    )


### @notice Gets the amount0 delta between two prices
### @dev Calculates liquidity / sqrt(lower) - liquidity / sqrt(upper),
### i.e. liquidity * (sqrt(upper) - sqrt(lower)) / (sqrt(upper) * sqrt(lower))
### @param sqrtRatioAX96 A sqrt price
### @param sqrtRatioBX96 Another sqrt price
### @param liquidity The amount of usable liquidity
### @return amount0 Amount of token0 required to cover a position of size liquidity between the two passed prices
def getAmount0Delta(sqrtRatioAX96, sqrtRatioBX96, liquidity, roundUp):
    checkInputTypes(
        uint160=(sqrtRatioAX96, sqrtRatioBX96), uint128=liquidity, bool=roundUp
    )
    if sqrtRatioAX96 > sqrtRatioBX96:
        (sqrtRatioAX96, sqrtRatioBX96) = (sqrtRatioBX96, sqrtRatioAX96)

    numerator1 = liquidity << FixedPoint96_RESOLUTION
    numerator2 = sqrtRatioBX96 - sqrtRatioAX96
    assert numerator2 >= 0

    assert sqrtRatioAX96 > 0
    if roundUp:
        return FullMath.divRoundingUp(
            FullMath.mulDivRoundingUp(numerator1, numerator2, sqrtRatioBX96),
            sqrtRatioAX96,
        )
    else:
        return FullMath.mulDiv(numerator1, numerator2, sqrtRatioBX96) // sqrtRatioAX96


### @notice Gets the amount1 delta between two prices
### @dev Calculates liquidity * (sqrt(upper) - sqrt(lower))
### @param sqrtRatioAX96 A sqrt price
### @param sqrtRatioBX96 Another sqrt price
### @param liquidity The amount of usable liquidity
### @return amount1 Amount of token1 required to cover a position of size liquidity between the two passed prices
def getAmount1Delta(sqrtRatioAX96, sqrtRatioBX96, liquidity, roundUp):
    checkInputTypes(
        uint160=(sqrtRatioAX96, sqrtRatioBX96), uint128=liquidity, bool=roundUp
    )
    if sqrtRatioAX96 > sqrtRatioBX96:
        (sqrtRatioAX96, sqrtRatioBX96) = (sqrtRatioBX96, sqrtRatioAX96)

    if roundUp:
        return FullMath.mulDivRoundingUp(
            liquidity, (sqrtRatioBX96 - sqrtRatioAX96), FixedPoint96_Q96
        )
    else:
        return FullMath.mulDiv(
            liquidity, (sqrtRatioBX96 - sqrtRatioAX96), FixedPoint96_Q96
        )


### @notice Helper that gets signed token0 delta
### @param sqrtRatioAX96 A sqrt price
### @param sqrtRatioBX96 Another sqrt price
### @param liquidity The change in liquidity for which to compute the amount0 delta
### @return amount0 Amount of token0 corresponding to the passed liquidityDelta between the two prices
def getAmount0DeltaHelper(sqrtRatioAX96, sqrtRatioBX96, liquidity):
    checkInputTypes(uint160=(sqrtRatioAX96, sqrtRatioBX96), int128=liquidity)
    if liquidity < 0:
        return -getAmount0Delta(sqrtRatioAX96, sqrtRatioBX96, abs(liquidity), False)
    else:
        return getAmount0Delta(sqrtRatioAX96, sqrtRatioBX96, abs(liquidity), True)


### @notice Helper that gets signed token1 delta
### @param sqrtRatioAX96 A sqrt price
### @param sqrtRatioBX96 Another sqrt price
### @param liquidity The change in liquidity for which to compute the amount1 delta
### @return amount1 Amount of token1 corresponding to the passed liquidityDelta between the two prices
def getAmount1DeltaHelper(sqrtRatioAX96, sqrtRatioBX96, liquidity):
    checkInputTypes(uint160=(sqrtRatioAX96, sqrtRatioBX96), int128=liquidity)
    if liquidity < 0:
        return -getAmount1Delta(sqrtRatioAX96, sqrtRatioBX96, abs(liquidity), False)
    else:
        return getAmount1Delta(sqrtRatioAX96, sqrtRatioBX96, abs(liquidity), True)
