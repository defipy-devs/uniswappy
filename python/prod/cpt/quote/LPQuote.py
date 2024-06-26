# Copyright [2023] [Ian Moore]
# Distributed under the MIT License (license terms are at http://opensource.org/licenses/MIT).
# Email: defipy.devs@gmail.com

from ..index import RebaseIndexToken
from ..index import SettlementLPToken
from ...utils.data import UniswapExchangeData
from ...utils.tools.v3 import UniV3Helper

class LPQuote():
    
    """ 
        Liquidity pool token quotes (ie, price, reserve and liquidity)
        
        Parameters
        -----------------
        quote_opposing : boolean
            Quote the opposing token amount by default, given LP and a token    
    """      
    
    def __init__(self, quote_opposing = True, include_fee = False):
        self.quote_opposing = quote_opposing
        self.include_fee = include_fee
        self.price_tkn = True
        
    def get_opposing_token(self, lp, tkn):
        
        """ get_x

            Get opposing token given LP exchange and one of its token assetes
                
            Parameters
            -----------------
            lp : UniswapExchange
                Uniswap LP    
            tkn: ERC20
                Token asset from CPT pair                  

            Returns
            -----------------
            tkn: ERC20
                Opposing token from CPT pair      
        """             
        
        opposing_tkn_nm = lp.token1 if(tkn.token_name == lp.token0) else lp.token0
        return lp.factory.token_from_exchange[lp.name][opposing_tkn_nm]

    def get_reserve(self, lp, token, lwr_tick = None, upr_tick = None):  
        
        """ get_reserve

            Get reserve amount of token given LP exchange 
                
            Parameters
            -----------------
            lp : UniswapExchange
                Uniswap LP    
            token: ERC20
                Token asset from CPT pair                  

            Returns
            -----------------
            reserve: float
                Reserve amount from token asset     
        """             
        if(lp.version == UniswapExchangeData.VERSION_V2):
            if(token.token_name == lp.token0):        
                reserve_out = lp.reserve0 
            elif(token.token_name == lp.token1):
                reserve_out = lp.reserve1   

            if token.type == 'index':
                self.quote_opposing = False
                parent_lp = token.parent_lp
                parent_token = token.parent_tkn
                reserve_out = self.get_amount_from_lp(parent_lp, parent_token, reserve_out)  
        
        elif(lp.version == UniswapExchangeData.VERSION_V3):

            if(lp.total_supply == 0):
                reserve_out = 0
            else:    
                reserve_out = lp.get_virtual_reserve(token) 
                if token.type == 'index':
                    self.quote_opposing = False
                    parent_lp = token.parent_lp
                    parent_token = token.parent_tkn
                    parent_lp_tkn_x = parent_lp.factory.token_from_exchange[parent_lp.name][parent_lp.token0]
                    p = parent_lp.get_price(parent_lp_tkn_x)
                    lwr_tick = UniV3Helper().get_price_tick(parent_lp, -1, p, 1000)
                    upr_tick = UniV3Helper().get_price_tick(parent_lp, 1, p, 1000)
                    reserve_out = self.get_amount_from_lp(parent_lp, parent_token, reserve_out, lwr_tick, upr_tick)         
                    
        return reserve_out

    def get_price(self, lp, tkn, lwr_tick = None, upr_tick = None):  
        
        """ get_price

            Get price of token given LP exchange 
                
            Parameters
            -----------------
            lp : UniswapExchange
                Uniswap LP    
            tkn: ERC20
                Token asset from CPT pair                  

            Returns
            -----------------
            price: float
                Token price with respect to opposing token    
        """           
           
        opposing_tkn = self.get_opposing_token(lp, tkn)

        if(tkn.token_name == lp.token0):
            reserve0 = self.get_reserve(lp, tkn, lwr_tick, upr_tick)
            reserve1 = self.get_reserve(lp, opposing_tkn, lwr_tick, upr_tick)
            if(reserve0 == 0):
                return 0 
            else:
                return reserve1/reserve0 if self.price_tkn else lp.get_price(tkn)
        elif(tkn.token_name == lp.token1):    
            reserve1 = self.get_reserve(lp, tkn, lwr_tick, upr_tick)
            reserve0 = self.get_reserve(lp, opposing_tkn, lwr_tick, upr_tick)        
            if(reserve1 == 0):
                return 0
            else:
                return reserve0/reserve1 if self.price_tkn else lp.get_price(tkn)
        else:
            print('ERROR: wrong input token')              
        
    def get_liquidity(self, lp, tkn, amount_in): 
        
        """ get_liquidity

            Get liquidity amount given amount of one of the tokens in x*y CPT pair 
                
            Parameters
            -----------------
            lp : UniswapExchange
                Uniswap LP    
            tkn: ERC20
                Token asset from CPT pair   
            amount_in: float
                Amount of liquidity               

            Returns
            -----------------
            amt_out: float
                Liquidity amount given amount of one of the tokens in x*y CPT pair   
        """           
        
        if(tkn.token_name == lp.token0):
            amt_out = (amount_in * lp.total_supply)/lp.reserve0 
        else:
            amt_out = (amount_in * lp.total_supply)/lp.reserve1 

        return amt_out         
        
        
    def get_amount(self, lp, tkn, amount_in, lwr_tick = None, upr_tick = None):
        
        """ get_amount

            Get amount of reserve for opposing token, given an amount of reserve of input token
                
            Parameters
            -----------------
            lp : UniswapExchange
                Uniswap LP    
            tkn: ERC20
                Token asset from CPT pair   
            amount_in: float
                Amount of reserve token               

            Returns
            -----------------
            amt_out: float
                Amount of reserve for opposing token 
        """       

        if (amount_in == 0):
            return 0

        if(lp.version == UniswapExchangeData.VERSION_V2):

            if(self.include_fee):
                if(tkn.token_name == lp.token0):
                    amt_out = lp.get_amount_out0(amount_in)
                else:
                    amt_out = lp.get_amount_out1(amount_in)
            else:
                if(tkn.token_name == lp.token0):
                    amt_out = (amount_in * lp.reserve1) / lp.reserve0
                else:
                    amt_out = (amount_in * lp.reserve0) / lp.reserve1

        elif(lp.version == UniswapExchangeData.VERSION_V3): 
            quote_out = UniV3Helper().quote(lp, tkn, amount_in, lwr_tick, upr_tick)
            amt_out = quote_out[0]
    
        return amt_out if self.quote_opposing else amount_in 
    
    def get_amount_from_lp(self, lp, tkn, amount_lp_in, lwr_tick = None, upr_tick = None):
        
        """ get_amount_from_lp

            Get amount of opposing token, given an amount priced in liquidity
                
            Parameters
            -----------------
            lp : UniswapExchange
                Uniswap LP    
            tkn: ERC20
                Token asset from CPT pair   
            amount_lp_in: float
                Amount of liquidity               

            Returns
            -----------------
            amt_out: float
                Amount of opposing token 
        """           
        
        if(amount_lp_in > 0):
            itkn_amt = RebaseIndexToken().apply(lp, tkn, amount_lp_in, lwr_tick, upr_tick)
            amt_out = self.get_amount(lp, tkn, itkn_amt, lwr_tick, upr_tick) if self.quote_opposing else itkn_amt
        else:
            amt_out = 0
        return amt_out   
    
    
    def get_lp_from_amount(self, lp, tkn, amount_in, lwr_tick = None, upr_tick = None):
        
        """ get_lp_from_amount

            Get amount of liquidity, given an amount reserve token
                
            Parameters
            -----------------
            lp : UniswapExchange
                Uniswap LP    
            tkn: ERC20
                Token asset from CPT pair   
            amount_lp_in: float
                Amount of reserve token               

            Returns
            -----------------
            amt_out: float
                Amount of liquidity 
        """         
        
        if(amount_in > 0):
            lp_amt = SettlementLPToken().apply(lp, tkn, amount_in, lwr_tick, upr_tick)
        else:
            lp_amt = 0
        return lp_amt   
         