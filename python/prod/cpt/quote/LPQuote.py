# LPQuote.py
# Author: Ian Moore ( utiliwire@gmail.com )
# Date: Jul 2023

from ..index import RebaseIndexToken
from ..index import SettlementLPToken
import math

class LPQuote():
    
    def __init__(self, quote_opposing = True):
        self.quote_opposing = quote_opposing
        

    def get_opposing_token(self, lp, tkn):
        opposing_tkn_nm = lp.token1 if(tkn.token_name == lp.token0) else lp.token0
        return lp.factory.exchange_to_tokens[lp.name][opposing_tkn_nm]

    def get_reserve(self, lp, token):  
        
        if(token.token_name == lp.token0):        
            reserve_out = lp.reserve0 
        elif(token.token_name == lp.token1):
            reserve_out = lp.reserve1     

        if token.type == 'index':
            self.quote_opposing = False
            parent_lp = token.parent_lp
            parent_token = token.parent_tkn
            reserve_out = self.get_amount_from_lp(parent_lp, parent_token, reserve_out)     

        return reserve_out

    def get_price(self, lp, tkn, price_tkn = True):  
           
        opposing_tkn = self.get_opposing_token(lp, tkn)

        if(tkn.token_name == lp.token0):
            reserve0 = self.get_reserve(lp, tkn)
            reserve1 = self.get_reserve(lp, opposing_tkn)
            if(reserve0 == 0):
                return 0 
            else:
                return reserve1/reserve0 if price_tkn else lp.get_price(tkn)
        elif(tkn.token_name == lp.token1):    
            reserve1 = self.get_reserve(lp, tkn)
            reserve0 = self.get_reserve(lp, opposing_tkn)        
            if(reserve1 == 0):
                return 0
            else:
                return reserve0/reserve1 if price_tkn else lp.get_price(tkn)
        else:
            print('ERROR: wrong input token')              
        
    def get_liquidity(self, lp, tkn, amount_in):   
        
        if(tkn.token_name == lp.token0):
            amt_out = (amount_in * lp.total_supply)/lp.reserve0 
        else:
            amt_out = (amount_in * lp.total_supply)/lp.reserve1 

        return amt_out         
        
        
    def get_amount(self, lp, tkn, amount_in):
                
        if(tkn.token_name == lp.token0):
            amt_out = (amount_in * lp.reserve1) / lp.reserve0
        else:
            amt_out = (amount_in * lp.reserve0) / lp.reserve1
    
        return amt_out if self.quote_opposing else amount_in 
    
    def get_amount_from_lp(self, lp, tkn, amount_lp_in):
        if(amount_lp_in > 0):
            itkn_amt = RebaseIndexToken().apply(lp, tkn, amount_lp_in)
            amt_out = self.get_amount(lp, tkn, itkn_amt) if self.quote_opposing else itkn_amt
        else:
            amt_out = 0
        return amt_out   
    
    
    def get_lp_from_amount(self, lp, tkn, amount_in):
        if(amount_in > 0):
            lp_amt = SettlementLPToken().apply(lp, tkn, amount_in)
        else:
            lp_amt = 0
        return lp_amt   
         