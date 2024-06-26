from ..quote import LPQuote
from ...utils.tools.v3 import UniV3Helper

class ChildLP():
    
    def __init__(self, lp):
        self.lp = lp 
        self.version = lp.version
        tokens = self.lp.factory.token_from_exchange[self.lp.name]
        self.x_tkn = tokens[lp.token0]
        self.y_tkn = tokens[lp.token1]  
        self.token0 = self.x_tkn.token_name
        self.token1 = self.y_tkn.token_name
        self.name = lp.name 
        self.factory = lp.factory
        self.tick_space = 1000
        self.reserve0 = None
        self.reserve1 = None
        self.virtual_reserve0 = None
        self.virtual_reserve1 = None   

    def summary(self):
        self._update()          
        print(f"Exchange {self.lp.name} ({self.lp.symbol})") 
        print(f"Real Reserves:   {self.x_tkn.token_name} = {self.reserve0}, {self.y_tkn.token_name} = {self.reserve1}")
        print(f"Virtual Reserves:   {self.x_tkn.token_name} = {self.virtual_reserve0}, {self.y_tkn.token_name} = {self.virtual_reserve1}")
        print(f"Price ({self.y_tkn.token_name}/{self.x_tkn.token_name}): {self.virtual_reserve1/self.virtual_reserve0}\n")
      
    def _update(self):
        self.reserve0, self.virtual_reserve0 = self._get_reserves(self.x_tkn)
        self.reserve1, self.virtual_reserve1 = self._get_reserves(self.y_tkn)

    def _get_reserves(self, tkn):
        reserve = self.lp.get_reserve(tkn)
        if(reserve == 0):
            virtual_reserve = 0
        else:      
            virtual_reserve = self.lp.get_virtual_reserve(tkn)
            if tkn.type == 'index':
                parent_lp = tkn.parent_lp
                parent_token = tkn.parent_tkn
                parent_lp_tkn_x = parent_lp.factory.token_from_exchange[parent_lp.name][parent_lp.token0]
                p = parent_lp.get_price(parent_lp_tkn_x)
                lwr_tick = UniV3Helper().get_price_tick(parent_lp, -1, p, 1000)
                upr_tick = UniV3Helper().get_price_tick(parent_lp, 1, p, 1000)
                reserve = LPQuote(False).get_amount_from_lp(parent_lp, parent_token, int(reserve), lwr_tick, upr_tick)
                virtual_reserve = LPQuote(False).get_amount_from_lp(parent_lp, parent_token, int(virtual_reserve), lwr_tick, upr_tick)
            
        return reserve, virtual_reserve

    def get_price(self, tkn):  
        self._update()  
        if(tkn.token_name == self.x_tkn.token_name):
            return self.virtual_reserve1/self.virtual_reserve0 
        elif(tkn.token_name == self.y_tkn.token_name):
            return self.virtual_reserve0/self.virtual_reserve1  
    
    def get_reserve(self, tkn):
        self._update()
        tokens = self.lp.factory.token_from_exchange[self.lp.name]
        x_tkn = tokens[self.lp.token0]
        y_tkn = tokens[self.lp.token1]        
        
        if(tkn.token_name == self.x_tkn.token_name):
            return self.reserve0 
        elif(tkn.token_name == self.y_tkn.token_name):
            return self.reserve1 

    def get_base_tkn(self, tkn):
        if tkn.type == 'index':
            base_lp = tkn.parent_lp
            base_token = tkn.parent_tkn
            return base_token
        else:
            return tkn

    def get_real_reserve(self, tkn):  
        return self.lp.get_reserve(tkn)

    def get_virtual_reserve(self, tkn): 
        self._update() 
        if(tkn.token_name == self.x_tkn.token_name):
            return self.virtual_reserve0  
        elif(tkn.token_name == self.y_tkn.token_name):
            return self.virtual_reserve1         
        