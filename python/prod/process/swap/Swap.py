# Copyright [2023] [Ian Moore]
# Distributed under the MIT License (license terms are at http://opensource.org/licenses/MIT).
# Email: defipy.devs@gmail.com

from ..Process import Process
from ...math.model import TokenDeltaModel
from ...math.model import EventSelectionModel
from ...utils.data import UniswapExchangeData
import math

class Swap(Process):
    
    """ Process to swap token X for token Y (and vice verse) 

        Parameters
        ----------
        ev : EventSelectionModel
            EventSelectionModel object to randomly generate buy vs sell events
        tDel : TokenDeltaModel
            TokenDeltaModel to randomly generate token amounts                 
    """       

    def __init__(self, ev = None, tDel = None):
        self.ev = EventSelectionModel() if ev  == None else ev
        self.tDel = TokenDeltaModel(50) if tDel == None else tDel
            
    def apply(self, lp, token_in, user_nm, amount_in, sqrt_price_limit = None):    
        
        """ apply

            Swap token X for token Y (and vice verse) 
                
            Parameters
            -------
            lp : Exchange
                LP exchange
            token_in : ERC20
                specified ERC20 token               
            user_nm : str
                account name
            amount_in : float
                token amount to be swap 
            lwr_tick : int
                lower tick of the position in which to add liquidity   
            upr_tick : int
                upper tick of the position in which to add liquidity                
                
            Returns
            -------
            amount_out_expected : float
                exchanged token amount               
        """          
        
        amount_in = tDel.delta() if amount_in == None else amount_in
        
        if(lp.version == UniswapExchangeData.VERSION_V2):
            amount_out = math.floor(lp.get_amount_out(amount_in, token_in))
            amount_out_expected = lp.swap_exact_tokens_for_tokens(amount_in, amount_out, token_in, to_addr=user_nm)
            
        elif(lp.version == UniswapExchangeData.VERSION_V3):
            tokens = lp.factory.token_from_exchange[lp.name]
            if(token_in.token_name == lp.token0):
                amount_out = lp.swapExact0For1(user_nm, amount_in, sqrt_price_limit)
                amount_out_expected = abs(amount_out[2])
            else: 
                amount_out = lp.swapExact1For0(user_nm, amount_in, sqrt_price_limit)
                amount_out_expected = abs(amount_out[1])
            
        return amount_out_expected        
        
