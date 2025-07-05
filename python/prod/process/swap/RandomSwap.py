# Copyright 2023–2025 Ian Moore
# Email: defipy.devs@gmail.com
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License

from ..Process import Process
from ...math.model import TokenDeltaModel
from ...math.model import EventSelectionModel
from ...process.swap import Swap

class RandomSwap(Process):
    
    """ Process to randomly swap token X for token Y (and vice verse) 

        Parameters
        ----------
        ev : EventSelectionModel
            EventSelectionModel object to randomly generate buy vs sell events
        tDel : TokenDeltaModel
            TokenDeltaModel to randomly generate token amounts                 
    """           

    def __init__(self, p = None, ev = None, tDel = None):
        self.ev = EventSelectionModel() if ev  == None else ev
        self.tDel = TokenDeltaModel(50) if tDel == None else tDel
        self.buy_sell_prob = 0.5 if p == None else p
        
    def set_buy_sell_prob(self, p):
        self.buy_sell_prob = p
            
    def apply(self, lp, token_in, user_nm, amount_in = None):    
        
        """ apply

            Randomly swap token X for token Y (and vice verse) 
                
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
        
        amount_in = self.tDel.delta() if amount_in == None else amount_in
        direction = self.ev.bi_select(self.buy_sell_prob) 
        tokens = lp.factory.token_from_exchange[lp.name]
        
        
        #print('direction {}, p {}'.format(direction, self.buy_sell_prob))

        if(direction == 0):
            token_in = tokens[lp.token0]
            amount_out_expected = Swap().apply(lp, token_in, user_nm, amount_in)
        elif(direction == 1):
            token_in = tokens[lp.token1]
            amount_out_expected = Swap().apply(lp, token_in, user_nm, amount_in)

        return amount_out_expected    
        
