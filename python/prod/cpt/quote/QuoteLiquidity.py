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

from ..exchg.ChildLP import ChildLP
from ...utils.data import UniswapExchangeData

class QuoteLiquidity():

    def __init__(self):
        pass

    def apply(self, lp_in, tkn):
        tkn_x = lp_in.factory.token_from_exchange[lp_in.name][lp_in.token0]
        tkn_y = lp_in.factory.token_from_exchange[lp_in.name][lp_in.token1]
        
        return self.get_tkn_amt(lp_in, tkn, tkn_x) + self.get_tkn_amt(lp_in, tkn, tkn_y)
    
    def get_base_lp(self, lp_in):
    
        tkn_x = lp_in.factory.token_from_exchange[lp_in.name][lp_in.token0]
        tkn_y = lp_in.factory.token_from_exchange[lp_in.name][lp_in.token1]
        
        if(tkn_x.type == 'index'):
            base_lp = tkn_y.parent_lp
        elif(tkn_y.type == 'index'):
            base_lp = tkn_y.parent_lp
        else: 
            base_lp = lp_in
            
        return base_lp  
    
    def get_tkn_amt(self, lp_in, tkn_in, tkn):

        if(lp_in.version == UniswapExchangeData.VERSION_V2):    

            if tkn.type == 'index':
                base_lp = tkn.parent_lp
                base_tkn = tkn.parent_tkn
                base_tkn_amt = base_lp.get_reserve(base_tkn)
            else:
                base_tkn = tkn
                base_tkn_amt = lp_in.get_reserve(tkn)

        elif(lp_in.version == UniswapExchangeData.VERSION_V3):
            lp_child = ChildLP(lp_in)
            base_tkn = lp_child.get_base_tkn(tkn)
            base_tkn_amt = lp_child.get_reserve(tkn)
            
        base_lp = self.get_base_lp(lp_in)
        
        tot_amt = 0
        if(tkn_in.token_name == base_tkn.token_name):
            tot_amt += base_tkn_amt
        else:
            tot_amt += base_tkn_amt*base_lp.get_price(base_tkn)
    
        return tot_amt