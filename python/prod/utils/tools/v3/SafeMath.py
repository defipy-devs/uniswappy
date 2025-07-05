# ─────────────────────────────────────────────────────────────────────────────
# Apache 2.0 License (DeFiPy)
# ─────────────────────────────────────────────────────────────────────────────
# Copyright 2023–2025 Ian Moore
# Email: defipy.devs@gmail.com
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License

# ─────────────────────────────────────────────────────────────────────────────
# MIT License Attribution (Third-Party Code)
# ─────────────────────────────────────────────────────────────────────────────
# This file contains code adapted from chainflip-io (https://github.com/chainflip-io/chainflip-uniswapV3-python)
# Licensed under the MIT License.
# Original copyright (c) 2022 chainflip-io contributors.

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
