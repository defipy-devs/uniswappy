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

from .IPS import IPS

class ConstantIPS(IPS):
       
    def __swap_balance(self, balance, price):
        
        if price == None:
            return balance
        else:
            return balance*price
        
    def calc_ips_from_state(self, state, price = None):
              
        A0 = state.get_balance() - state.get_yield() - state.get_delta()
        A0 = self.__swap_balance(A0, price)
        
        dt = state.get_event().get_time_delta()
        
        A1 = A0 + state.get_yield()
        A1 = self.__swap_balance(A1, price)
        
        return self.calc_ips(A0, A1, dt)
    
    def calc_ips(self, a0, a1, dt):
        return (a1/a0)**(1/dt) - 1
        