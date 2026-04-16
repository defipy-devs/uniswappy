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
from python.prod.process.swap import WithdrawSwap

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


class TestWithdrawSwap(unittest.TestCase):

    def setUp(self):
        self.lp, self.eth, self.dai = setup_v2_lp()

    def test_withdraw_decreases_liquidity(self):
        supply_before = self.lp.total_supply
        WithdrawSwap().apply(self.lp, self.eth, USER, 1)
        self.assertLess(self.lp.total_supply, supply_before)

    def test_withdraw_returns_token(self):
        result = WithdrawSwap().apply(self.lp, self.eth, USER, 1)
        self.assertGreater(result, 0)

    def test_withdraw_eth_reserve_change(self):
        reserve_before = self.lp.get_reserve(self.eth)
        WithdrawSwap().apply(self.lp, self.eth, USER, 1)
        self.assertLess(self.lp.get_reserve(self.eth), reserve_before)

    def test_withdraw_roundtrip(self):
        deposit_amt = 10
        SwapDeposit().apply(self.lp, self.eth, USER, deposit_amt)
        eth_reserve_after_deposit = self.lp.get_reserve(self.eth)
        recovered = WithdrawSwap().apply(self.lp, self.eth, USER, deposit_amt)
        # Within fee tolerance (~0.3%)
        self.assertAlmostEqual(recovered, deposit_amt, delta=deposit_amt * 0.01)


if __name__ == '__main__':
    unittest.main()
