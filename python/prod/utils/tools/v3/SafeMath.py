from .Shared import *
from . import TickMath

### @title Overflow and underflow math operations.
### @notice Contains methods for doing math operations that revert on overflow or underflow for minimal gas cost.Mimic solidity overflow and underflow check as in some cases the check is a safeguard.

### @notice Returns x + y, reverts if sum overflows uint256
### @param x The augend
### @param y The addend
### @return z The sum of x and y
def add(x, y):
    checkInputTypes(uint256=(x, y))
    z = x + y
    assert z <= TickMath.MAX_UINT256
    return z


### @notice Returns x - y, reverts if underflows
### @param x The minuend
### @param y The subtrahend
### @return z The difference of x and y
def sub(x, y):
    checkInputTypes(uint256=(x, y))
    z = x - y
    assert z >= 0
    return z


### @notice Returns x * y, reverts if overflows
### @param x The multiplicand
### @param y The multiplier
### @return z The product of x and y
def mul(x, y):
    checkInputTypes(uint256=(x, y))
    z = x * y
    assert z <= TickMath.MAX_UINT256
    return z


### @notice Returns x + y, reverts if overflows or underflows
### @param x The augend
### @param y The addend
### @return z The sum of x and y
def addInts(x, y):
    checkInputTypes(int256=(x, y))
    z = x + y
    assert z >= TickMath.MIN_INT256 and z <= TickMath.MAX_UINT256
    return z


### @notice Returns x - y, reverts if overflows or underflows
### @param x The minuend
### @param y The subtrahend
### @return z The difference of x and y
def subInts(x, y):
    checkInputTypes(int256=(x, y))
    z = x - y
    assert z >= TickMath.MIN_INT256 and z <= TickMath.MAX_UINT256
    return z
