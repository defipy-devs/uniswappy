# LPTokenQuote.py
# Author: Ian Moore ( utiliwire@gmail.com )
# Date: Sept 2023

from .LPQuote import LPQuote

class LPTokenQuote():
    
    def __init__(self, quote_child = True):
        self.quote_child = quote_child  
 
    def get_x(self, lp, amt_tkn_x): 
        tkn_x = lp.factory.exchange_to_tokens[lp.name][lp.token0] 
        parent_lp = self.get_base_lp(lp, tkn_x)
        parent_lp_x_tkn = parent_lp.factory.exchange_to_tokens[parent_lp.name][parent_lp.token0]
        parent_x_tkn = tkn_x.parent_tkn if tkn_x.type == 'index' else tkn_x

        if(parent_x_tkn.token_name != parent_lp_x_tkn.token_name):
            amt_tkn_x = LPQuote().get_amount(parent_lp, parent_lp_x_tkn, amt_tkn_x)     

        if(tkn_x.type == 'standard'):
            amt_x = LPQuote(False).get_amount(parent_lp, parent_x_tkn, amt_tkn_x)
            lp_amt = LPQuote().get_lp_from_amount(lp, parent_x_tkn, amt_x)
        else: 
            amt_x = LPQuote(False).get_amount(parent_lp, parent_x_tkn, amt_tkn_x) 
            amt_x_lp = LPQuote().get_lp_from_amount(parent_lp, parent_x_tkn, amt_x)
            lp_amt = LPQuote().get_lp_from_amount(lp, parent_x_tkn, amt_x_lp)

        return lp_amt 
        
    def base_x_asset(self, lp):
        tkn_x = lp.factory.exchange_to_tokens[lp.name][lp.token0]
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
 
 

        
            
