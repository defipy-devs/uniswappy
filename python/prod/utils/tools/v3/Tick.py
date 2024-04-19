from . import TickMath, LiquidityMath, SafeMath
import math
from .Shared import *


### @notice Derives max liquidity per tick from given tick spacing
### @dev Executed within the pool constructor
### @param tickSpacing The amount of required tick separation, realized in multiples of `tickSpacing`
###     e.g., a tickSpacing of 3 requires ticks to be initialized every 3rd tick i.e., ..., -6, -3, 0, 3, 6, ...
### @return The max liquidity per tick
def tickSpacingToMaxLiquidityPerTick(tickSpacing):
    checkInt24(tickSpacing)
    minTick = math.ceil(TickMath.MIN_TICK / tickSpacing) * tickSpacing
    maxTick = math.floor(TickMath.MAX_TICK / tickSpacing) * tickSpacing
    assert abs(maxTick) >= abs(minTick)  # Health check
    numTicks = ((maxTick - minTick) // tickSpacing) + 1
    assert numTicks <= 2**24 - 1  # Health check
    return TickMath.MAX_UINT128 // numTicks


### @notice Retrieves fee growth data
### @param self The mapping containing all tick information for initialized ticks
### @param tickLower The lower tick boundary of the position
### @param tickUpper The upper tick boundary of the position
### @param tickCurrent The current tick
### @param feeGrowthGlobal0X128 The all-time global fee growth, per unit of liquidity, in token0
### @param feeGrowthGlobal1X128 The all-time global fee growth, per unit of liquidity, in token1
### @return feeGrowthInside0X128 The all-time fee growth in token0, per unit of liquidity, inside the position's tick boundaries
### @return feeGrowthInside1X128 The all-time fee growth in token1, per unit of liquidity, inside the position's tick boundaries
def getFeeGrowthInside(
    self, tickLower, tickUpper, tickCurrent, feeGrowthGlobal0X128, feeGrowthGlobal1X128
):
    checkInputTypes(
        dict=self,
        int24=(tickLower, tickUpper, tickCurrent),
        uint256=(feeGrowthGlobal0X128, feeGrowthGlobal1X128),
    )

    # Assumption that the key (tick) exists
    lower = self[tickLower]
    upper = self[tickUpper]

    ## calculate fee growth below
    if tickCurrent >= tickLower:
        feeGrowthBelow0X128 = lower.feeGrowthOutside0X128
        feeGrowthBelow1X128 = lower.feeGrowthOutside1X128
    else:
        feeGrowthBelow0X128 = feeGrowthGlobal0X128 - lower.feeGrowthOutside0X128
        feeGrowthBelow1X128 = feeGrowthGlobal1X128 - lower.feeGrowthOutside1X128

    ## calculate fee growth above
    if tickCurrent < tickUpper:
        feeGrowthAbove0X128 = upper.feeGrowthOutside0X128
        feeGrowthAbove1X128 = upper.feeGrowthOutside1X128
    else:
        feeGrowthAbove0X128 = feeGrowthGlobal0X128 - upper.feeGrowthOutside0X128
        feeGrowthAbove1X128 = feeGrowthGlobal1X128 - upper.feeGrowthOutside1X128

    # Mimic overflow from solidity
    feeGrowthInside0X128 = toUint256(
        feeGrowthGlobal0X128 - feeGrowthBelow0X128 - feeGrowthAbove0X128
    )
    feeGrowthInside1X128 = toUint256(
        feeGrowthGlobal1X128 - feeGrowthBelow1X128 - feeGrowthAbove1X128
    )
    return (feeGrowthInside0X128, feeGrowthInside1X128)


### @notice Updates a tick and returns true if the tick was flipped from initialized to uninitialized, or vice versa
### @param self The mapping containing all tick information for initialized ticks
### @param tick The tick that will be updated
### @param tickCurrent The current tick
### @param liquidityDelta A new amount of liquidity to be added (subtracted) when tick is crossed from left to right (right to left)
### @param feeGrowthGlobal0X128 The all-time global fee growth, per unit of liquidity, in token0
### @param feeGrowthGlobal1X128 The all-time global fee growth, per unit of liquidity, in token1
### @param secondsPerLiquidityCumulativeX128 The all-time seconds per max(1, liquidity) of the pool
### @param time The current block timestamp cast to a uint32
### @param upper true for updating a position's upper tick, or false for updating a position's lower tick
### @param maxLiquidity The maximum liquidity allocation for a single tick
### @return flipped Whether the tick was flipped from initialized to uninitialized, or vice versa
def update(
    self,
    tick,
    tickCurrent,
    liquidityDelta,
    feeGrowthGlobal0X128,
    feeGrowthGlobal1X128,
    upper,
    maxLiquidity,
):
    checkInputTypes(
        dict=self,
        int24=(tick, tickCurrent),
        int128=liquidityDelta,
        uint256=(feeGrowthGlobal0X128, feeGrowthGlobal1X128),
        bool=upper,
        uint128=maxLiquidity,
    )
    # Tick might not exist - create it. Make sure tick is not created unless it is then initialized with liquidityDelta > 0
    if not self.__contains__(tick):
        assert liquidityDelta > 0, "Avoid creating empty tick"
        insertUninitializedTickstoMapping(self, [tick])

    info = self[tick]

    liquidityGrossBefore = info.liquidityGross
    liquidityGrossAfter = LiquidityMath.addDelta(liquidityGrossBefore, liquidityDelta)

    assert liquidityGrossAfter <= maxLiquidity, "LO"

    flipped = (liquidityGrossAfter == 0) != (liquidityGrossBefore == 0)

    if liquidityGrossBefore == 0:
        ## by convention, we assume that all growth before a tick was initialized happened _below_ the tick
        if tick <= tickCurrent:
            info.feeGrowthOutside0X128 = feeGrowthGlobal0X128
            info.feeGrowthOutside1X128 = feeGrowthGlobal1X128

    info.liquidityGross = liquidityGrossAfter

    ## when the lower (upper) tick is crossed left to right (right to left), liquidity must be added (removed)
    if upper:
        info.liquidityNet = SafeMath.subInts(info.liquidityNet, liquidityDelta)
        checkInt128(info.liquidityNet)
    else:
        info.liquidityNet = SafeMath.addInts(info.liquidityNet, liquidityDelta)
        checkInt128(info.liquidityNet)

    # No longer require flip to signal if it has been initialized but it is needed for when it is cleared
    return flipped


### @notice Clears tick data
### @param self The mapping containing all initialized tick information for initialized ticks
### @param tick The tick that will be cleared
def clear(self, tick):
    checkInputTypes(dict=self, int24=tick)
    # Assumption that the key (tick) exists (it should)
    del self[tick]


### @notice Transitions to next tick as needed by price movement
### @param self The mapping containing all tick information for initialized ticks
### @param tick The destination tick of the transition
### @param feeGrowthGlobal0X128 The all-time global fee growth, per unit of liquidity, in token0
### @param feeGrowthGlobal1X128 The all-time global fee growth, per unit of liquidity, in token1
### @param secondsPerLiquidityCumulativeX128 The current seconds per liquidity
### @param time The current block.timestamp
### @return liquidityNet The amount of liquidity added (subtracted) when tick is crossed from left to right (right to left)
def cross(
    tickBitmap,
    tick,
    feeGrowthGlobal0X128,
    feeGrowthGlobal1X128,
):
    checkInputTypes(
        dict=tickBitmap,
        int24=tick,
        uint256=(feeGrowthGlobal0X128, feeGrowthGlobal1X128),
    )
    ## TickBitMap is passed by reference so all changes will be applied to the original dict
    ## TickBitMap = dict(uint256 tick => TickInfo)
    info = tickBitmap[tick]
    info.feeGrowthOutside0X128 = feeGrowthGlobal0X128 - info.feeGrowthOutside0X128
    info.feeGrowthOutside1X128 = feeGrowthGlobal1X128 - info.feeGrowthOutside1X128
    liquidityNet = info.liquidityNet
    return liquidityNet
