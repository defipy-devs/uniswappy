# Arbitrage.py
# Author: Ian Moore ( utiliwire@gmail.com )
# Date: Jun 2023

import numpy as np
import pandas as pd
from ..cpt.quote import LPQuote
from ..process.swap import Swap
from ..math.model import TokenDeltaModel

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
           
    def apply(self, price_benchmark, user_nm, amt_in = None):
        tokens = self.lp.factory.exchange_to_tokens[self.lp.name]
        
        x_tkn = tokens[self.lp.token0]
        y_tkn = tokens[self.lp.token1]
        
        amt_x_sell = 0; amt_y_buy = 0 
        amt_y_sell = 0; amt_x_buy = 0
        
        #p_x = self.lp.get_price(x_tkn)
        p_x = LPQuote().get_price(self.lp, x_tkn)
        num_states = len(self.mstate.states)
        held_x_amt = self.mstate.get_current_state('dHeld') 
        
        # arbitrage LP1
        if(p_x != None and p_x > price_benchmark):
            while(p_x > price_benchmark):
                amt = self.gen_random_amt() if amt_in == None else self.FRAC*amt_in
                amt_x_sell += amt
                amt_y_buy += Swap().apply(self.lp, x_tkn, user_nm, amt)
                p_x = LPQuote().get_price(self.lp, x_tkn)
                #print('p-bench {:.3f} p_x {:.3f}'.format(price_benchmark, p_x))

        elif(p_x != None and p_x <= price_benchmark and num_states > 3):
            while(p_x <= price_benchmark):  
                amt = self.gen_random_amt() if amt_in == None else self.FRAC*amt_in
                amt = LPQuote().get_amount(self.lp, x_tkn, amt)
                if(amt+amt_y_sell > self.threshold*held_x_amt): 
                    break
                else:  
                    amt_y_sell += amt
                    amt_x_buy += Swap().apply(self.lp, y_tkn, user_nm, amt)
                    p_x = LPQuote().get_price(self.lp, x_tkn)
                #print('p-bench {:.3f} p_x {:.3f}'.format(price_benchmark, p_x))    
         
        self.net_x = amt_x_buy - amt_x_sell
        self.net_y = amt_y_buy - amt_y_sell 
        
        self.y_tot += abs(amt_y_buy) + abs(amt_y_sell) 
        self.x_tot += abs(amt_x_buy) + abs(amt_x_sell)

    def set_portion_threshold(self, thres):            
        self.threshold = thres      
        
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
        tokens = self.lp.factory.exchange_to_tokens[self.lp.name]
        x_tkn = tokens[self.lp.token0]
        y_tkn = tokens[self.lp.token1]
        net_amt = 0
        
        if(token.token_name == x_tkn.token_name):
            net_amt = self.net_x
        elif(token.token_name == y_tkn.token_name):
            net_amt = self.net_y
            
        return net_amt    