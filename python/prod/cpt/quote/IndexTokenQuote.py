# IndexTokenQuote.py
# Author: Ian Moore ( utiliwire@gmail.com )
# Date: Sept 2023

from .LPQuote import LPQuote

class IndexTokenQuote():
    
    def __init__(self, quote_native_tokens = True):
        self.quote_native_tokens = quote_native_tokens    

    def get_x(self, lp, amt_lp): 
        tkn_x = lp.factory.exchange_to_tokens[lp.name][lp.token0]  
        if(tkn_x.type == 'standard'):
            x_amt = LPQuote(False).get_amount_from_lp(lp, tkn_x, amt_lp)
        else: 
            parent_x_tkn = tkn_x.parent_tkn
            parent_lp = self.get_base_lp(lp, tkn_x)
            itkn_lp = LPQuote(False).get_amount_from_lp(lp, tkn_x, amt_lp)
            x_amt = LPQuote(False).get_amount_from_lp(parent_lp, parent_x_tkn, itkn_lp)        
        return self.get_native_x(lp, tkn_x, x_amt) if self.quote_native_tokens else x_amt           
        
    def get_y(self, lp, amt_lp): 
        tkn_y = lp.factory.exchange_to_tokens[lp.name][lp.token1]  
        if(tkn_y.type == 'standard'):
            y_amt = LPQuote(False).get_amount_from_lp(lp, tkn_y, amt_lp)
        else:           
            parent_y_tkn = tkn_y.parent_tkn
            parent_lp = self.get_base_lp(lp, tkn_y)
            itkn_lp = LPQuote(False).get_amount_from_lp(lp, tkn_y, amt_lp)
            y_amt = LPQuote(False).get_amount_from_lp(parent_lp, parent_y_tkn, itkn_lp)        

        return self.get_native_y(lp, tkn_y, y_amt) if self.quote_native_tokens else y_amt     
   
    def base_x_asset(self, lp):
        tkn_x = lp.factory.exchange_to_tokens[lp.name][lp.token0]
        if(tkn_x.type == 'index'):
            tkn = tkn_x.parent_tkn
        else:
            tkn = tkn_x

        return tkn    

    def base_y_asset(self, lp):
        tkn_y = lp.factory.exchange_to_tokens[lp.name][lp.token1]
        if(tkn_y.type == 'index'):
            tkn = tkn_y.parent_tkn
        else:
            tkn = tkn_y

        return tkn   

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
    
    
    def get_base_lp(self, lp, tkn):
        if(tkn.type == 'index'):
            base_lp = tkn.parent_lp
        else:
            base_lp = lp.factory.parent_lp
        return lp if base_lp == None else base_lp          
        
        