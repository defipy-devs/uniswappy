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

# Modified version of original MIT licenced Shared file from chainflip-io
# - https://github.com/chainflip-io/chainflip-uniswapV3-python

from .Shared import *

## @notice Calculates ceil(a×b÷denominator) with full precision. Throws if result overflows a uint256 or denominator == 0
## @param a The multiplicand
## @param b The multiplier
## @param denominator The divisor
## @return result The 256-bit result
def mulDivRoundingUp(a, b, c):
    return divRoundingUp(a * b, c)


## @notice Calculates ceil(a÷denominator) with full precision rounding up. Throws if result overflows a uint256 or denominator == 0
## @param a The multiplicand
## @param b The divisor
## @return result The 256-bit result
def divRoundingUp(a, b):
    result = a // b
    if a % b > 0:
        result += 1
    checkUInt256(result)
    return result


## @notice Calculates floor(a×b÷denominator) with full precision. Throws if result overflows a uint256 or denominator == 0
## @param a The multiplicand
## @param b The multiplier
## @param denominator The divisor
## @return result The 256-bit result
def mulDiv(a, b, c):
    result = (a * b) // c
    checkUInt256(result)
    return result
