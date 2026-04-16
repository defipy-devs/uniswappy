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
from python.prod.process.join import Join

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


class TestJoin(unittest.TestCase):

    def setUp(self):
        self.lp, self.eth, self.dai = setup_v2_lp()

    def test_join_initial_reserves(self):
        self.assertEqual(self.lp.get_reserve(self.eth), ETH_AMT)
        self.assertEqual(self.lp.get_reserve(self.dai), DAI_AMT)

    def test_join_lp_minted(self):
        self.assertGreater(self.lp.total_supply, 0)

    def test_join_proportional(self):
        initial_eth = self.lp.get_reserve(self.eth)
        initial_dai = self.lp.get_reserve(self.dai)
        self.lp.add_liquidity(USER, ETH_AMT, DAI_AMT, ETH_AMT, DAI_AMT)
        self.assertAlmostEqual(self.lp.get_reserve(self.eth), initial_eth * 2, places=4)
        self.assertAlmostEqual(self.lp.get_reserve(self.dai), initial_dai * 2, places=4)

    def test_join_lp_attribution(self):
        self.assertGreater(self.lp.liquidity_providers[USER], 0)


if __name__ == '__main__':
    unittest.main()
