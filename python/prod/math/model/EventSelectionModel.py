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