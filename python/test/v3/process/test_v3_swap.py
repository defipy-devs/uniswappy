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

import sys, os, unittest, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)).split('/python/')[0])

from python.test.v3.utilities import (
    encodePriceSqrt, getMinTick, getMaxTick, FeeAmount, TICK_SPACINGS,
    expandTo18Decimals
)
from python.prod.cpt.factory import UniswapFactory
from python.prod.erc import ERC20
from python.prod.utils.data import UniswapExchangeData
from python.prod.cpt.quote import LPQuote
from python.prod.cpt.index import RebaseIndexToken, SettlementLPToken

USER = 'user0'


def setup_v3_lp():
    fee = FeeAmount.MEDIUM
    tick_spacing = TICK_SPACINGS[FeeAmount.MEDIUM]
    usdc = ERC20("USDC", "0x09")
    dai = ERC20("DAI", "0x111")
    factory = UniswapFactory("TEST pool factory", "0x2")
    exch_data = UniswapExchangeData(
        tkn0=usdc, tkn1=dai, symbol="LP", address="0x011",
        version=UniswapExchangeData.VERSION_V3,
        precision=UniswapExchangeData.TYPE_GWEI,
        tick_spacing=tick_spacing, fee=fee
    )
    lp = factory.deploy(exch_data)
    lp.initialize(encodePriceSqrt(1, 1))
    lwr = getMinTick(tick_spacing)
    upr = getMaxTick(tick_spacing)
    lp.mint(USER, lwr, upr, 3161)
    return lp, usdc, dai, lwr, upr


class TestV3Swap(unittest.TestCase):

    def setUp(self):
        self.lp, self.usdc, self.dai, self.lwr, self.upr = setup_v3_lp()

    def test_v3_mint_virtual_reserves_positive(self):
        r0 = self.lp.get_virtual_reserve(self.usdc)
        r1 = self.lp.get_virtual_reserve(self.dai)
        self.assertGreater(r0, 0)
        self.assertGreater(r1, 0)

    def test_v3_swap_token0_in(self):
        amt_in = expandTo18Decimals(1) // 100
        result = self.lp.swapExact0For1(USER, amt_in, None)
        # V3 swap returns (recipient, amount0, amount1, sqrtPriceX96, liquidity, tick)
        amount1 = result[2]
        self.assertLess(amount1, 0)  # output is negative (token1 leaves pool)

    def test_v3_swap_token1_in(self):
        amt_in = expandTo18Decimals(1) // 100
        result = self.lp.swapExact1For0(USER, amt_in, None)
        # V3 swap returns (recipient, amount0, amount1, sqrtPriceX96, liquidity, tick)
        amount0 = result[1]
        self.assertLess(amount0, 0)  # output is negative (token0 leaves pool)

    def test_v3_lp_quote_get_amount(self):
        amt = LPQuote().get_amount(self.lp, self.usdc, 100, self.lwr, self.upr)
        self.assertGreater(amt, 0)

    def test_v3_settlement_positive(self):
        result = SettlementLPToken().apply(self.lp, self.usdc, 100, self.lwr, self.upr)
        self.assertGreater(result, 0)

    def test_v3_rebase_positive(self):
        lp_amt = self.lp.get_liquidity() * 0.1
        result = RebaseIndexToken().apply(self.lp, self.usdc, lp_amt, self.lwr, self.upr)
        self.assertGreater(result, 0)


if __name__ == '__main__':
    unittest.main()
