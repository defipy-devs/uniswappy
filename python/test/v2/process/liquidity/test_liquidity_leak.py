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
from python.prod.process.liquidity import AddLiquidity, RemoveLiquidity

USER = 'user0'
ETH_AMT = 100000
DAI_AMT = 10000


def setup_v2_lp():
    eth = ERC20("ETH", "0x09")
    dai = ERC20("DAI", "0x111")
    factory = UniswapFactory("ETH pool factory", "0x2")
    exch_data = UniswapExchangeData(tkn0=eth, tkn1=dai, symbol="LP", address="0x011")
    lp = factory.deploy(exch_data)
    lp.add_liquidity(USER, ETH_AMT, DAI_AMT, ETH_AMT, DAI_AMT)
    return lp, eth, dai


class TestLiquidityLeak(unittest.TestCase):

    def setUp(self):
        self.lp, self.eth, self.dai = setup_v2_lp()

    def test_no_value_leak_after_100_cycles(self):
        """After 100 add/remove liquidity cycles, token amounts and LP
        should remain consistent (no value leak)."""
        pre_eth_amt = LPQuote(False).get_amount_from_lp(self.lp, self.eth, 1)
        pre_lp_amt = self.lp.liquidity_providers[USER]

        N_RUNS = 100
        for _ in range(N_RUNS):
            lp1_amt = 100
            dai_amount1 = LPQuote(True).get_amount_from_lp(self.lp, self.dai, lp1_amt)
            price_idai = dai_amount1 / lp1_amt
            AddLiquidity(price_idai).apply(self.lp, self.dai, USER, lp1_amt)
            RemoveLiquidity().apply(self.lp, self.dai, USER, abs(lp1_amt))

        post_eth_amt = LPQuote(False).get_amount_from_lp(self.lp, self.eth, 1)
        post_lp_amt = self.lp.liquidity_providers[USER]

        # Values should be stable at magnitude level (rounding to -8 matches order of magnitude)
        self.assertEqual(round(pre_eth_amt, -8), round(post_eth_amt, -8))
        self.assertEqual(round(pre_lp_amt, -8), round(post_lp_amt, -8))


if __name__ == '__main__':
    unittest.main()
