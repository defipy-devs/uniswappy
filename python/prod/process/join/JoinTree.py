# Copyright [2023] [Ian Moore]
# Distributed under the MIT License (license terms are at http://opensource.org/licenses/MIT).
# Email: defipy.devs@gmail.com

from ..Process import Process
from ..liquidity import AddLiquidity
from ..mint import SwapIndexMint
from ...cpt.quote import LPQuote
from ...math.model import TokenDeltaModel
from ...math.model import EventSelectionModel
from ...utils.data import UniswapExchangeData
from ...utils.tools.v3 import UniV3Helper

class JoinTree(Process):

    """ Process to join tree with liquidity 

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
            
    def apply(self, child_lp, user_nm, iVault, parent_tkn_amt, lwr_tick = None, upr_tick = None):    
        
        """ apply

            Join x amounts to parent pool, and swap index mint into child LP
                
            Parameters
            -------
            lp : Exchange
                LP exchange
            iVault : iVault
                specified index vault               
            user_nm : str
                account name
            lp_amt_in : float
                lp token amount to be added 
                                
            Returns
            -------
            (amount_in, amount_out) : float, float
                token swap amounts                
        """  

        lp_tkns = child_lp.factory.token_from_exchange[child_lp.name]
        x_tkn = lp_tkns[[*lp_tkns][0]]
        y_tkn = lp_tkns[[*lp_tkns][1]]
    
        parent_lp = child_lp.factory.parent_lp
        parent_lp_tkns = parent_lp.factory.token_from_exchange[parent_lp.name]
        parent_x_tkn = parent_lp_tkns[[*parent_lp_tkns][0]]
        parent_y_tkn = parent_lp_tkns[[*parent_lp_tkns][0]]    
        
        itkn_nm = y_tkn.token_name
        parent_tkn = parent_y_tkn
        parent_lp = child_lp.factory.parent_lp
        SwapIndexMint(iVault).apply(parent_lp, parent_tkn, user_nm, parent_tkn_amt)
        mint_itkn_deposit = iVault.index_tokens[itkn_nm]['last_lp_deposit']
        opposite_tkn = x_tkn.token_name != parent_tkn.token_name
        tkn_amount1 = LPQuote(opposite_tkn).get_amount_from_lp(parent_lp, parent_tkn, mint_itkn_deposit) 
        price_itkn = tkn_amount1/mint_itkn_deposit 
        return AddLiquidity(price_itkn).apply(child_lp, y_tkn, user_nm, mint_itkn_deposit) 
        
