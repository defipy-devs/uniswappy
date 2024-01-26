# Swap.py
# Author: Ian Moore ( utiliwire@gmail.com )
# Date: May 2023

from ..Process import Process
from ...math.model import TokenDeltaModel
from ...math.model import EventSelectionModel
import math

class Swap(Process):
    
    """ Process to swap token X for token Y (and vice verse) 

        Parameters
        ----------
        self.ev : EventSelectionModel
            EventSelectionModel object to randomly generate buy vs sell events
        self.tDel : TokenDeltaModel
            TokenDeltaModel to randomly generate token amounts                 
    """       

    def __init__(self, ev = None, tDel = None):
        self.ev = EventSelectionModel() if ev  == None else ev
        self.tDel = TokenDeltaModel(50) if tDel == None else tDel
            
    def apply(self, lp, token_in, user_nm, amount_in):    
        
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
                
            Returns
            -------
            amount_out_expected : float
                exchanged token amount               
        """          
        
        amount_in = tDel.delta() if amount_in == None else amount_in
        amount_out = math.floor(lp.get_amount_out(amount_in, token_in))
        amount_out_expected = lp.swap_exact_tokens_for_tokens(amount_in, amount_out, token_in, to=user_nm)
        return amount_out_expected        
        
