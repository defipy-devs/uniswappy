# Copyright [2023] [Ian Moore]
# Distributed under the MIT License (license terms are at http://opensource.org/licenses/MIT).
# Email: defipy.devs@gmail.com

import numpy as np

class EventSelectionModel():
    
    FIRST = 0 
    SECOND = 1 
    THIRD = 1     

    def bi_select(self, p):  
        p = max(min(p, 1), 0)
        return np.random.choice(2, 1, p=[1-p,p])[0]
    
    def tri_select(self, p1, p2):     
        p3 = 1 - p1 - p2
        return np.random.choice(3, 1, p=[p1, p2, p3])[0]    