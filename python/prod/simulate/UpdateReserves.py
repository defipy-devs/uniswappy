# Copyright [2024] [Ian Moore]
# Distributed under the MIT License (license terms are at http://opensource.org/licenses/MIT).
# Email: defipy.devs@gmail.com

from ..simulate import SolveDeltas
from ..process.deposit import SwapDeposit
from ..process.swap import WithdrawSwap

X0 = 1
FAC = 1
USER_NM = 'adjust'

class UpdateReserves:
    
    def __init__(self, lp, x0 = None, fac = None):
        self.lp = lp
        self.sDel = SolveDeltas(lp)
        self.x0 = X0 if x0 == None else int(x0)
        self.fac = FAC if fac == None else fac
        
    def apply(self, p): 
        tkn_x = self.get_x_tkn()
        tkn_y = self.get_y_tkn()
        
        swap_dx, swap_dy = self.sDel.calc(p, self.x0, self.fac)   
        if(swap_dx >= 0):
            expected_amount_dep = SwapDeposit().apply(self.lp, tkn_x, USER_NM, abs(swap_dx))
            expected_amount_out = WithdrawSwap().apply(self.lp, tkn_y, USER_NM, abs(swap_dy))
        elif(swap_dy >= 0):
            expected_amount_dep = SwapDeposit().apply(self.lp, tkn_y, USER_NM, abs(swap_dy))
            expected_amount_out = WithdrawSwap().apply(self.lp, tkn_x, USER_NM, abs(swap_dx)) 
            
    def get_x_tkn(self): 
        return self.lp.factory.token_from_exchange[self.lp.name][self.lp.token0]
        
    def get_y_tkn(self):     
        return self.lp.factory.token_from_exchange[self.lp.name][self.lp.token1]
        
        