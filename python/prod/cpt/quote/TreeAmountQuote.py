# TreeAmountQuote.py
# Author: Ian Moore ( utiliwire@gmail.com )
# Date: Aug 2023

from ..index import RebaseIndexToken
from .LPQuote import LPQuote
import math

class TreeAmountQuote():
    
    def __init__(self, quote_native_token = True, exchg_price = 1):
        self.exchg_price = exchg_price if exchg_price != 1 else exchg_price
        self.quote_native_token = quote_native_token 

    def get_tot_x(self, lp, amt0, amt1):
        tkn_x = lp.factory.exchange_to_tokens[lp.name][lp.token0]
        tkn_y = lp.factory.exchange_to_tokens[lp.name][lp.token1]
        amt_in_x =  self.get_x(lp, tkn_x, amt0) + self.get_x(lp, tkn_y, amt1)
        return self.get_native_x(lp, tkn_x, amt_in_x) if self.quote_native_token else amt_in_x

    def get_tot_y(self, lp, amt0, amt1):
        tkn_x = lp.factory.exchange_to_tokens[lp.name][lp.token0]
        tkn_y = lp.factory.exchange_to_tokens[lp.name][lp.token1]
        amt_in_y = self.get_y(lp, tkn_x, amt0) + self.get_y(lp, tkn_y, amt1)
        return self.get_native_y(lp, tkn_y, amt_in_y) if self.quote_native_token else amt_in_y 

    def get_x(self, lp, tkn, amt):
        amt_in_x = 0 
        if(tkn.type == 'standard'):
            x_tkn = self.base_x_asset_nm(lp) == tkn.token_name
            base_lp = self.get_base_lp(lp, tkn)
            amt_in_x = LPQuote(not x_tkn).get_amount(base_lp, tkn, amt)
        elif(tkn.type == 'index'):
            x_tkn = self.base_x_asset_nm(lp) == tkn.parent_tkn.token_name
            amt_in_x = LPQuote(not x_tkn).get_amount_from_lp(tkn.parent_lp, tkn.parent_tkn, amt)

        return amt_in_x

    def get_y(self, lp, tkn, amt): 
        amt_in_y = 0 
        if(tkn.type == 'standard'):
            y_tkn = self.base_y_asset_nm(lp) == tkn.token_name
            base_lp = self.get_base_lp(lp, tkn)
            amt_in_y = LPQuote(not y_tkn).get_amount(base_lp, tkn, amt)
        elif(tkn.type == 'index'):
            y_tkn = self.base_y_asset_nm(lp) == tkn.parent_tkn.token_name
            amt_in_y = LPQuote(not y_tkn).get_amount_from_lp(tkn.parent_lp, tkn.parent_tkn, amt)
            
        return amt_in_y  
    
    def get_native_x(self, lp, tkn_x, x_amt):
        parent_lp = self.get_base_lp(lp, tkn_x)
        parent_lp_x_tkn = parent_lp.factory.exchange_to_tokens[parent_lp.name][parent_lp.token0]
        parent_x_tkn = tkn_x.parent_tkn if tkn_x.type == 'index' else tkn_x

        if(parent_x_tkn.token_name != parent_lp_x_tkn.token_name):
            x_amt = LPQuote().get_amount(parent_lp, parent_x_tkn, x_amt) 

        return x_amt

    def get_native_y(self, lp, tkn_y, y_amt):
        parent_lp = self.get_base_lp(lp, tkn_y)
        parent_lp_y_tkn = parent_lp.factory.exchange_to_tokens[parent_lp.name][parent_lp.token1]
        parent_y_tkn = tkn_y.parent_tkn if tkn_y.type == 'index' else tkn_y

        if(parent_y_tkn.token_name != parent_lp_y_tkn.token_name):
            y_amt = LPQuote().get_amount(parent_lp, parent_y_tkn, y_amt) 

        return y_amt    
    
    def calc_lp_settlement(self, lp, token_in, itkn_amt):

        if(token_in.token_name == lp.token1):
            x = lp.reserve0
            y = lp.reserve1
        else: 
            x = lp.reserve1
            y = lp.reserve0

        L = lp.total_supply
        if(L == 0): 
            return 0
        else:
            gamma = 997

            a1 = x*y/L
            a2 = L
            a = a1/a2
            b = (1000*itkn_amt*x - itkn_amt*gamma*x + 1000*x*y + x*y*gamma)/(1000*L);
            c = itkn_amt*x;

            dL = (b*a2 - a2*math.sqrt(b*b - 4*a1*c/a2)) / (2*a1);
            return dL    

    def base_x_asset_nm(self, lp):
        tkn_x = lp.factory.exchange_to_tokens[lp.name][lp.token0]
        if(tkn_x.type == 'index'):
            tkn_name = tkn_x.parent_tkn.token_name
        else:
            tkn_name = tkn_x.token_name

        return tkn_name
    
    def base_x_asset(self, lp):
        tkn_x = lp.factory.exchange_to_tokens[lp.name][lp.token0]
        if(tkn_x.type == 'index'):
            tkn = tkn_x.parent_tkn
        else:
            tkn = tkn_x

        return tkn    

    def base_y_asset_nm(self, lp):
        tkn_y = lp.factory.exchange_to_tokens[lp.name][lp.token1]
        if(tkn_y.type == 'index'):
            tkn_name = tkn_y.parent_tkn.token_name
        else:
            tkn_name = tkn_y.token_name

        return tkn_name

    def get_base_lp(self, lp, tkn):
        if(tkn.type == 'index'):
            base_lp = tkn.parent_lp
        else:
            base_lp = lp.factory.parent_lp
        return base_lp if base_lp != None else lp      
