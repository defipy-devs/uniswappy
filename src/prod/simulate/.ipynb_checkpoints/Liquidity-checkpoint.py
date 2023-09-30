# Based on Uniswap v1 and v2 (see Reference 1); for Uniswap v3 see reference 2

# References: 

# [1] Pandichef, A Brief History of Uniswap and Its Math 
# Link: https://pandichef.medium.com/a-brief-history-of-uniswap-and-its-math-90443241c9b7

# [2] Atis Elsts, Liquidity Math in Uniswap V3  
# Link: https://atiselsts.github.io/pdfs/uniswap-v3-liquidity-math.pdf

import numpy as np
import copy

YX_PRICE = 'YX'
XY_PRICE = 'XY'
FEE = 3/1000

class Liquidity():
    
    def __init__(self, x_real, y_real, x_name, y_name):
        self.__x_real = x_real
        self.__y_real = y_real  
        self.__x_name = x_name
        self.__y_name = y_name        
        self.__liquidity_val = 0
        self.__yx_price = None 
        self.__y_fee = None 
        self.__x_fee = None         
        self.__x_delta = 0
        self.__y_delta = 0           
       
    def get_x_real(self):
        return self.__x_real

    def get_y_real(self):
        return self.__y_real
    
    def get_x_delta(self):
        return self.__x_delta

    def get_y_delta(self):
        return self.__y_delta   
    
    def get_x_fee(self):
        return self.__x_fee

    def get_y_fee(self):
        return self.__y_fee     
    
    def get_x_name(self):
        return self.__x_name  
    
    def get_y_name(self):
        return self.__y_name      
    
    def get_liquidity_val(self):
        self.calc()
        return self.__liquidity_val  
      
    def get_price(self, direction = 'YX'): 
        
        if(self.__yx_price == None):
            self.calc()    
            
        if direction == YX_PRICE:
            return self.__yx_price
        else: 
            return 1/self.__yx_price    
          
    def set_y_real(self, y_real):
        self.__y_real = y_real
        
    def set_x_real(self, x_real):
        self.__x_real = x_real
        
    def set_x_name(self, x_name):
        self.__x_name = x_name  
    
    def set_y_name(self, y_name):
        self.__y_name = y_name  
    
    def swap(self, x_delta, y_delta):
        self.__x_fee = self.calc_fee(x_delta)
        self.__y_fee = self.calc_fee(y_delta)
        #x_delta = x_delta - self.__x_fee
        #y_delta = y_delta - self.__y_fee
        self.add_delta_x(x_delta)
        self.add_delta_y(y_delta)
        return -x_delta if x_delta < 0 else -y_delta
        
    def add_delta_x(self, x_delta):
        self.__x_delta = x_delta
        self.__x_real = self.__x_real + x_delta 
        self.__liquidity_val = self.calc()
        
    def add_delta_y(self, y_delta):
        self.__y_delta = y_delta 
        self.__y_real = self.__y_real + y_delta 
        self.__liquidity_val = self.calc()
        
    def calc_fee(self, delta):
        fee = FEE*delta if delta > 0 else 0
        fee = fee if fee > 1e-8 else 0
        return fee
        
    def calc(self): 
        
        self.__prev_liquidity_val = copy.copy(self.__liquidity_val)
        if(self.__x_real != 0):
            self.__liquidity_val = np.sqrt(self.__x_real*self.__y_real)
            self.__yx_price = self.calc_price()

        return self.__liquidity_val
    
    def calc_price(self): 
        if(self.__liquidity_val == 0):
            return 0
        else:
            return self.__y_real**2/self.__liquidity_val**2