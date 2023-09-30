from python.prod.defi.process import Process
from python.prod.defi.process.liquidity import AddLiquidity
from python.dev.math.model import TokenDeltaModel
from python.dev.math.model import EventSelectionModel

class SwapDeposit(Process):

    def __init__(self, ev = None, tDel = None):
        self.ev = EventSelectionModel() if self.ev  == None else ev
        self.tDel = TokenDeltaModel(50) if self.tDel == None else tDel
            
    def apply(self, lp, token_in, user_nm, amount_in):    
        amount_in = tDel.delta() if amount_in == None else amount_in
        amount_out = swap(lp, token_in, user_nm, 0.5*amount_in)
        trading_token = self.get_trading_token(lp, token_in)
        
        addLiq = AddLiquidity()
        addLiq.apply(lp, trading_token, user_nm, amount_out) 
        
        return 0.5*amount_in, amount_out 
    
    def get_trading_token(self, lp, token):
        tokens = lp.factory.exchange_to_tokens[lp.name]
        trading_token = tokens[lp.token1] if token.token_name == lp.token0 else tokens[lp.token0]
        return trading_token       
        
