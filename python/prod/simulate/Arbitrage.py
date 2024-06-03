# Copyright [2023] [Ian Moore]
# Distributed under the MIT License (license terms are at http://opensource.org/licenses/MIT).
# Email: defipy.devs@gmail.com

import numpy as np
import pandas as pd
from ..cpt.quote import LPQuote
from ..process.swap import Swap
from ..math.model import TokenDeltaModel
from ..utils.data import UniswapExchangeData
from ..utils.tools.v3 import UniV3Helper
from ..utils.tools.v3 import UniV3Utils

class Arbitrage():
    
    THRES = 0.2
    FRAC = 0.1
    
    def __init__(self, lp, mstate, tDel = None):   
        self.lp = lp
        self.mstate = mstate
        self.tDel = TokenDeltaModel(50) if tDel == None else tDel
        self.threshold = self.THRES
        self.net_y = 0
        self.net_x = 0
        self.y_tot = 0
        self.x_tot = 0 
        self.lwr_tick = None
        self.upr_tick = None         
           
    def apply(self, price_benchmark, user_nm, amt_in = None):
        tokens = self.lp.factory.token_from_exchange[self.lp.name]
        
        x_tkn = tokens[self.lp.token0]
        y_tkn = tokens[self.lp.token1]
        
        amt_x_sell = 0; amt_y_buy = 0 
        amt_y_sell = 0; amt_x_buy = 0
        
        lwr_tick, upr_tick = self.gen_ticks(x_tkn)
        p_x = LPQuote().get_price(self.lp, x_tkn, lwr_tick, upr_tick)
        num_states = len(self.mstate.states)
        held_y_amt = self.mstate.get_current_state('dHeld') 
        
        # arbitrage LP1
        if(p_x != None and p_x > price_benchmark):
            while(p_x > price_benchmark):
                lwr_tick, upr_tick = self.gen_ticks(x_tkn)
                amt = self.gen_random_amt() if amt_in == None else self.FRAC*amt_in
                amt_x_sell += amt
                amt_y_buy += Swap().apply(self.lp, x_tkn, user_nm, amt)
                p_x = LPQuote().get_price(self.lp, x_tkn, lwr_tick, upr_tick)
                #print('p-bench {:.3f} p_x {:.3f}'.format(price_benchmark, p_x))

        elif(p_x != None and p_x <= price_benchmark and num_states > 3):
            while(p_x <= price_benchmark):  
                lwr_tick, upr_tick = self.gen_ticks(x_tkn)
                amt = self.gen_random_amt() if amt_in == None else self.FRAC*amt_in
                q_amt = LPQuote().get_amount(self.lp, x_tkn, amt, lwr_tick, upr_tick)
                #q_held_x_amt = LPQuote().get_amount(self.lp, x_tkn, held_x_amt, lwr_tick, upr_tick)
                if(q_amt+amt_y_sell > self.threshold*held_y_amt): 
                #if(q_amt+amt_y_sell > self.threshold*held_x_amt):     
                    break
                else:  
                    amt_y_sell += q_amt
                    amt_x_buy += Swap().apply(self.lp, y_tkn, user_nm, q_amt)
                    p_x = LPQuote().get_price(self.lp, x_tkn, lwr_tick, upr_tick)
                #print('p-bench {:.3f} p_x {:.3f}'.format(price_benchmark, p_x))    
        
        self.net_x = amt_x_buy - amt_x_sell
        self.net_y = amt_y_buy - amt_y_sell 
        
        self.y_tot += abs(amt_y_buy) + abs(amt_y_sell) 
        self.x_tot += abs(amt_x_buy) + abs(amt_x_sell)

    def set_portion_threshold(self, thres):            
        self.threshold = thres  

    def set_ticks(self, lwr_tick, upr_tick):
        self.lwr_tick = lwr_tick
        self.upr_tick = upr_tick
    
    def gen_ticks(self, x_tkn):
        if(self.lp.version == UniswapExchangeData.VERSION_V3):    
            fee = UniV3Utils.FeeAmount.MEDIUM
            tick_spacing = UniV3Utils.TICK_SPACINGS[fee]
            lwr_tick = UniV3Utils.getMinTick(tick_spacing)
            upr_tick = UniV3Utils.getMaxTick(tick_spacing)
        else:
            lwr_tick = None
            upr_tick = None 
        return lwr_tick, upr_tick
        
    def gen_random_amt(self):            
        return self.FRAC*self.tDel.delta()        
                   
    def update_state(self, token):
        net_amt = self.net_amount(token)
        self.mstate.update_current_state(net_amt) 
    
    def get_x_tot(self):
        return self.x_tot 
    
    def get_y_tot(self):
        return self.y_tot     
    
    def net_amount(self, token):
        tokens = self.lp.factory.token_from_exchange[self.lp.name]
        x_tkn = tokens[self.lp.token0]
        y_tkn = tokens[self.lp.token1]
        net_amt = 0
        
        if(token.token_name == x_tkn.token_name):
            net_amt = self.net_x
        elif(token.token_name == y_tkn.token_name):
            net_amt = self.net_y
            
        return net_amt    