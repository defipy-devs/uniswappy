from scipy.optimize import fsolve
import warnings
warnings.filterwarnings("ignore")

class SolveDeltas():
    
    def __init__(self, liq):
        self.x = liq.get_x_real()
        self.y = liq.get_y_real()
        self.p = liq.get_price()
        self.dx = liq.get_x_delta()
        self.dy = liq.get_y_delta()
        self.p_prev = self.y/self.x
        self.liq = liq
        self.x_fee = 0
        self.y_fee = 0
        self.dp = 0
     
    def apply(self, p):    
        self.dx, self.dy = self.calc_dx_dy(p)
        self.updates(p)
        self.x_fee = self.liq.get_x_fee()
        self.y_fee = self.liq.get_y_fee()  
        return self.dx, self.dy
    
    def get_x_fee(self):
        return self.x_fee 
   
    def get_y_fee(self):
        return self.y_fee 
        
    def updates(self, p):
        self.liq.swap(self.dx, self.dy)
        self.p_prev = p
        
    def add_dx(self, dx): 
        self.liq.add_delta_x(dx)
        self.p_prev = self.liq.get_price()
        
    def add_dy(self, dy): 
        self.liq.add_delta_y(dy) 
        self.p_prev = self.liq.get_price()
                
    def get_liquidity(self):
        return self.liq   
                    
    def func_swap_yx(self, z):
        z[0] = 1 if z[0] == 0 else z[0]
        return [(self.x*abs(z[1]) + abs(z[0])*self.y)/(self.x**2 - abs(z[0])*self.x) - self.dp,
                abs(z[1])/abs(z[0]) - self.p ]

    def func_swap_xy(self, z):
        z[0] = 1 if z[0] == 0 else z[0]
        return [-(self.x*abs(z[1]) + abs(z[0])*self.y)/(self.x**2 + abs(z[0])*self.x) - self.dp,
                abs(z[1])/abs(z[0]) - self.p]

    def calc_dx_dy(self, p):
        self.p = p
        self.dp = p - self.p_prev
        self.x = self.liq.get_x_real()
        self.y = self.liq.get_y_real()
        if(self.dp >= 0):
            dx, dy = fsolve(self.func_swap_yx, [0.5, 0.5], xtol=1e-6, factor=0.1, maxfev = 200)
            return -dx, dy
        else:
            dx, dy = fsolve(self.func_swap_xy, [0.5, 0.5], xtol=1e-6, factor=0.1, maxfev = 200)
            return dx, -dy
        
    def calc_dx_dy2(self, p, x, y):
        self.p = p
        self.dp = p - self.p_prev
        self.x = x
        self.y = y
        if(self.dp >= 0):
            dx, dy = fsolve(self.func_swap_yx, [0.5, 0.5], xtol=1e-6, factor=0.1, maxfev = 200)
            self.p_prev = p
            return -dx, dy
        else:
            dx, dy = fsolve(self.func_swap_xy, [0.5, 0.5], xtol=1e-6, factor=0.1, maxfev = 200)
            self.p_prev = p
            return dx, -dy        