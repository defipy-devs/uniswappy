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
from python.prod.cpt.index import SettlementLPToken

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


class TestSettlementLPToken(unittest.TestCase):

    def setUp(self):
        self.lp, self.eth, self.dai = setup_v2_lp()

    def test_settlement_positive(self):
        result = SettlementLPToken().apply(self.lp, self.eth, 100)
        self.assertGreater(result, 0)

    def test_settlement_scales_with_input(self):
        # Use small amounts relative to pool for approximate linearity
        result1 = SettlementLPToken().apply(self.lp, self.eth, 10)
        result2 = SettlementLPToken().apply(self.lp, self.eth, 20)
        ratio = result2 / result1
        self.assertAlmostEqual(ratio, 2.0, delta=0.02)

    def test_settlement_zero_input(self):
        result = SettlementLPToken().apply(self.lp, self.eth, 0)
        self.assertEqual(result, 0)

    def test_settlement_dai_direction(self):
        result = SettlementLPToken().apply(self.lp, self.dai, 10000)
        self.assertGreater(result, 0)


if __name__ == '__main__':
    unittest.main()
