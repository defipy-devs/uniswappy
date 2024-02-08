# Factory.py
# Author: Ian Moore ( utiliwire@gmail.com )
# Date: May 2023

from ..exchg import UniswapExchange 
from ...erc import ERC20
from ...erc import LPERC20
from ...utils.interfaces import IExchangeFactory 
from ...utils.data import UniswapExchangeData
from ...utils.data import FactoryData


class UniswapFactory(IExchangeFactory):

    """ 
        Create liquidity pools for given token pairs.
        
        Parameters
        ----------
        self.name : str
            Token name 
        self.address : str
            Token 0 name  
        self.exchange_from_token : dictionary
            Map of tokens to exchanges
        self.tokens_from_exchange : dictionary
            Map of exchanges to pair tokens          
    """     
    
    def __init__(self, name: str, address: str) -> None:
        self.name = name
        self.address = address
        self.exchange_from_token = {}
        self.token_from_exchange = {}
        self.parent_lp = None

    def deploy(self, exchg_data : UniswapExchangeData):
        
        """ create_exchange

            Create liquidity pool (LP) exchange
                
            Parameters
            -------
            exchg_data : UniswapExchangeInit
                Exchange initialization data     

            Returns
            -------
            exchange : UniswapExchange
                Newly created exchange that is also a LP token                    
        """  
        
        token0 = exchg_data.tkn0
        token1 = exchg_data.tkn1
        symbol = exchg_data.symbol
        address = exchg_data.address
        
        
        assert f"{token0.token_name}/{token1.token_name}" not in self.token_from_exchange, 'UniswapV2Factory: EXCHANGE_CREATED'
            
        self.parent_lp = token0.parent_lp if token0.type == 'index' else self.parent_lp
        self.parent_lp = token1.parent_lp if token1.type == 'index' else self.parent_lp 
        
        factory_struct = FactoryData(self.token_from_exchange,  self.parent_lp, self.name, self.address)
        exchg_struct = UniswapExchangeData(tkn0 = token0, tkn1 = token1, symbol=symbol, address=address)
        exchange = UniswapExchange(factory_struct, exchg_struct)       
        
        self.exchange_from_token[token0.token_name] = exchange
        self.token_from_exchange[exchange.name] = {token0.token_name: token0, token1.token_name: token1}
        
        return exchange

    def get_exchange(self, token):
        
        """ get_exchange

            Get exchange from given pair token
                
            Parameters
            -------
            token : ERC20
                receiving user address      
                
            Returns
            -------
            exchange : UniswapExchange
                exchange from mapped token                    
        """         
        
        return self.token_from_exchange.get(token)

    def get_token(self, exchange):
        
        """ get_token

            Get token from exchange
                
            Parameters
            -------
            exchange : UniswapExchange
                receiving user address      
                
            Returns
            -------
            token : ERC20 
                token from mapped exchange                     
        """          
        
        return self.token_from_exchange.get(exchange)