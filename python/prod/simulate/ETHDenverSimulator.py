from ..utils.data import UniswapExchangeData
from ..utils.data import Chain0x
from ..erc import ERC20
from ..utils.client import API0x
from ..math.model import TokenDeltaModel
from ..math.model import EventSelectionModel
from ..cpt.factory import UniswapFactory
from ..simulate import CorrectReserves
from ..process.deposit import SwapDeposit
from ..process.swap import WithdrawSwap
from ..process.swap import Swap

import time
import datetime
import random

BUY_TOKEN = '0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2'
SELL_TOKEN = '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48'
SELL_AMOUNT = '10000000'
USER_NM = 'user'
TRADE_TIME_WINDOW = 0.5
TKN_TRADE_BIAS = 0.5

class ETHDenverSimulator:
    
    STATE_ARB = 'arb'
    STATE_SWAP = 'swap'
    
    def __init__(self, time_window = None, trade_bias = None):
        self.lp = None 
        self.api = API0x(chain = Chain0x.ETHEREUM)
        self.time_window = TRADE_TIME_WINDOW if time_window == None else time_window
        self.trade_bias = TKN_TRADE_BIAS if trade_bias == None else trade_bias
        self.td_model = TokenDeltaModel(30)
        self.arb = None
        self.x_tkn = None
        self.y_tkn = None
        self.time_init = None
        self.state = 'instantiate'
        
        self.time_arb = None
        self.x_amt_arb = None
        self.y_amt_arb = None
        self.price_arb = None
        
        self.time_swap = None
        self.x_amt_swap = None
        self.y_amt_swap = None
        self.price_swap = None     
        self.amt_swap = None
        
    def get_lp(self):
        return self.lp
    
    def get_state(self):
        return self.state
    
    def get_swap_amt(self):
        return self.amt_swap     
    
    def get_x_tkn(self):
        return self.x_tkn    
    
    def get_y_tkn(self):
        return self.y_tkn        
    
    def get_time_stamp(self, state):
        if(state == self.STATE_SWAP):
            return self.time_swap 
        else:
            return self.time_arb    
    
    def get_lp_price(self, state):
        if(state == self.STATE_SWAP):
            return self.price_swap 
        else:
            return self.price_arb
    
    def get_x_reserve(self, state):
        if(state == self.STATE_SWAP):
            return self.x_amt_swap 
        else:
            return self.x_amt_arb       
        
    def get_y_reserve(self, state):
        if(state == self.STATE_SWAP):
            return self.y_amt_swap 
        else:
            return self.y_amt_arb             
        
    def get_0x_data(self):    
        return self.api.apply(SELL_TOKEN, BUY_TOKEN, SELL_AMOUNT)
    
    def get_market_price(self): 
        chain_call = self.get_0x_data()
        return 1/float(chain_call['price'])
    
    def init_lp(self, amt_tkn0):
        self.state = 'init_lp'
        p = self.get_market_price()
        x_tkn_amt = amt_tkn0
        y_tkn_amt = x_tkn_amt*p

        self.x_tkn = ERC20("WETH", None)
        self.y_tkn = ERC20("USDC", None)
        exchg_data = UniswapExchangeData(tkn0 = self.x_tkn, tkn1 = self.y_tkn, symbol="LP", address=None)

        factory = UniswapFactory("ETH pool factory", None)
        self.lp = factory.deploy(exchg_data)
        self.lp.add_liquidity(USER_NM, x_tkn_amt, y_tkn_amt, x_tkn_amt, y_tkn_amt) 
        
        self.arb = CorrectReserves(self.lp, x0 = p)
        self.time_init = datetime.datetime.now()
     
    def trial(self):
        p = self.get_market_price()
        remaining_sleep = TRADE_TIME_WINDOW
        
        # STATE: RANDOM SWAP
        pause = random.uniform(0, remaining_sleep)
        time.sleep(pause)        
        self._random_swap(p)
        remaining_sleep -= pause
        
        # STATE: MARKET ARBITRAGE
        pause = random.uniform(0, remaining_sleep)
        time.sleep(pause) 
        self._market_arbitrage(p)
        remaining_sleep -= pause
        
        time.sleep(remaining_sleep) 

        return p
        
    def process(self):
        while(True): 
            self.trial()
        
    def _random_swap(self, p):   
        self.state = self.STATE_SWAP
        rnd_amt = self.td_model.delta()
        self.amt_swap = rnd_amt
        select_tkn = EventSelectionModel().bi_select(self.trade_bias)
        
        if(select_tkn == 0):
            out = Swap().apply(self.lp, self.x_tkn, USER_NM, rnd_amt)  
        else:
            out = Swap().apply(self.lp, self.y_tkn, USER_NM, 0.5*p*rnd_amt)  
            
        self.time_swap = datetime.datetime.now() 
        self.x_amt_swap = self.lp.get_reserve(self.arb.get_x_tkn())
        self.y_amt_swap = self.lp.get_reserve(self.arb.get_y_tkn())
        self.price_swap = self.lp.get_price(self.arb.get_x_tkn())        
            
    def _market_arbitrage(self, p):  
        self.state = self.STATE_ARB
        self.arb.apply(p)
        
        self.time_arb = datetime.datetime.now()
        self.x_amt_arb = self.lp.get_reserve(self.arb.get_x_tkn())
        self.y_amt_arb = self.lp.get_reserve(self.arb.get_y_tkn())
        self.price_arb = self.lp.get_price(self.arb.get_x_tkn())            
                 