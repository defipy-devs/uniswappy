# IDGenerator.py
# Author: Ian Moore ( utiliwire@gmail.com )
# Date: Sept 2022

import string
import random

class IDGenerator():

    def get_chars(self):
        return string.ascii_uppercase

    def get_digits(self):
        return string.digits     
    
    def apply(self, n=6):
        chars =  self.get_chars() + self.get_digits() 
        return '_' + ''.join(random.choice(chars) for _ in range(n))
        
   