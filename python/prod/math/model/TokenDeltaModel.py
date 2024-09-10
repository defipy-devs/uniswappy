# Copyright [2023] [Ian Moore]
# Distributed under the MIT License (license terms are at http://opensource.org/licenses/MIT).
# Email: defipy.devs@gmail.com

import numpy as np
from .EventSelectionModel import EventSelectionModel
  
MAX_TRADE = 10000    
    
class TokenDeltaModel():
    
    def __init__(self, max_trade = 100, shape=1, scale=1):
        self.__shape = shape
        self.__scale = scale
        self.__max_trade = max_trade

    def apply(self, n = 1):
        
        if(n == 1):
            rval = self.delta(self.__max_trade)
            return min(rval, self.__max_trade)  
        else:
    
            res = []
            for k in range(n):
                rval = self.delta(self.__max_trade)
                res.append(min(rval,self.__max_trade))
                
            return res  
        
    def set_param(self, max_trade = 100, shape=1, scale=1):
        self.__shape = shape
        self.__scale = scale
        self.__max_trade = max_trade        
        
    def delta(self, p=1):
        self.__scale = self.__max_trade/5
        return self.add_sub(p)*np.random.gamma(self.__shape, self.__scale)   
    
    def add_sub(self, p):
        return 1 if bool(EventSelectionModel().bi_select(p)) else -1     