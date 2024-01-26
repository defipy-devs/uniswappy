# ConstantIPS.py
# Author: Ian Moore ( utiliwire@gmail.com )
# Date: Sept 2022

from .IPS import IPS

class ConstantIPS(IPS):
       
    def __swap_balance(self, balance, price):
        
        if price == None:
            return balance
        else:
            return balance*price
        
    def calc_ips_from_state(self, state, price = None):
              
        A0 = state.get_balance() - state.get_yield() - state.get_delta()
        A0 = self.__swap_balance(A0, price)
        
        dt = state.get_event().get_time_delta()
        
        A1 = A0 + state.get_yield()
        A1 = self.__swap_balance(A1, price)
        
        return self.calc_ips(A0, A1, dt)
    
    def calc_ips(self, a0, a1, dt):
        return (a1/a0)**(1/dt) - 1
        