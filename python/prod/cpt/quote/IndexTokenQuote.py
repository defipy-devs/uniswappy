# Copyright [2023] [Ian Moore]
# Distributed under the MIT License (license terms are at http://opensource.org/licenses/MIT).
# Email: defipy.devs@gmail.com

from .LPQuote import LPQuote

class IndexTokenQuote():
    
    """ 
        Index token quotes
        
        Parameters
        -----------------
        quote_native_tokens : boolean
            Quote LP amount of base pool, otherwise quote indexed pool      
    """        
    
    def __init__(self, lwr_tick = None, upr_tick = None, quote_native_tokens = True):
        self.quote_native_tokens = quote_native_tokens    
        self.lwr_tick = lwr_tick
        self.upr_tick = upr_tick        

    def get_x(self, lp, amt_lp): 
        
        """ get_x

            Given an amount of LP holdings, get x reserve of CPT pair (ie, xy = k)
                
            Parameters
            -----------------
            lp : UniswapExchange
                Uniswap LP    
            amt_lp : float
                Amount of LP holdings                   

            Returns
            -----------------
            reserve: float
                Amount of x reserve from CPT pair     
        """          
        
        tkn_x = lp.factory.token_from_exchange[lp.name][lp.token0]  
        if(tkn_x.type == 'standard'):
            x_amt = LPQuote(False).get_amount_from_lp(lp, tkn_x, amt_lp, self.lwr_tick, self.upr_tick)
        else: 
            parent_x_tkn = tkn_x.parent_tkn
            parent_lp = self.get_base_lp(lp, tkn_x)
            itkn_lp = LPQuote(False).get_amount_from_lp(lp, tkn_x, amt_lp)
            x_amt = LPQuote(False).get_amount_from_lp(parent_lp, parent_x_tkn, itkn_lp, self.lwr_tick, self.upr_tick)        
        return self.get_native_x(lp, tkn_x, x_amt) if self.quote_native_tokens else x_amt           
        
    def get_y(self, lp, amt_lp): 
        
        """ get_y

            Given an amount of LP holdings, get y reserve of CPT pair (ie, x*y = k)
                
            Parameters
            -----------------
            lp : UniswapExchange
                Uniswap liquidity pool (LP) exchange    
            amt_lp : float
                Amount of LP holdings                   

            Returns
            -----------------
            reserve: float
                Amount of y reserve from CPT pair     
        """        
    
        tkn_y = lp.factory.token_from_exchange[lp.name][lp.token1]  
        if(tkn_y.type == 'standard'):
            y_amt = LPQuote(False).get_amount_from_lp(lp, tkn_y, amt_lp, self.lwr_tick, self.upr_tick)
        else:           
            parent_y_tkn = tkn_y.parent_tkn
            parent_lp = self.get_base_lp(lp, tkn_y)
            itkn_lp = LPQuote(False).get_amount_from_lp(lp, tkn_y, amt_lp, self.lwr_tick, self.upr_tick)
            y_amt = LPQuote(False).get_amount_from_lp(parent_lp, parent_y_tkn, itkn_lp, self.lwr_tick, self.upr_tick)        

        return self.get_native_y(lp, tkn_y, y_amt) if self.quote_native_tokens else y_amt     
   
    def base_x_asset(self, lp):
        
        """ base_x_asset

            Get x base asset in x*y CPT pairing
                
            Parameters
            -----------------
            lp : UniswapExchange
                Uniswap liquidity pool (LP) exchange   
               
            Returns
            -----------------
            token: ERC20
                x base asset from CPT pair    
        """          
        
        tkn_x = lp.factory.token_from_exchange[lp.name][lp.token0]
        if(tkn_x.type == 'index'):
            tkn = tkn_x.parent_tkn
        else:
            tkn = tkn_x

        return tkn    

    def base_y_asset(self, lp):
        
        """ base_y_asset

            Get y base asset in x*y CPT pairing
                
            Parameters
            -----------------
            lp : UniswapExchange
                Uniswap liquidity pool (LP) exchange   
               
            Returns
            -----------------
            token: ERC20
                y base asset from CPT pair     
        """                  
        
        tkn_y = lp.factory.token_from_exchange[lp.name][lp.token1]
        if(tkn_y.type == 'index'):
            tkn = tkn_y.parent_tkn
        else:
            tkn = tkn_y

        return tkn   

    def get_native_x(self, lp, tkn_x, x_amt):
        
        """ get_native_x

            Get x base asset amount in x*y CPT pairing
                
            Parameters
            -----------------
            lp : UniswapExchange
                Uniswap liquidity pool (LP) exchange   
            tkn_x : ERC20
                ERC20 x token in x*y CPT pairing   
            x_amt : float
                Amount of x token                    
                
            Returns
            -----------------
            reserve: float
                Amount of x reserve from CPT pair     
        """            
        
        parent_lp = self.get_base_lp(lp, tkn_x)
        parent_lp_x_tkn = parent_lp.factory.token_from_exchange[parent_lp.name][parent_lp.token0]
        parent_x_tkn = tkn_x.parent_tkn if tkn_x.type == 'index' else tkn_x

        if(parent_x_tkn.token_name != parent_lp_x_tkn.token_name):
            x_amt = LPQuote().get_amount(parent_lp, parent_x_tkn, x_amt, self.lwr_tick, self.upr_tick) 

        return x_amt

    def get_native_y(self, lp, tkn_y, y_amt):
        
        """ get_native_y

            Get y base asset amount in x*y CPT pairing
                
            Parameters
            -----------------
            lp : UniswapExchange
                Uniswap liquidity pool (LP) exchange   
            tkn_y : ERC20
                ERC20 y token in x*y CPT pairing   
            y_amt : float
                Amount of x token                        
                
            Returns
            -----------------
            reserve: float
                Amount of y reserve from CPT pair     
        """           
        
        parent_lp = self.get_base_lp(lp, tkn_y)
        parent_lp_y_tkn = parent_lp.factory.token_from_exchange[parent_lp.name][parent_lp.token1]
        parent_y_tkn = tkn_y.parent_tkn if tkn_y.type == 'index' else tkn_y

        if(parent_y_tkn.token_name != parent_lp_y_tkn.token_name):
            y_amt = LPQuote().get_amount(parent_lp, parent_y_tkn, y_amt, self.lwr_tick, self.upr_tick) 

        return y_amt
    
    
    def get_base_lp(self, lp, tkn):
        
        """ get_base_lp

            Return the parent LP, given a child LP and one of its reserve tokens, 
                
            Parameters
            -----------------
            lp : UniswapExchange
                Child Uniswap liquidity pool (LP) exchange   
            tkn : ERC20
                Child ERC20 token in x*y CPT pairing                           
                
            Returns
            -----------------
            lp: UniswapExchange
                Parent liquidity pool (LP) exchange  
        """         
        
        if(tkn.type == 'index'):
            base_lp = tkn.parent_lp
        else:
            base_lp = lp.factory.parent_lp
        return lp if base_lp == None else base_lp          
        
        