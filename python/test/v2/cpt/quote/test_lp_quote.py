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
from python.prod.cpt.quote import LPQuote

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


class TestLPQuote(unittest.TestCase):

    def setUp(self):
        self.lp, self.eth, self.dai = setup_v2_lp()

    def test_get_price_eth(self):
        price = LPQuote().get_price(self.lp, self.eth)
        self.assertAlmostEqual(price, 100.0, places=2)

    def test_get_price_dai(self):
        price = LPQuote().get_price(self.lp, self.dai)
        self.assertAlmostEqual(price, 0.01, places=4)

    def test_get_reserve_eth(self):
        reserve = LPQuote().get_reserve(self.lp, self.eth)
        self.assertEqual(reserve, ETH_AMT)

    def test_get_reserve_dai(self):
        reserve = LPQuote().get_reserve(self.lp, self.dai)
        self.assertEqual(reserve, DAI_AMT)

    def test_get_amount_eth_to_dai(self):
        amt = LPQuote().get_amount(self.lp, self.eth, 100)
        self.assertAlmostEqual(amt / 10000, 1.0, delta=0.01)

    def test_get_amount_from_lp(self):
        some_lp_amt = self.lp.total_supply * 0.1
        amt = LPQuote(False).get_amount_from_lp(self.lp, self.eth, some_lp_amt)
        self.assertGreater(amt, 0)

    def test_get_lp_from_amount(self):
        lp_amt = LPQuote(False).get_lp_from_amount(self.lp, self.eth, 100)
        self.assertGreater(lp_amt, 0)

    def test_round_trip_lp(self):
        lp_amt = LPQuote(False).get_lp_from_amount(self.lp, self.eth, 100)
        recovered = LPQuote(False).get_amount_from_lp(self.lp, self.eth, lp_amt)
        self.assertAlmostEqual(recovered / 100.0, 1.0, delta=0.001)


if __name__ == '__main__':
    unittest.main()
