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

from ...utils.data import UniswapExchangeData
from ...cpt.factory import UniswapFactory
from ...analytics.simulate import SolveDeltas
from ...process.deposit import SwapDeposit
from ...process.swap import WithdrawSwap

USER_NM = 'USER_SIM'

class SimpleLPSimulation:
    
    def __init__(self):
        self.lp = None
        self.tkn_price_arr = []
        self.x_amt_arr = []
        self.y_amt_arr = []
        self.tkn_x_amt = None
        self.tkn_y_amt = None

    def init_amts(self, tkn_x_amt, init_price):
        self.tkn_x_amt = tkn_x_amt
        self.tkn_y_amt = init_price*tkn_x_amt 

    def create_lp(self, tkn_x, tkn_y):
        
        assert self.tkn_x_amt != None or self.tkn_y_amt != None, 'SimpleLPSimulation: TKN AMTS NOT INITIALIZED'
        
        factory = UniswapFactory("TKN pool factory", None)
        
        exchg_data = UniswapExchangeData(tkn0 = tkn_x, tkn1 = tkn_y, symbol='LP', address=None)
        self.lp = factory.deploy(exchg_data)
        self.lp.add_liquidity(USER_NM, self.tkn_x_amt, self.tkn_y_amt, self.tkn_x_amt, self.tkn_y_amt)

    def run(self, p_trial_arr):
        sDel = SolveDeltas(self.lp)
        tkn_x = self.lp.factory.token_from_exchange[self.lp.name][self.lp.token0]
        tkn_y = self.lp.factory.token_from_exchange[self.lp.name][self.lp.token1]
        tkn_price_arr = []
        lp_tot_arr = []
        x_amt_arr = []
        y_amt_arr = []
        for p in p_trial_arr[1:]: 
            
            swap_dx, swap_dy = sDel.calc(p)   
            if(swap_dx >= 0):
                expected_amount_dep = SwapDeposit().apply(self.lp, tkn_x, USER_NM, abs(swap_dx))
                expected_amount_out = WithdrawSwap().apply(self.lp, tkn_y, USER_NM, abs(swap_dy))
            elif(swap_dy >= 0):
                expected_amount_dep = SwapDeposit().apply(self.lp, tkn_y, USER_NM, abs(swap_dy))
                expected_amount_out = WithdrawSwap().apply(self.lp, tkn_x, USER_NM, abs(swap_dx)) 
              
            # ************************* #
            # do advanced lp stuff here
            # ************************* #
                
            self.tkn_price_arr.append(self.lp.get_price(tkn_x))    
            self.x_amt_arr.append(self.lp.get_reserve(tkn_x))  
            self.y_amt_arr.append(self.lp.get_reserve(tkn_y))  
    
    def get_lp(self):
        return self.lp
    
    def get_tkn_price_sim(self):
        return self.tkn_price_arr
    
    def get_x_amt_sim(self):
        return self.x_amt_arr
    
    def get_y_amt_sim(self): 
        return self.y_amt_arr
        