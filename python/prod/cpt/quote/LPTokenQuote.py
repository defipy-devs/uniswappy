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

from .LPQuote import LPQuote

class LPTokenQuote():
    
    def __init__(self, lwr_tick = None, upr_tick = None, quote_child = True):
        self.quote_child = quote_child 
        self.lwr_tick = lwr_tick
        self.upr_tick = upr_tick         
 
    def get_x(self, lp, amt_tkn_x): 
        tkn_x = lp.factory.token_from_exchange[lp.name][lp.token0] 
        parent_lp = self.get_base_lp(lp, tkn_x)
        parent_lp_x_tkn = parent_lp.factory.token_from_exchange[parent_lp.name][parent_lp.token0]
        parent_x_tkn = tkn_x.parent_tkn if tkn_x.type == 'index' else tkn_x

        if(parent_x_tkn.token_name != parent_lp_x_tkn.token_name):
            amt_tkn_x = LPQuote().get_amount(parent_lp, parent_lp_x_tkn, amt_tkn_x, self.lwr_tick, self.upr_tick)     

        if(tkn_x.type == 'standard'):
            amt_x = LPQuote(False).get_amount(parent_lp, parent_x_tkn, amt_tkn_x, self.lwr_tick, self.upr_tick)
            lp_amt = LPQuote().get_lp_from_amount(lp, parent_x_tkn, amt_x, self.lwr_tick, self.upr_tick)
        else: 
            amt_x = LPQuote(False).get_amount(parent_lp, parent_x_tkn, amt_tkn_x, self.lwr_tick, self.upr_tick) 
            amt_x_lp = LPQuote().get_lp_from_amount(parent_lp, parent_x_tkn, amt_x, self.lwr_tick, self.upr_tick)
            lp_amt = LPQuote().get_lp_from_amount(lp, parent_x_tkn, amt_x_lp, self.lwr_tick, self.upr_tick)

        return lp_amt 
        
    def base_x_asset(self, lp):
        tkn_x = lp.factory.token_from_exchange[lp.name][lp.token0]
        if(tkn_x.type == 'index'):
            tkn = tkn_x.parent_tkn
        else:
            tkn = tkn_x

        return tkn    

    def get_base_lp(self, lp, tkn):
        if(tkn.type == 'index'):
            base_lp = tkn.parent_lp
        else:
            base_lp = lp.factory.parent_lp
        return base_lp if base_lp != None else lp      
 
 

        
            
