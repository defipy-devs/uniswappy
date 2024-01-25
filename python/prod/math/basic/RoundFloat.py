# RoundFloat.py
# Author: Ian Moore ( utiliwire@gmail.com )
# Date: Sept 2022

from decimal import Decimal

class RoundFloat():
    
    def apply(self, num, trunc_ratio = 0.5):
        n_float = self.n_float_digits(num)
        trunc = int(n_float*trunc_ratio)
        return round(num, trunc)
    
    def n_float_digits(self, num):
        d = Decimal(str(num))
        return abs(d.as_tuple().exponent)