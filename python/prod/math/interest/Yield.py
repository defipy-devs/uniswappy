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

DAYS_IN_YEAR = 365.25
HOURS_IN_DAY = 24
SECONDS_IN_HOUR = 3600

class Yield():
             
    def __seconds_per_year(self):
        return DAYS_IN_YEAR*HOURS_IN_DAY*SECONDS_IN_HOUR

    def apply(self, A0, delta_t, apy):  
        multiplier = 1 + apy
        freq = self.__seconds_per_year()
        A1 = A0*(multiplier)**(delta_t/freq)
        return A1-A0