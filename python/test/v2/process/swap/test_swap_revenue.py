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
from python.prod.process.deposit import SwapDeposit
from python.prod.process.swap import WithdrawSwap

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


class TestSwapRevenue(unittest.TestCase):

    def setUp(self):
        self.lp, self.eth, self.dai = setup_v2_lp()

    def test_swap_revenue_accumulates(self):
        """After 100 deposit/withdraw cycles, ETH reserve increases (fee revenue)
        while DAI quote and LP amount remain constant."""
        pre_dai_amt = LPQuote(False).get_amount_from_lp(self.lp, self.dai, 1)
        pre_lp_amt = self.lp.get_liquidity_from_provider(USER)
        pre_eth_reserve = self.lp.get_reserve(self.eth)

        N_RUNS = 100
        for _ in range(N_RUNS):
            requested_liquidity_in = 500
            eth_settlement_amt = LPQuote(True).get_amount_from_lp(
                self.lp, self.eth, requested_liquidity_in
            )
            SwapDeposit().apply(self.lp, self.eth, USER, eth_settlement_amt)
            get_deposit = LPQuote(False).get_amount_from_lp(
                self.lp, self.eth, self.lp.get_last_liquidity_deposit()
            )
            WithdrawSwap().apply(self.lp, self.eth, USER, get_deposit)

        post_dai_amt = LPQuote(False).get_amount_from_lp(self.lp, self.dai, 1)
        post_lp_amt = self.lp.get_liquidity_from_provider(USER)
        post_eth_reserve = self.lp.get_reserve(self.eth)

        # ETH reserve increases from fee revenue
        self.assertGreater(round(post_eth_reserve, 8), round(pre_eth_reserve, 8))
        # DAI quote per LP stays the same
        self.assertAlmostEqual(pre_dai_amt, post_dai_amt, places=8)
        # LP amount stays the same
        self.assertAlmostEqual(pre_lp_amt, post_lp_amt, places=8)


if __name__ == '__main__':
    unittest.main()
