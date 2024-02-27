# Copyright [2024] [Ian Moore]
# Distributed under the MIT License (license terms are at http://opensource.org/licenses/MIT).
# Email: defipy.devs@gmail.com

from ..simulate import SolveDeltas
from ..process.deposit import SwapDeposit
from ..process.swap import WithdrawSwap
import numpy as np

X0 = 1
FAC = 1
USER_NM = 'reserve_correction'
MAX_ATTEMPTS = 5

class CorrectReserves:
    
    def __init__(self, lp, x0 = None, fac = None):
        self.lp = lp
        self.sDel = SolveDeltas(lp)
        self.x0 = X0 if x0 == None else int(x0)
        self.fac = FAC if fac == None else fac
        self.swap_dx = 0
        self.swap_dy = 0
    
    def get_swap_dx(self): 
        return self.swap_dx
    
    def get_swap_dy(self): 
        return self.swap_dy    
    
    def apply(self, p): 
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
            
    def get_x_tkn(self): 
        return self.lp.factory.token_from_exchange[self.lp.name][self.lp.token0]
        
    def get_y_tkn(self):     
        return self.lp.factory.token_from_exchange[self.lp.name][self.lp.token1]
        
        