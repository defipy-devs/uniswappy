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
import queue

class ModelQueue():

    def __init__(self):
        self.__model_queue = queue.Queue()
      
    def size(self):
        return self.__model_queue.qsize()
    
    def apply(self, arr, n_points = None):     
        n_points = len(arr) if n_points == None else n_points  
        for k in range(n_points):
            self.__model_queue.put(arr[k])
            
        return self.__model_queue   