# Copyright [2024] [Ian Moore, Bart Hofkin]
# Distributed under the MIT License (license terms are at http://opensource.org/licenses/MIT).
# Email: defipy.devs@gmail.com

from ..utils.data import UniswapExchangeData
from ..utils.data import Chain0x
from ..erc import ERC20
from ..utils.client import API0x
from ..math.model import TokenDeltaModel
from ..math.model import EventSelectionModel
from ..cpt.factory import UniswapFactory
from ..cpt.quote import LPTokenQuote
from ..cpt.quote import IndexTokenQuote
from ..cpt.quote import TreeAmountQuote
from ..simulate import CorrectReserves
from ..process.deposit import SwapDeposit
from ..process.swap import WithdrawSwap
from ..process.swap import Swap

import time
import datetime
import random

USER_NM = 'user'

class QuantTerminal:
    
    """ 
        Quant Terminal Simulator class applies the 0x API to produce a mock Uniswap pool to 
        allow end-users to stress test the limitations of a Uniswap pool setup using live price 
        feeds from 0x API

        Parameters
        -----------------
        buy_token : str
            buy token contract address (ie, pulled from Chain0x data class)
        sell_token : str
            buy token contract address (ie, pulled from Chain0x data class)  
        time_window : float
            trial time window (ie, pulled from Chain0x data class, or passed in directly)  
        trade_bias : float
            Random trade bias where probability of bias to buy verses sell token postions is set to 50/50 by default 
            (ie, pulled from Chain0x data class, or passed in directly from slider in GUI) 
        td_model : TokenDeltaModel
            Token delta model is the non-deterministic model for incoming swap amounts; set 
            to Gamma distribution with paramaters set to scale = 1 and shape = 1 (by default)
        api : API0x
            Ox API class; unless otherwise specified, set to ETHEREUM chain and WETH/USDC trading pair by default
        
    """        
    
    STATE_ARB = 'arb'
    STATE_SWAP = 'swap'
    STATE_INIT = 'init_lp'
    STATE_INSTANTIATE = 'instantiate'
    
    def __init__(self, 
                 buy_token = None,
                 sell_token = None,                 
                 time_window = None, 
                 trade_bias = None,
                 td_model = None,
                 api = None
                ):
        
        self.buy_token = Chain0x().get_buy_token() if buy_token == None else buy_token
        self.sell_token = Chain0x().get_sell_token() if sell_token == None else sell_token
        self.time_window = Chain0x.time_window if time_window == None else time_window
        self.trade_bias = Chain0x.trade_bias if trade_bias == None else trade_bias        
        self.td_model = TokenDeltaModel(30) if td_model == None else td_model
        self.api = API0x(chain = Chain0x.ETHEREUM) if api == None else api 
        
        self.lp = None 
        self.arb = None
        self.x_tkn = None
        self.y_tkn = None
        self.time_init = None
        self.init_lp_invest = None
        self.state = self.STATE_INSTANTIATE
        self.remaining_sleep = self.time_window
        self.api_0x_data = None
        self.prev_api_0x_data = None
        
        self.x_redeem = None
        self.y_redeem = None
        
        self.x_trial_amt = 0
        self.y_trial_amt = 0        
        
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
        
        """ get_lp

            Get Uniswap exchange pool object   
                
            Returns
            -----------------
            lp : UniswapExchange
                Uniswap exchange pool object                 
        """          
        
        return self.lp
    
    def get_state(self):
        
        """ get_state

            Get pool's current state (ie, init_lp, arb, swap)
                
            Returns
            -----------------
            state : str
                Pool's current state (ie, init_lp, arb, swap)                 
        """         
        
        return self.state
    
    def get_swap_amt(self):
        
        """ get_swap_amt

            Get pool's current state (ie, init_lp, arb, swap)
                
            Returns
            -----------------
            amt_swap : float
                Pool's current state (ie, init_lp, arb, swap)                 
        """         
        
        return self.amt_swap  
    
    def get_x_redeem(self):
        
        """ get_x_redeem

            Get x token redemption amount from mock pool investment
                
            Returns
            -----------------
            x_redeem : float
                x token redemption amount from mock pool investment                  
        """           
        
        return self.x_redeem
    
    def get_y_redeem(self):
        
        """ get_y_redeem

            Get y token redemption amount from mock pool investment
                
            Returns
            -----------------
            y_redeem : float
                y token redemption amount from mock pool investment                  
        """          
        
        return self.y_redeem    
    
    def get_x_tkn(self):
        
        """ get_x_tkn

            Get x token from Uniswap mock pool
                
            Returns
            -----------------
            x_tkn : ERC20
                x token from mock pool                   
        """          
        
        return self.x_tkn    
    
    def get_y_tkn(self):
        
        """ get_y_tkn

            Get y token from Uniswap mock pool
                
            Returns
            -----------------
            y_tkn : ERC20
                y token from mock pool                   
        """            
        
        return self.y_tkn        
    
    def get_time_stamp(self, state):
        
        """ get_time_stamp

            Get datetime time stamp for a given pool state
                
            Parameters
            -----------------
            state : str
                Mock pool state (ie, arb, swap)  

            Returns
            -----------------
            time : datetime
                datetime timestamp                    
        """          
        
        if(state == self.STATE_SWAP):
            return self.time_swap 
        else:
            return self.time_arb    
    
    def get_lp_price(self, state):
        
        """ get_lp_price

            Get liquidity pool price for a given pool state
                
            Parameters
            -----------------
            state : str
                Mock pool state (ie, arb, swap)  

            Returns
            -----------------
            price : float
                LP price x/y (NOTE: returns x/y not y/x due to a nuance in SolveDeltas class)                      
        """            
        
        if(state == self.STATE_SWAP):
            return self.price_swap 
        else:
            return self.price_arb
    
    def get_x_reserve(self, state):
        
        """ get_x_reserve

            Get liquidity pool x reserve for a given pool state
                
            Parameters
            -----------------
            state : str
                Mock pool state (ie, arb, swap)  

            Returns
            -----------------
            x reserve : float
                Amount of x reserve in pool                   
        """          
        
        if(state == self.STATE_SWAP):
            return self.x_amt_swap 
        else:
            return self.x_amt_arb       
        
    def get_y_reserve(self, state):
        
        """ get_y_reserve

            Get liquidity pool y reserve for a given pool state
                
            Parameters
            -----------------
            state : str
                Mock pool state (ie, arb, swap)  

            Returns
            -----------------
            y reserve : float
                Amount of y reserve in pool                   
        """         
        
        if(state == self.STATE_SWAP):
            return self.y_amt_swap 
        else:
            return self.y_amt_arb 
        
    def get_usd_trial_volume(self):
        
        """ get_usd_trial_volume

            Get trade volume valued in stable token (eg. USDC) that passes through mock pool after a trial pass
            
            Returns
            -----------------
            volume : float
                Amount of total volume that passes through pool on both sides (ie, x and y) of the trade                  
        """           
        
        return TreeAmountQuote().get_tot_y(self.lp, self.x_trial_amt, self.y_trial_amt)
        
    def get_0x_data(self):    
        
        """ get_0x_data

            Get returned JSON structure after 0x API call 
                
            Returns
            -----------------
            0x api data : dictionary
                JSON structure after 0x api call                   
        """          
        
        return self.api_0x_data      
        
    def get_market_price(self): 
        
        """ get_market_price

            Get market price returned from 0x API call 
                
            Returns
            -----------------
            price : float
                price valued in x/y (NOTE: returns x/y not y/x due to a nuance in SolveDeltas class)                   
        """          
        
        return 1/float(self.api_0x_data['price']) if self.api_0x_data != None else -1
    
    def call_0x_api(self):    
        
        """ call_0x_api

            Call 0x API  
                
            Returns
            -----------------
            0x api data : dictionary
                JSON structured 0x api call data                 
        """   
        call_api = self.api.apply(self.sell_token, self.buy_token, Chain0x().get_api_sell_amount())   
        return call_api if bool(call_api) else self.prev_api_0x_data   
    
    def init_lp(self, init_x_tkn, x_tkn_nm = None, y_tkn_nm = None, init_x_invest = 1):
        
        """ init_lp

            Initialize mock liquidity pool
                
            Parameters
            -----------------
            init_x_tkn : float
                Initial x token amount
            x_tkn_nm : str
                x token name                
            y_tkn_nm : str
                y token name
            init_x_invest : float
                Initial x mock investment into pool (eg. if x tkn is WETH then init_x_invest = 1 would be 1 WETH)                             
        """          
        
        self.state = self.STATE_INIT
        self.api_0x_data = self.call_0x_api()
        p = self.get_market_price()
        x_tkn_amt = init_x_tkn
        y_tkn_amt = x_tkn_amt*p
        
        x_tkn_nm = Chain0x.buy_tkn_nm if x_tkn_nm == None else x_tkn_nm
        y_tkn_nm = Chain0x.sell_tkn_nm if y_tkn_nm == None else y_tkn_nm

        self.x_tkn = ERC20(x_tkn_nm, None)
        self.y_tkn = ERC20(y_tkn_nm, None)
        exchg_data = UniswapExchangeData(tkn0 = self.x_tkn, tkn1 = self.y_tkn, symbol="LP", address=None)

        factory = UniswapFactory("ETH pool factory", None)
        self.lp = factory.deploy(exchg_data)
        self.lp.add_liquidity(USER_NM, x_tkn_amt, y_tkn_amt, x_tkn_amt, y_tkn_amt) 
        self.take_x_position(init_x_invest)
                
        self.arb = CorrectReserves(self.lp, x0 = p)
        self.time_init = datetime.datetime.now()

     
    def trial(self):
        
        """ trial

            One trial pass includes: 1 random swap where amount is Gamma distributed which offsets pool price
            from the market price that the 0x API returns; this event is followed by an arbitrage to bring
            mock pool price in balance with the market price
                
            Returns
            -----------------
            p : float
                LP price x/y (NOTE: returns x/y not y/x due to a nuance in SolveDeltas class)                      
        """            
        
        self._reset_trial()
        self.api_0x_data = self.call_0x_api()
        p = self.get_market_price()
        remaining_sleep = self.time_window
        
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
        
        self._update_investment()
        self.prev_api_0x_data = self.api_0x_data
        time.sleep(remaining_sleep) 

        return p
    
    def take_x_position(self, x_invest):
        
        """ take_x_position

            Take mock position on pool; this is for the purpose of monitoring investment performance
            of trade over time within simulation
                
            Parameters
            -----------------
            x_invest : float
                Mock x position; eg. we invest 1 WETH into pool to monitor performance                   
        """          
        
        x_invest = x_invest if x_invest == 1 else x_invest
        self.init_lp_invest = LPTokenQuote().get_x(self.lp, x_invest)
        SwapDeposit().apply(self.lp, self.get_x_tkn(), USER_NM, x_invest)
        self._update_investment()    
        
    def _random_swap(self, p):   
        self.state = self.STATE_SWAP
        rnd_amt = self.td_model.delta()
        self.amt_swap = rnd_amt
        select_tkn = EventSelectionModel().bi_select(self.trade_bias)
        bias_factor = 1
        
        if(select_tkn == 0):
            out = Swap().apply(self.lp, self.x_tkn, USER_NM, rnd_amt) 
            self.x_trial_amt += rnd_amt
        else:
            out = Swap().apply(self.lp, self.y_tkn, USER_NM,  bias_factor*p*rnd_amt)  
            self.y_trial_amt += bias_factor*p*rnd_amt
            
        self.time_swap = datetime.datetime.now() 
        self.x_amt_swap = self.lp.get_reserve(self.arb.get_x_tkn())
        self.y_amt_swap = self.lp.get_reserve(self.arb.get_y_tkn())
        self.price_swap = self.lp.get_price(self.arb.get_x_tkn())        
        
    def _update_investment(self): 
        self.x_redeem = IndexTokenQuote().get_x(self.lp, self.init_lp_invest)
        self.y_redeem = IndexTokenQuote().get_y(self.lp, self.init_lp_invest)
        
    def _reset_trial(self):
        self.x_trial_amt = 0
        self.y_trial_amt = 0
            
    def _market_arbitrage(self, p):  
        self.state = self.STATE_ARB
        self.arb.apply(p)
        self.x_trial_amt += self.arb.get_swap_dx()
        self.y_trial_amt += self.arb.get_swap_dy()
        
        self.time_arb = datetime.datetime.now()
        self.x_amt_arb = self.lp.get_reserve(self.arb.get_x_tkn())
        self.y_amt_arb = self.lp.get_reserve(self.arb.get_y_tkn())
        self.price_arb = self.lp.get_price(self.arb.get_x_tkn())            
                 