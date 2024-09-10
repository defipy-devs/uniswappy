# Copyright [2024] [Ian Moore]
# Distributed under the MIT License (license terms are at http://opensource.org/licenses/MIT).
# Email: defipy.devs@gmail.com

from ..simulate import SolveDeltas
from ..process.deposit import SwapDeposit
from ..process.swap import WithdrawSwap
from ..utils.data import UniswapExchangeData
import numpy as np

X0 = 1
FAC = 1
MAX_ATTEMPTS = 5
USER_NM = 'reserve_correction'

class CorrectReserves:
    
    """ 
        Applies SolveDeltas to Correct x/y reserve amounts so that price reflects desired input price; 
        in the marjority of cases, the input price would be the most recent outside market price 
        
        Parameters
        -----------------
        lp : UniswapExchange
            Uniswap Exchange class
        x0 : float
            Initial market price at the beginning of the simulation 
        fac : float
            scipy.fsolve parameter for non-linear solver found in SolveDeltas class
    """             
    
    def __init__(self, lp, x0 = None, fac = None):
        self.lp = lp
        self.sDel = SolveDeltas(lp)
        self.x0 = X0 if x0 == None else int(x0)
        self.fac = FAC if fac == None else fac
        self.swap_dx = 0
        self.swap_dy = 0
        self.user_nm = USER_NM

    def set_user(self, user_nm): 
        self.user_nm = user_nm    
    
    def get_swap_dx(self): 
        
        """ get_swap_dx

            Get delta x reserve adjustment from SolveDeltas class
                
            Returns
            -----------------
            swap_dx : float
                Delta x reserve adjustment from SolveDeltas class                   
        """         
        
        return self.swap_dx
    
    def get_swap_dy(self): 
        
        """ get_swap_dy

            Get delta y reserve adjustment from SolveDeltas class
                
            Returns
            -----------------
            swap_dy : float
                Delta y reserve adjustment from SolveDeltas class                   
        """           
        
        return self.swap_dy    
    
    def apply(self, p, lwr_tick = None, upr_tick = None): 
        
        """ apply

            Apply reserve correction of mock pool given external price (eg. market price from 0x API)
                
            Parameters
            -----------------
            p : float
                Price (eg. market price from 0x API)               
        """         
        
        do_update = True  
        max_tries = 5; c = 0
        while(do_update and c <= MAX_ATTEMPTS):
            c=+1
            try: 
                self._update(p, lwr_tick, upr_tick)
                do_update = False 
            except:
                p = p + np.random.normal(0, 0.001)  
                do_update = True 
                
        assert c != MAX_ATTEMPTS, 'Uniswap: RESERVE_CORRECTION_FAILURE'   
        
    def get_x_tkn(self): 
        
        """ get_x_tkn

            Get x token from Uniswap mock pool
                
            Returns
            -----------------
            x_tkn : ERC20
                x token from mock pool                   
        """         
        
        return self.lp.factory.token_from_exchange[self.lp.name][self.lp.token0]
        
    def get_y_tkn(self):     
        
        """ get_y_tkn

            Get y token from Uniswap mock pool
                
            Returns
            -----------------
            y_tkn : ERC20
                y token from mock pool                   
        """           
        
        return self.lp.factory.token_from_exchange[self.lp.name][self.lp.token1]        
                
    def _update(self, p, lwr_tick, upr_tick):  
        tkn_x = self.get_x_tkn()
        tkn_y = self.get_y_tkn()
        self.swap_dx, self.swap_dy = self.sDel.calc(p, self.x0, self.fac)

        if(self.lp.version == UniswapExchangeData.VERSION_V2):
            if(self.swap_dx >= 0):
                expected_amount_dep = SwapDeposit().apply(self.lp, tkn_x, self.user_nm, abs(self.swap_dx))
                expected_amount_out = WithdrawSwap().apply(self.lp, tkn_y, self.user_nm, abs(self.swap_dy))
            elif(self.swap_dy >= 0):
                expected_amount_dep = SwapDeposit().apply(self.lp, tkn_y, self.user_nm, abs(self.swap_dy))
                expected_amount_out = WithdrawSwap().apply(self.lp, tkn_x, self.user_nm, abs(self.swap_dx)) 
               
        elif(self.lp.version == UniswapExchangeData.VERSION_V3):
            if(self.swap_dx >= 0):
                expected_amount_dep = SwapDeposit().apply(self.lp, tkn_x, self.user_nm, abs(self.swap_dx), lwr_tick, upr_tick)
                expected_amount_out = WithdrawSwap().apply(self.lp, tkn_y, self.user_nm, abs(self.swap_dy), lwr_tick, upr_tick)
            elif(self.swap_dy >= 0):
                expected_amount_dep = SwapDeposit().apply(self.lp, tkn_y, self.user_nm, abs(self.swap_dy), lwr_tick, upr_tick)
                expected_amount_out = WithdrawSwap().apply(self.lp, tkn_x, self.user_nm, abs(self.swap_dx), lwr_tick, upr_tick)


    def get_ticks(self, tkn_x):
        lwr_tick = UniV3Helper().get_tick_price(self.lp, -1, lp.get_price(tkn_x), 1000)
        upr_tick = UniV3Helper().get_tick_price(self.lp, 1, lp.get_price(tkn_x), 1000)
        return lwr_tick, upr_tick
              
         