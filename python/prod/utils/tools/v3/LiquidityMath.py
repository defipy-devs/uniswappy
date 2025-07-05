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
