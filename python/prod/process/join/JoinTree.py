# ─────────────────────────────────────────────────────────────────────────────
# Apache 2.0 License (DeFiPy)
# ─────────────────────────────────────────────────────────────────────────────
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
from ..liquidity import AddLiquidity
from ..mint import SwapIndexMint
from ...cpt.quote import LPQuote
from ...math.model import TokenDeltaModel
from ...math.model import EventSelectionModel
from ...utils.data import UniswapExchangeData
from ...utils.data import LPType
from ...utils.tools.v3 import UniV3Helper

DEFAULT_TYPE = LPType.HYBRID

class JoinTree(Process):

    """ Process to join tree with liquidity 

        Parameters
        ----------
        ev : EventSelectionModel
            EventSelectionModel object to randomly generate buy vs sell events
        tDel : TokenDeltaModel
            TokenDeltaModel to randomly generate token amounts        
    """     

    def __init__(self, lp_type = None, init_price = None, ev = None, tDel = None):
        self.lp_type = DEFAULT_TYPE if lp_type  == None else lp_type
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

        match self.lp_type:
            case LPType.HYBRID:
                return self._hybrid(child_lp, user_nm, iVault, parent_tkn_amt, lwr_tick, upr_tick)
            case LPType.SYNTHETIC:
                return self._synthetic(child_lp, user_nm, iVault, parent_tkn_amt, lwr_tick, upr_tick)

    def _hybrid(self, child_lp, user_nm, iVault, parent_tkn_amt, lwr_tick, upr_tick):  
        
        lp_tkns = child_lp.factory.token_from_exchange[child_lp.name]
        x_tkn = lp_tkns[[*lp_tkns][0]]
        y_tkn = lp_tkns[[*lp_tkns][1]]

        itkn = y_tkn
        itkn_nm = itkn.token_name 
            
        parent_lp = child_lp.factory.parent_lp
        parent_lp_tkns = parent_lp.factory.token_from_exchange[parent_lp.name]
                 
        parent_tkn = itkn.parent_tkn
        parent_lp = child_lp.factory.parent_lp
        
        SwapIndexMint(iVault).apply(parent_lp, parent_tkn, user_nm, parent_tkn_amt)
        mint_itkn_deposit = iVault.index_tokens[itkn_nm]['last_lp_deposit']
        mint_itkn_deposit = child_lp.convert_to_human(mint_itkn_deposit)
        opposite_tkn = x_tkn.token_name != parent_tkn.token_name
        tkn_amount1 = LPQuote(opposite_tkn).get_amount_from_lp(parent_lp, parent_tkn, mint_itkn_deposit) 
        price_itkn = tkn_amount1/mint_itkn_deposit 
        #AddLiquidity(price_itkn).apply(child_lp, y_tkn, user_nm, mint_itkn_deposit)  
        
        return AddLiquidity(price_itkn).apply(child_lp, y_tkn, user_nm, mint_itkn_deposit)    

    def _synthetic(self, child_lp, user_nm, iVault, parent_tkn_amt, lwr_tick, upr_tick):  
        
        lp_tkns = child_lp.factory.token_from_exchange[child_lp.name]
        x_tkn = lp_tkns[[*lp_tkns][0]]
        y_tkn = lp_tkns[[*lp_tkns][1]]
        
        itkn_nm = list(iVault.index_tokens.keys())[0]
        itkn = lp_tkns[itkn_nm]
        
        parent_tkn = itkn.parent_tkn
        parent_lp = child_lp.factory.parent_lp
        
        SwapIndexMint(iVault).apply(parent_lp, parent_tkn, user_nm, parent_tkn_amt)
        mint_itkn_deposit = iVault.index_tokens[itkn_nm]['last_lp_deposit']
        mint_itkn_deposit = child_lp.convert_to_human(mint_itkn_deposit)
        tkn_amount1 = LPQuote(False).get_amount_from_lp(parent_lp, parent_tkn, mint_itkn_deposit) 
        
        itkn1_deposit = 0.5*mint_itkn_deposit
        itkn2_deposit = 0.5*mint_itkn_deposit
        
        return child_lp.add_liquidity(user_nm, itkn1_deposit, itkn2_deposit, itkn1_deposit, itkn2_deposit)  
        
