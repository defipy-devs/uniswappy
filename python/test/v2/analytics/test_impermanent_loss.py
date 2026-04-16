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

import sys, os, unittest
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)).split('/python/')[0])

from python.prod.erc import ERC20
from python.prod.cpt.factory import UniswapFactory
from python.prod.utils.data import UniswapExchangeData
from python.prod.process.deposit import SwapDeposit
from python.prod.process.swap import Swap
from python.prod.analytics.risk import UniswapImpLoss

# NOTE: UniswapV2 K invariant check is currently disabled in UniswapExchange.swap()
# These tests verify reserve changes and output amounts, not K conservation.

USER = 'user0'
ETH_AMT = 1000
DAI_AMT = 100000


def setup_v2_lp(eth_amt=ETH_AMT, dai_amt=DAI_AMT):
    eth = ERC20("ETH", "0x09")
    dai = ERC20("DAI", "0x111")
    factory = UniswapFactory("ETH pool factory", "0x2")
    exch_data = UniswapExchangeData(tkn0=eth, tkn1=dai, symbol="LP", address="0x011")
    lp = factory.deploy(exch_data)
    lp.add_liquidity(USER, eth_amt, dai_amt, eth_amt, dai_amt)
    return lp, eth, dai


class TestImpermanentLoss(unittest.TestCase):

    def setUp(self):
        self.lp, self.eth, self.dai = setup_v2_lp()
        # UniswapImpLoss expects human-scale LP amount
        self.lp_init_amt = self.lp.convert_to_human(self.lp.liquidity_providers[USER])
        self.il_tracker = UniswapImpLoss(self.lp, self.lp_init_amt)

    def test_il_zero_at_entry(self):
        il = self.il_tracker.apply(fees=False)
        self.assertAlmostEqual(il, 0.0, places=6)

    def test_il_negative_after_price_move(self):
        Swap().apply(self.lp, self.dai, USER, 10000)
        il = self.il_tracker.apply(fees=False)
        self.assertLess(il, 0)

    def test_il_worse_with_larger_price_move(self):
        lp1, eth1, dai1 = setup_v2_lp()
        lp_init1 = lp1.convert_to_human(lp1.liquidity_providers[USER])
        il1_tracker = UniswapImpLoss(lp1, lp_init1)
        Swap().apply(lp1, dai1, USER, 10000)
        il_small = il1_tracker.apply(fees=False)

        lp2, eth2, dai2 = setup_v2_lp()
        lp_init2 = lp2.convert_to_human(lp2.liquidity_providers[USER])
        il2_tracker = UniswapImpLoss(lp2, lp_init2)
        Swap().apply(lp2, dai2, USER, 30000)
        il_large = il2_tracker.apply(fees=False)

        self.assertLess(il_large, il_small)

    def test_hold_value_positive_at_entry(self):
        tokens = self.lp.factory.token_from_exchange[self.lp.name]
        x_tkn = tokens[self.lp.token0]
        hold = self.il_tracker.hold_value(x_tkn)
        self.assertGreater(hold, 0)

    def test_current_position_value_positive(self):
        tokens = self.lp.factory.token_from_exchange[self.lp.name]
        x_tkn = tokens[self.lp.token0]
        val = self.il_tracker.current_position_value(x_tkn)
        self.assertGreater(val, 0)

    def test_fees_mode_returns_float(self):
        result = self.il_tracker.apply(fees=True)
        self.assertIsInstance(result, float)


if __name__ == '__main__':
    unittest.main()
