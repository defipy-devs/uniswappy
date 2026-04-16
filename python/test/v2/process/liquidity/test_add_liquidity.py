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
from python.prod.process.liquidity import AddLiquidity, RemoveLiquidity

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


class TestAddLiquidity(unittest.TestCase):

    def setUp(self):
        self.lp, self.eth, self.dai = setup_v2_lp()

    def test_add_liquidity_single_token(self):
        supply_before = self.lp.total_supply
        AddLiquidity().apply(self.lp, self.eth, USER, 10)
        self.assertGreater(self.lp.total_supply, supply_before)

    def test_add_liquidity_reserve_increases(self):
        eth_before = self.lp.get_reserve(self.eth)
        AddLiquidity().apply(self.lp, self.eth, USER, 10)
        self.assertGreater(self.lp.get_reserve(self.eth), eth_before)

    def test_remove_liquidity_single_token(self):
        dai_before = self.lp.get_reserve(self.dai)
        RemoveLiquidity().apply(self.lp, self.dai, USER, 1000)
        self.assertLess(self.lp.get_reserve(self.dai), dai_before)

    def test_add_then_remove_approx_neutral(self):
        eth_start = self.lp.get_reserve(self.eth)
        dai_start = self.lp.get_reserve(self.dai)
        AddLiquidity().apply(self.lp, self.eth, USER, 10)
        RemoveLiquidity().apply(self.lp, self.eth, USER, 10)
        eth_end = self.lp.get_reserve(self.eth)
        dai_end = self.lp.get_reserve(self.dai)
        self.assertAlmostEqual(eth_end / eth_start, 1.0, delta=0.01)
        self.assertAlmostEqual(dai_end / dai_start, 1.0, delta=0.01)


if __name__ == '__main__':
    unittest.main()
