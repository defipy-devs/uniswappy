# AggregateIPS.py
# Author: Ian Moore ( imoore@syscoin.org )
# Date: Sept 2022

from python.prod.math.interest.ips import IPS

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
        