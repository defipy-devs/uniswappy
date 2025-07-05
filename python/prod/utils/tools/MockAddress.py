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

from ...math.basic import IDGenerator

ADDRESS_PREFIX = '0x'
ADDRESS_LENGTH = 40

class MockAddress():

    def __init__(self):
        pass

    def apply(self, n = 1, addr_len = None):
        if(n == 1):
            return self.gen_address(addr_len)
        else:
            out = []
            for k in range(n):
                out.append(self.gen_address(addr_len))
            return out
    
    def gen_address(self, addr_len): 
        addr_len = ADDRESS_LENGTH if addr_len == None else addr_len
        return ADDRESS_PREFIX+IDGenerator().apply(addr_len)