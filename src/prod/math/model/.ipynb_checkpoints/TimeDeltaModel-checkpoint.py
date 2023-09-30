import numpy as np

class TimeDeltaModel():   
    
    
    def __init__(self, no_time_delay = False):
        self.__no_time_delay = no_time_delay

    def apply(self, n = 1, p = 0.00001):  
        
        if(self.__no_time_delay):
            return [0] * n if n > 1 else 0
        elif(n == 1):
            return np.random.negative_binomial(1, p)  
        else:
            
            res = []
            for k in range(n):
                rval = np.random.negative_binomial(1, p)
                res.append(rval)
                
            return np.array(res)              

            
 