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
from python.prod.cpt.index import RebaseIndexToken
from python.prod.cpt.quote import LPQuote
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


class TestDrainLP(unittest.TestCase):

    def setUp(self):
        self.lp, self.eth, self.dai = setup_v2_lp()

    def test_drain_lp_to_zero(self):
        """Repeatedly withdraw from LP until position is fully drained."""
        amt_lp = 250
        N = int(self.lp.get_liquidity_from_provider(USER) / amt_lp)

        aggr_withdrawn = 0
        for k in range(N - 1):
            itkn_amt = LPQuote(False).get_amount_from_lp(self.lp, self.dai, amt_lp)
            aggr_withdrawn += WithdrawSwap().apply(self.lp, self.dai, USER, itkn_amt)

        tol = 1e-5
        itkn_amt = LPQuote(False).get_amount_from_lp(self.lp, self.dai, amt_lp - tol)
        aggr_withdrawn += WithdrawSwap().apply(self.lp, self.dai, USER, itkn_amt)

        # LP position nearly zero
        self.assertAlmostEqual(self.lp.get_liquidity_from_provider(USER), 0.0, places=4)
        # All DAI withdrawn
        self.assertAlmostEqual(aggr_withdrawn, DAI_AMT, places=4)
        # ETH reserve unchanged (all withdrawals were in DAI)
        self.assertAlmostEqual(self.lp.get_reserve(self.eth), ETH_AMT, places=4)
        # DAI reserve fully drained
        self.assertAlmostEqual(self.lp.get_reserve(self.dai), 0.0, places=4)


if __name__ == '__main__':
    unittest.main()
