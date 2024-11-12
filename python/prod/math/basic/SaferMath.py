from decimal import *

MAX_UINT256 = 2**256 - 1

class SaferMath():

    def __init__(self):
        pass

    def add_div_round(self, x, y, z):
        val = self.div_round(self.add(x, y), z)
        return int(val)
    
    def add_div(self, x, y, z):
        val = (Decimal(str(x))+Decimal(str(y)))/Decimal(str(z))
        return int(val)
    
    def mul_div(self, x, y, z):
        val = (Decimal(str(x))*Decimal(str(y)))/Decimal(str(z))
        return int(val)
    
    def exp(self, x, y):
        val = Decimal(str(x)) ** Decimal(str(y))
        return int(val)
    
    def div(self, x, y):
        val = Decimal(str(x))/Decimal(str(y))
        return int(val)
    
    def add(self, x, y):
        val = Decimal(str(x))+Decimal(str(y))
        return int(val)
        
    def mul(self, x, y):
        val = Decimal(str(x))*Decimal(str(y))
        return int(val)

    def div_round(self, x, y):
        try:
            result = Decimal(str(x))//Decimal(str(y))
            if Decimal(str(x)) % Decimal(str(y))  > 0:
                result += 1
            self.check_uint_256(int(result))
        except:
            result = self.div(x, y)
            
        return int(result)

    def mul_div_round(self, x, y, z):
        return self.div_round(self.mul(x, y), z)
    
    def check_uint_256(self, val):
        assert val >= 0 and val <= MAX_UINT256, "OF or UF of UINT256"
        assert type(val) == int, "Not an integer"
        
