# Copyright [2024] [Ian Moore]
# Distributed under the MIT License (license terms are at http://opensource.org/licenses/MIT).
# Email: defipy.devs@gmail.com

from ..simulate import SolveDeltas
from ..process.deposit import SwapDeposit
from ..process.swap import WithdrawSwap
import numpy as np

X0 = 1
FAC = 1
MAX_ATTEMPTS = 5
USER_NM = 'reserve_correction'

class CorrectReserves:
    
    """ 
        Applies SolveDeltas to Correct x/y reserve amounts so that price reflects desired input price; 
        in the case for the BUIDL week event, it would be the most recent market price returned from 
        the 0x API 
        
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
    
    def apply(self, p): 
        
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
                self._update(p)
                do_update = False 
            except:
                p = p + np.random.normal(0, 0.1)  
                do_update = True 
                
        assert c != MAX_ATTEMPTS, 'UniswapV2: RESERVE_CORRECTION_FAILURE'   
        
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
                
    def _update(self, p):  
        tkn_x = self.get_x_tkn()
        tkn_y = self.get_y_tkn()
        
        self.swap_dx, self.swap_dy = self.sDel.calc(p, self.x0, self.fac)   
        if(self.swap_dx >= 0):
            expected_amount_dep = SwapDeposit().apply(self.lp, tkn_x, USER_NM, abs(self.swap_dx))
            expected_amount_out = WithdrawSwap().apply(self.lp, tkn_y, USER_NM, abs(self.swap_dy))
        elif(self.swap_dy >= 0):
            expected_amount_dep = SwapDeposit().apply(self.lp, tkn_y, USER_NM, abs(self.swap_dy))
            expected_amount_out = WithdrawSwap().apply(self.lp, tkn_x, USER_NM, abs(self.swap_dx))                   
            

        
        