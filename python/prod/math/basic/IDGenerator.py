# Copyright [2023] [Ian Moore]
# Distributed under the MIT License (license terms are at http://opensource.org/licenses/MIT).
# Email: defipy.devs@gmail.com

import string
import random

class IDGenerator():

    def get_chars(self):
        return string.ascii_lowercase

    def get_digits(self):
        return string.digits     
    
    def apply(self, n=6):
        chars =  self.get_chars() + self.get_digits() 
        return ''.join(random.choice(chars) for _ in range(n))
        
   