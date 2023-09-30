# SeedProxyArbitrage.py
# Author: Ian Moore ( imoore@syscoin.org )
# Date: Sept 2023

import numpy as np
import pandas as pd
from python.prod.cpt.quote import LPQuote
from python.prod.defi.process.swap import Swap
from python.prod.math.model import TokenDeltaModel

class SeedProxyArbitrage():
    
    THRES = 0.2
    FRAC = 0.2
    
    def __init__(self, lp, mstate, tDel = None):   
        self.lp = lp
        self.mstate = mstate
        self.tDel = TokenDeltaModel(50) if tDel == None else tDel
        self.net_y = 0
        self.net_x = 0
        self.y_tot = 0
        self.x_tot = 0        
           
    def apply(self, lp_seed_proxy, user_nm, amt_in = None): 
        x_tkn = self.lp.factory.exchange_to_tokens[self.lp.name][self.lp.token0]
        y_itkn = self.lp.factory.exchange_to_tokens[self.lp.name][self.lp.token1]

        amt_x_sell = 0; amt_y_buy = 0 
        amt_y_sell = 0; amt_x_buy = 0 

        p_x = LPQuote().get_price(self.lp, x_tkn)
        held_y_iamt = self.mstate.get_current_state('dHeld') 

        if(1/p_x > lp_seed_proxy):
            while(1/p_x > lp_seed_proxy):   
                iamt = LPQuote().get_amount(self.lp, x_tkn, self.FRAC*amt_in) 
                if(iamt+amt_y_sell > self.THRES*held_y_iamt): 
                    break
                else:  
                    amt_y_sell += iamt
                    amt_x_buy += Swap().apply(self.lp, y_itkn, user_nm, iamt)
                    p_x = LPQuote().get_price(self.lp, x_tkn)  
        else:    
            while(1/p_x < lp_seed_proxy):
                amt = self.FRAC*amt_in
                amt_x_sell += amt
                amt_y_buy += Swap().apply(self.lp, x_tkn, user_nm, amt)
                p_x = LPQuote().get_price(self.lp, x_tkn)    
            
        net_idai1 = amt_y_buy - amt_y_sell
        self.mstate.update_current_state(net_idai1)            

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
        y_itkn = tokens[self.lp.token1]
        net_amt = 0
        
        if(token.token_name == x_tkn.token_name):
            net_amt = self.net_x
        elif(token.token_name == y_itkn.token_name):
            net_amt = self.net_y
            
        return net_amt    