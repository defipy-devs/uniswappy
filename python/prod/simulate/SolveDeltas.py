# Copyright [2023] [Ian Moore]
# Distributed under the MIT License (license terms are at http://opensource.org/licenses/MIT).
# Email: defipy.devs@gmail.com

from scipy.optimize import fsolve
from ..utils.data import UniswapExchangeData
import warnings
warnings.filterwarnings("ignore")

class SolveDeltas():
    
    def __init__(self, lp):
        self.lp = lp
        self.tkn_x = lp.factory.token_from_exchange[lp.name][lp.token0]
        self.tkn_y = lp.factory.token_from_exchange[lp.name][lp.token1]      
        self.x = self._get_reserve(self.tkn_x) 
        self.y = self._get_reserve(self.tkn_y)       
        self.p = lp.get_price(self.tkn_x)
        self.p_prev = lp.get_price(self.tkn_x)
        self.dp = 0
              
    def get_lp(self):
        return self.lp   
                    
    def func_swap_yx(self, z):
        z[0] = 1 if z[0] == 0 else z[0]
        return [(self.x*abs(z[1]) + abs(z[0])*self.y)/(self.x**2 - abs(z[0])*self.x) - self.dp,
                abs(z[1])/abs(z[0]) - self.p]

    def func_swap_xy(self, z):
        z[0] = 1 if z[0] == 0 else z[0]
        return [-(self.x*abs(z[1]) + abs(z[0])*self.y)/(self.x**2 + abs(z[0])*self.x) - self.dp,
                abs(z[1])/abs(z[0]) - self.p]
        
    def calc(self, p, x0 = None, fac = None):
        self.p = p
        self.p_prev = self.lp.get_price(self.tkn_x) 
        self.dp = p - self.p_prev
        self.x = self._get_reserve(self.tkn_x)
        self.y = self._get_reserve(self.tkn_y)   
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

    def _get_reserve(self, tkn):
        
        if(self.lp.version == UniswapExchangeData.VERSION_V2):
            return self.lp.get_reserve(tkn) 
        elif(self.lp.version == UniswapExchangeData.VERSION_V3):
            return self.lp.get_virtual_reserve(tkn)