# Copyright [2024] [Ian Moore]
# Distributed under the MIT License (license terms are at http://opensource.org/licenses/MIT).
# Email: defipy.devs@gmail.com

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