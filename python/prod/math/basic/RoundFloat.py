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

from decimal import Decimal

class RoundFloat():
    
    def apply(self, num, trunc_ratio = 0.5):
        n_float = self.n_float_digits(num)
        trunc = int(n_float*trunc_ratio)
        return round(num, trunc)
    
    def n_float_digits(self, num):
        d = Decimal(str(num))
        return abs(d.as_tuple().exponent)