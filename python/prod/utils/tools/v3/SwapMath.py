from . import SqrtPriceMath, FullMath
from .Shared import *

### @title Computes the result of a swap within ticks
### @notice Contains methods for computing the result of a swap within a single tick price range, i.e., a single tick.

### @notice Computes the result of swapping some amount in, or amount out, given the parameters of the swap
### @dev The fee, plus the amount in, will never exceed the amount remaining if the swap's `amountSpecified` is positive
### @param sqrtRatioCurrentX96 The current sqrt price of the pool
### @param sqrtRatioTargetX96 The price that cannot be exceeded, from which the direction of the swap is inferred
### @param liquidity The usable liquidity
### @param amountRemaining How much input or output amount is remaining to be swapped in#out
### @param feePips The fee taken from the input amount, expressed in hundredths of a bip
### @return sqrtRatioNextX96 The price after swapping the amount in#out, not to exceed the price target
### @return amountIn The amount to be swapped in, of either token0 or token1, based on the direction of the swap
### @return amountOut The amount to be received, of either token0 or token1, based on the direction of the swap
### @return feeAmount The amount of input that will be taken as a fee
def computeSwapStep(
    sqrtRatioCurrentX96, sqrtRatioTargetX96, liquidity, amountRemaining, feePips
):
    checkInputTypes(
        uint160=(sqrtRatioCurrentX96, sqrtRatioTargetX96),
        uint128=liquidity,
        int256=amountRemaining,
        uint24=feePips,
    )

    zeroForOne = sqrtRatioCurrentX96 >= sqrtRatioTargetX96

    # exactIn < 0 means exactOut = True
    exactIn = amountRemaining >= 0

    if exactIn:
        amountRemainingLessFee = FullMath.mulDiv(
            amountRemaining, ONE_IN_PIPS - feePips, ONE_IN_PIPS
        )
        amountIn = (
            SqrtPriceMath.getAmount0Delta(
                sqrtRatioTargetX96, sqrtRatioCurrentX96, liquidity, True
            )
            if zeroForOne
            else SqrtPriceMath.getAmount1Delta(
                sqrtRatioCurrentX96, sqrtRatioTargetX96, liquidity, True
            )
        )

        if amountRemainingLessFee >= amountIn:
            sqrtRatioNextX96 = sqrtRatioTargetX96
        else:
            sqrtRatioNextX96 = SqrtPriceMath.getNextSqrtPriceFromInput(
                sqrtRatioCurrentX96, liquidity, amountRemainingLessFee, zeroForOne
            )
    else:
        amountOut = (
            SqrtPriceMath.getAmount1Delta(
                sqrtRatioTargetX96, sqrtRatioCurrentX96, liquidity, False
            )
            if zeroForOne
            else SqrtPriceMath.getAmount0Delta(
                sqrtRatioCurrentX96, sqrtRatioTargetX96, liquidity, False
            )
        )

        # amountRemaining <= 0
        if abs(amountRemaining) >= amountOut:
            sqrtRatioNextX96 = sqrtRatioTargetX96
        else:
            sqrtRatioNextX96 = SqrtPriceMath.getNextSqrtPriceFromOutput(
                sqrtRatioCurrentX96, liquidity, abs(amountRemaining), zeroForOne
            )

    max = sqrtRatioTargetX96 == sqrtRatioNextX96

    ## get the input#output amounts
    if zeroForOne:
        amountIn = (
            amountIn
            if (max and exactIn)
            else SqrtPriceMath.getAmount0Delta(
                sqrtRatioNextX96, sqrtRatioCurrentX96, liquidity, True
            )
        )
        amountOut = (
            amountOut
            if (max and not exactIn)
            else SqrtPriceMath.getAmount1Delta(
                sqrtRatioNextX96, sqrtRatioCurrentX96, liquidity, False
            )
        )

    else:
        amountIn = (
            amountIn
            if (max and exactIn)
            else SqrtPriceMath.getAmount1Delta(
                sqrtRatioCurrentX96, sqrtRatioNextX96, liquidity, True
            )
        )
        amountOut = (
            amountOut
            if (max and not exactIn)
            else SqrtPriceMath.getAmount0Delta(
                sqrtRatioCurrentX96, sqrtRatioNextX96, liquidity, False
            )
        )

    ## cap the output amount to not exceed the remaining output amount
    if (not exactIn) and (amountOut > abs(amountRemaining)):
        checkUInt256(-amountRemaining)
        amountOut = abs(amountRemaining)

    if exactIn and sqrtRatioNextX96 != sqrtRatioTargetX96:
        ## we didn't reach the target, so take the remainder of the maximum input as fee
        checkUInt256(amountRemaining)
        feeAmount = abs(amountRemaining) - amountIn
    else:
        feeAmount = FullMath.mulDivRoundingUp(amountIn, feePips, ONE_IN_PIPS - feePips)

    return (sqrtRatioNextX96, amountIn, amountOut, feeAmount)
