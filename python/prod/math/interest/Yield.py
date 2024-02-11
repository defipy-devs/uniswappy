# Copyright [2023] [Ian Moore]
# Distributed under the MIT License (license terms are at http://opensource.org/licenses/MIT).
# Email: defipy.devs@gmail.com

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