# SolveDeltas.py
# Author: Ian Moore ( utiliwire@gmail.com )
# Date: Mar 2023

from scipy.optimize import fsolve
import warnings
warnings.filterwarnings("ignore")

class SolveDeltas():
    
    def __init__(self, lp):
        self.x = lp.reserve0
        self.y = lp.reserve1
        self.tkn_x = lp.factory.exchange_to_tokens[lp.name][lp.token0]
        self.tkn_y = lp.factory.exchange_to_tokens[lp.name][lp.token1]      
        self.p = lp.get_price(self.tkn_x)
        self.p_prev = lp.get_price(self.tkn_x)
        self.lp = lp
        self.dp = 0
              
    def get_lp(self):
        return self.lp   
                    
    def func_swap_yx(self, z):
        z[0] = 1 if z[0] == 0 else z[0]
        return [(self.x*abs(z[1]) + abs(z[0])*self.y)/(self.x**2 - abs(z[0])*self.x) - self.dp,
                abs(z[1])/abs(z[0]) - self.p ]

    def func_swap_xy(self, z):
        z[0] = 1 if z[0] == 0 else z[0]
        return [-(self.x*abs(z[1]) + abs(z[0])*self.y)/(self.x**2 + abs(z[0])*self.x) - self.dp,
                abs(z[1])/abs(z[0]) - self.p]
        
    def calc(self, p, x0 = None, fac = None):
        self.p = p
        self.p_prev = self.lp.get_price(self.tkn_x) 
        self.dp = p - self.p_prev
        self.x = self.lp.reserve0
        self.y = self.lp.reserve1
        fac = 0.1 if fac == None else fac
        dx0 = 0.5 if x0 == None else x0/p
        dy0 = 0.5 if x0 == None else x0
        if(self.dp >= 0):
            dx, dy = fsolve(self.func_swap_yx, [dx0, dy0], xtol=1e-6, factor=fac, maxfev = 200)
            self.p_prev = p
            return -dx, dy
        else:
            dx, dy = fsolve(self.func_swap_xy, [dx0, dy0], xtol=1e-6, factor=fac, maxfev = 200)
            self.p_prev = p
            return dx, -dy        