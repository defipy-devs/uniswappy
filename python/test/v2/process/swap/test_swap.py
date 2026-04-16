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
from python.prod.process.swap import Swap

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


class TestSwap(unittest.TestCase):

    def setUp(self):
        self.lp, self.eth, self.dai = setup_v2_lp()

    def test_swap_dai_for_eth_reserve_hardcoded(self):
        # Swap 1000 DAI in → ETH reserve drops to 990.12842
        Swap().apply(self.lp, self.dai, USER, 1000)
        self.assertAlmostEqual(round(self.lp.get_reserve(self.eth), 6), 990.12842, places=5)

    def test_swap_eth_for_dai_reserve_hardcoded(self):
        # Swap 10 ETH in → DAI reserve drops to 99012.841966
        Swap().apply(self.lp, self.eth, USER, 10)
        self.assertAlmostEqual(round(self.lp.get_reserve(self.dai), 6), 99012.841966, places=4)

    def test_swap_output_positive(self):
        result = Swap().apply(self.lp, self.dai, USER, 1000)
        self.assertGreater(result, 0)

    def test_swap_reserves_move_opposite(self):
        eth_before = self.lp.get_reserve(self.eth)
        dai_before = self.lp.get_reserve(self.dai)
        Swap().apply(self.lp, self.dai, USER, 1000)
        self.assertLess(self.lp.get_reserve(self.eth), eth_before)
        self.assertGreater(self.lp.get_reserve(self.dai), dai_before)

    def test_swap_larger_input_worse_rate(self):
        lp1, eth1, dai1 = setup_v2_lp()
        lp2, eth2, dai2 = setup_v2_lp()
        out_small = Swap().apply(lp1, dai1, USER, 100)
        out_large = Swap().apply(lp2, dai2, USER, 10000)
        # Rate = output / input; larger trade gets worse rate
        self.assertGreater(out_small / 100, out_large / 10000)


if __name__ == '__main__':
    unittest.main()
