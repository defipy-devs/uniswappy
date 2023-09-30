# CompoundReturn.py
# Author: Ian Moore ( imoore@syscoin.org )
# Date: Sept 2022

from src.prod.math.basic import RoundFloat

class CompoundReturn():        
       
    __DEC = 5    
        
    def apply(self, A0, n_compounds, ips, t_ratio = 0.3):
        res = (A0)*(1+ips)**(n_compounds)
        return RoundFloat().apply(res, t_ratio)      