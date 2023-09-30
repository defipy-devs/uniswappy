from python.prod.cpt.index import RebaseIndexToken

class LPQuote():
    
    def __init__(self, quote_opposing = True):
        self.quote_opposing = quote_opposing
        
    def amount_tkn(self, lp, tkn, amount_in):

        if(tkn.token_name == lp.token0):
            amt_out = (amount_in * lp.reserve1) / lp.reserve0
        else:
            amt_out = (amount_in * lp.reserve0) / lp.reserve1

        return amt_out 
    
    def amount_tkn_from_lp(self, lp, tkn, amount_lp_in):
        itkn_amt = RebaseIndexToken().apply(lp, tkn, amount_lp_in)
        amt_out = self.amount_tkn(lp, tkn, itkn_amt) if self.quote_opposing else itkn_amt
        return amt_out    