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

            
 