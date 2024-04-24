# Copyright [2024] [Ian Moore]
# Distributed under the MIT License (license terms are at http://opensource.org/licenses/MIT).
# Email: defipy.devs@gmail.com

# Modified version of original MIT licenced TickMath file from chainflip-io
# - https://github.com/chainflip-io/chainflip-uniswapV3-python

from . import TickMath

### @title Math library for liquidity

### @notice Add a signed liquidity delta to liquidity and revert if it overflows or underflows
### @param x The liquidity before change
### @param y The delta by which liquidity should be changed
### @return z The liquidity delta
def addDelta(x, y):
    if y < 0:
        z = x - abs(y)
        # Mimic solidity underflow
        assert z >= 0, "LS"
    else:
        z = x + abs(y)
        # Mimic solidity overflow check
        assert z <= TickMath.MAX_UINT128, "LA"
    return z
