# Copyright [2023] [Ian Moore]
# Distributed under the MIT License (license terms are at http://opensource.org/licenses/MIT).
# Email: defipy.devs@gmail.com

from ..Process import Process
from ...math.model import TokenDeltaModel
from ...math.model import EventSelectionModel
from ...utils.data import UniswapExchangeData
from ...utils.tools.v3 import UniV3Helper

class AddLiquidity(Process):
     
    """ Add liquidity process

        Parameters
        ----------
        ev : EventSelectionModel
            EventSelectionModel object to randomly generate buy vs sell events
        tDel : TokenDeltaModel
            TokenDeltaModel to randomly generate token amounts        
    """     

    def __init__(self, init_price = None, ev = None, tDel = None):
        self.ev = EventSelectionModel() if ev  == None else ev
        self.tDel = TokenDeltaModel(50) if tDel == None else tDel
        self.init_price = 1 if init_price == None else init_price
            
    def apply(self, lp, token_in, user_nm, amount_in, lwr_tick = None, upr_tick = None):    
        
        """ apply

            Adds liquidity using only X or Y amounts
                
            Parameters
            -------
            lp : Exchange
                LP exchange
            token_in : ERC20
                specified ERC20 token               
            user_nm : str
                account name
            amount_in : float
                token amount to be add to liquidity 
            lwr_tick : int
                lower tick of the position in which to add liquidity   
            upr_tick : int
                upper tick of the position in which to add liquidity                  
                
            Returns
            -------
            (amount_in, amount_out) : float, float
                token swap amounts                
        """          
        
        amount_in = tDel.delta() if amount_in == None else amount_in
        tokens = lp.factory.token_from_exchange[lp.name]  

        if(lp.version == UniswapExchangeData.VERSION_V2):

            res0 = lp.get_reserve(tokens[lp.token0])
            res1 = lp.get_reserve(tokens[lp.token1])
            tot_liq = lp.get_liquidity()
            
            if(token_in.token_name == lp.token0):
                balance0 = amount_in         
                if(res1 > 0):
                    balance1 = lp.quote(amount_in, res0, res1)
                else:
                    balance1 = self.init_price*balance0  
                    
                lp.add_liquidity(user_nm, balance0, balance1, balance0, balance1)
                
            elif(token_in.token_name == lp.token1):
                balance1 = amount_in
                if(res0 > 0):
                    balance0 = lp.quote(amount_in, res1, res0)
                else:
                    balance0 = self.init_price*balance1            
                
                lp.add_liquidity(user_nm, balance0, balance1, balance0, balance1) 

        elif(lp.version == UniswapExchangeData.VERSION_V3): 

            sqrt_P = lp.slot0.sqrtPriceX96/2**96
            if(token_in.token_name == lp.token0):
                Lx = UniV3Helper().calc_Lx(sqrt_P, amount_in, lwr_tick, upr_tick)
                (balance0, balance1)  = lp.mint(user_nm, lwr_tick, upr_tick, Lx)
            elif(token_in.token_name == lp.token1): 
                Ly = UniV3Helper().calc_Ly(sqrt_P, amount_in, lwr_tick, upr_tick)
                (balance0, balance1) = lp.mint(user_nm, lwr_tick, upr_tick, Ly)  

        return {lp.token0:balance0, lp.token1:balance1}    
    
 
        
