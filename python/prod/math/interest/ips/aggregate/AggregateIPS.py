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
from ..IPS import IPS

class AggregateIPS():
    
    def __init__(self, ips, states = []):
        self.__states = states
        self.__ips = ips
        
    def update_states(self, states):
        self.__states = states

    def apply(self, states):
        aggr = 0
        for k in range(len(states)):
            aggr += self.__ips.calc_ips_from_state(states[k])
        return aggr/len(states)    
        