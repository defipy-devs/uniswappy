# Copyright [2023] [Ian Moore]
# Distributed under the MIT License (license terms are at http://opensource.org/licenses/MIT).
# Email: defipy.devs@gmail.com

import math
from scipy import optimize
from ..Process import Process
from ..liquidity import AddLiquidity
from ..swap import Swap
from ...math.model import TokenDeltaModel
from ...math.model import EventSelectionModel
from ...utils.data import UniswapExchangeData
from ...utils.tools.v3 import UniV3Helper
from ...utils.tools.v3 import TickMath

class SwapDeposit(Process):
    
    """ Process to swap approx. half of single token X for token Y (and vice verse) and deposit proceeds
        plus remaining other approximated half

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
            
    def apply(self, lp, token_in, user_nm, amount_in, lwr_tick = None, upr_tick = None):   
        
        """ apply

            Swap approx. half of single token X for token Y (and vice verse) and deposit proceeds
            plus remaining other approximated half
                
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
            (amount_in, amount_out) : float, float
                token swap amounts                
        """          
        
        amount_in = tDel.delta() if amount_in == None else amount_in    
        trading_token = self.get_trading_token(lp, token_in)

        # Step 2: deposit   
        if(lp.version == UniswapExchangeData.VERSION_V2):

            # Step 1: swap 
            p_in = self._calc_univ2_deposit_portion(lp, token_in, amount_in)
            amount_out = Swap().apply(lp, token_in, user_nm, p_in*amount_in)

            # Step 2: deposit   
            if(token_in.token_name == lp.token1):
                balance0 = amount_out 
                balance1 = lp.quote(balance0, lp.reserve0, lp.reserve1)
                deposited = balance1 + p_in*amount_in
            elif(token_in.token_name == lp.token0):
                balance1 = amount_out
                balance0 = lp.quote(balance1, lp.reserve1, lp.reserve0)
                deposited = balance0 + p_in*amount_in
            lp.add_liquidity(user_nm, balance0, balance1, balance0, balance1) 
            
        elif(lp.version == UniswapExchangeData.VERSION_V3):  

            # Step 1: swap 
            p_in = self._calc_univ3_deposit_portion(lp, token_in, amount_in, lwr_tick, upr_tick)
            amount_out = Swap().apply(lp, token_in, user_nm, p_in*amount_in)
            
            sqrt_P = lp.slot0.sqrtPriceX96/2**96
            tokens = lp.factory.token_from_exchange[lp.name] 

            # Step 2: deposit 
            if(token_in.token_name == lp.token0):
                balance1 = abs(amount_out) 
                liq = UniV3Helper().calc_Ly(sqrt_P, balance1, lwr_tick, upr_tick)
                deposited = liq/sqrt_P + p_in*amount_in
                                
            elif(token_in.token_name == lp.token1): 
                balance0 = abs(amount_out) 
                liq = UniV3Helper().calc_Lx(sqrt_P, balance0, lwr_tick, upr_tick)
                deposited = liq*sqrt_P + p_in*amount_in
                
            lp.mint(user_nm, lwr_tick, upr_tick, liq)  
                            
        return deposited  

    def get_trading_token(self, lp, token):
        
        """ get_trading_token

            Get opposing token from specified token
                
            Parameters
            -------
            lp : Exchange
                LP exchange
            token : ERC20
                specified ERC20 token      
                
            Returns
            -------
            trading_token : ERC20 
                opposing ERC20 token                   
        """         
        
        tokens = lp.factory.token_from_exchange[lp.name]
        trading_token = tokens[lp.token1] if token.token_name == lp.token0 else tokens[lp.token0]
        return trading_token       


    def _calc_univ3_deposit_portion(self, lp, tkn, amt_tkn_in, lwr_tick, upr_tick):
        bnds = [(0.35, 0.65)]
        opt_tol = 1e-8
        res = optimize.minimize(self._obj_func, x0 = 0.5, bounds=bnds, 
                                args=(amt_tkn_in, lp, tkn, lwr_tick, upr_tick), 
                                method='Nelder-Mead', tol=opt_tol)
        return res.x[0]
    
    def _obj_func(self, alpha, amt_tkn_in, lp, token_in, lwr_tick, upr_tick):
        opt_tol = 1e-8         
        swap_in = amt_tkn_in*alpha
        amt_tkn0, sqrtp_cur  = UniV3Helper().quote(lp, token_in, swap_in, lwr_tick, upr_tick)
        sqrtp_pa = TickMath.getSqrtRatioAtTick(lwr_tick)/2**96
        sqrtp_pb = TickMath.getSqrtRatioAtTick(upr_tick)/2**96    
        
        if(token_in.token_name == lp.token0):
            sqrtp_cur = 1/sqrtp_cur
            
        dPy = (sqrtp_cur - sqrtp_pa)
        dPx = (1/sqrtp_cur - 1/sqrtp_pb) 
        
        if(token_in.token_name == lp.token0):
            dL = amt_tkn0/dPy 
            amt_deposit = dL*dPx
        elif(token_in.token_name == lp.token1): 
            dL = amt_tkn0/dPx 
            amt_deposit = dL*dPy
        
        diff = amt_tkn_in - (swap_in + amt_deposit) 
        return abs(diff)+opt_tol
    
    def _calc_univ2_deposit_portion(self, lp, token_in, dx):

        tkn_supply = self._get_tkn_supply(lp, token_in)
        a = 997*(dx**2)/(1000*tkn_supply)
        b = dx*(1997/1000)
        c = -dx

        alpha = -(b - math.sqrt(b*b - 4*a*c)) / (2*a)
        return alpha 

    def _get_tkn_supply(self, lp, token_in):
        tokens = lp.factory.token_from_exchange[lp.name]
        if(lp.version == UniswapExchangeData.VERSION_V2):
            if(token_in.token_name == lp.token0):
                tkn_supply = lp.get_reserve(tokens[lp.token0])
            else:    
                tkn_supply = lp.get_reserve(tokens[lp.token1])
        elif(lp.version == UniswapExchangeData.VERSION_V3):   
            if(token_in.token_name == lp.token0):
                tkn_supply = lp.get_reserve(tokens[lp.token0])
            else:    
                tkn_supply = lp.get_reserve(tokens[lp.token1])
        return tkn_supply        
        

