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


class TestSwapDeposit(unittest.TestCase):

    def setUp(self):
        self.lp, self.eth, self.dai = setup_v2_lp()

    def test_swap_deposit_increases_liquidity(self):
        supply_before = self.lp.total_supply
        SwapDeposit().apply(self.lp, self.eth, USER, 10)
        self.assertGreater(self.lp.total_supply, supply_before)

    def test_swap_deposit_returns_lp_amount(self):
        result = SwapDeposit().apply(self.lp, self.eth, USER, 10)
        self.assertGreater(result, 0)

    def test_swap_deposit_eth_reserve_change(self):
        reserve_before = self.lp.get_reserve(self.eth)
        SwapDeposit().apply(self.lp, self.eth, USER, 10)
        self.assertGreater(self.lp.get_reserve(self.eth), reserve_before)

    def test_swap_deposit_dai_direction(self):
        reserve_before = self.lp.get_reserve(self.dai)
        SwapDeposit().apply(self.lp, self.dai, USER, 100)
        self.assertGreater(self.lp.get_reserve(self.dai), reserve_before)


if __name__ == '__main__':
    unittest.main()
