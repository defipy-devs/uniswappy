# ─────────────────────────────────────────────────────────────────────────────
# Apache 2.0 License (DeFiPy)
# ─────────────────────────────────────────────────────────────────────────────
# Copyright 2023–2025 Ian Moore
# Email: defipy.devs@gmail.com
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License

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