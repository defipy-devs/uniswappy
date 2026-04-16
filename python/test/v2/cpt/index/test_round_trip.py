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
from python.prod.cpt.index import RebaseIndexToken, SettlementLPToken

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


class TestRoundTrip(unittest.TestCase):
    """Crown jewels -- mathematical identity tests for RebaseIndexToken <-> SettlementLPToken."""

    def setUp(self):
        self.lp, self.eth, self.dai = setup_v2_lp()

    def test_lp_to_token_to_lp_eth(self):
        # Use human-scale LP amount; convert machine outputs to human between steps
        lp_amount = self.lp.convert_to_human(self.lp.total_supply) * 0.1
        token_machine = RebaseIndexToken().apply(self.lp, self.eth, lp_amount)
        token_human = self.lp.convert_to_human(token_machine)
        lp_machine2 = SettlementLPToken().apply(self.lp, self.eth, token_human)
        lp_human2 = self.lp.convert_to_human(lp_machine2)
        self.assertAlmostEqual(lp_human2 / lp_amount, 1.0, delta=0.001)

    def test_token_to_lp_to_token_eth(self):
        token_amount = 100
        lp_machine = SettlementLPToken().apply(self.lp, self.eth, token_amount)
        lp_human = self.lp.convert_to_human(lp_machine)
        token_machine2 = RebaseIndexToken().apply(self.lp, self.eth, lp_human)
        token_human2 = self.lp.convert_to_human(token_machine2)
        self.assertAlmostEqual(token_human2 / token_amount, 1.0, delta=0.001)

    def test_lp_to_token_to_lp_dai(self):
        lp_amount = self.lp.convert_to_human(self.lp.total_supply) * 0.1
        token_machine = RebaseIndexToken().apply(self.lp, self.dai, lp_amount)
        token_human = self.lp.convert_to_human(token_machine)
        lp_machine2 = SettlementLPToken().apply(self.lp, self.dai, token_human)
        lp_human2 = self.lp.convert_to_human(lp_machine2)
        self.assertAlmostEqual(lp_human2 / lp_amount, 1.0, delta=0.001)

    def test_token_to_lp_to_token_dai(self):
        token_amount = 10000
        lp_machine = SettlementLPToken().apply(self.lp, self.dai, token_amount)
        lp_human = self.lp.convert_to_human(lp_machine)
        token_machine2 = RebaseIndexToken().apply(self.lp, self.dai, lp_human)
        token_human2 = self.lp.convert_to_human(token_machine2)
        self.assertAlmostEqual(token_human2 / token_amount, 1.0, delta=0.001)


if __name__ == '__main__':
    unittest.main()
