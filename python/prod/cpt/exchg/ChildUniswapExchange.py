# Copyright [2023] [Ian Moore]
# Distributed under the MIT License (license terms are at http://opensource.org/licenses/MIT).
# Email: defipy.devs@gmail.com

from ...erc import ERC20
from ..exchg import UniswapExchange
from ..quote import LPQuote
from ...utils.data import UniswapExchangeData
from ...utils.data import FactoryData
import math

MINIMUM_LIQUIDITY = 1e-15

class ChildUniswapExchange(UniswapExchange):
    
    
    def __init__(self, factory_struct: FactoryData, exchg_struct: UniswapExchangeData) -> None:
        super().__init__(factory_struct, exchg_struct)
        self.hybrid_supply = 0
        self.hybrid_liquidity_providers = {}

        
    def info(self):
        print(f"Exchange {self.name} ({self.symbol})")
        print(f"Coins: {self.token0}/{self.token1}")
        print(f"Reserves: {self.token0} = {self.reserve0} | {self.token1} = {self.reserve1}")
        print(f"Liquidity: {self.total_supply}")  
        print(f"Hybrid Liquidity: {self.hybrid_supply} \n") 
        
    
    def remove_liquidity(self, to, liquidity, amount0_min, amount1_min):
        
        """ remove_liquidity

            Remove liquidity from both coins in the pair based on lp amount
                
            Parameters
            -------
            to : str
                receiving user address  
            liquidity : float
                lp amount to removed                 
            amount0_min : float
                Minimum amount of A  
            amount0_min : float
                Minimum amount of B 
                
            Returns
            -------
            amount0 : float
                removed liquidity from reserve0    
            amount1 : float
                removed liquidity from reserve1                    
        """         
        
        tokens = self.factory.token_from_exchange[self.name]
        assert tokens.get(self.token0) and tokens.get(self.token1), "Error"

        balance0 = tokens.get(self.token0).token_total
        balance1 = tokens.get(self.token1).token_total
        total_liquidity = self.liquidity_providers[to]
        if liquidity >= total_liquidity:
            liquidity = total_liquidity

        amount0 = liquidity * balance0 / self.total_supply      # using balances ensures pro-rata distribution
        amount1 = liquidity * balance1 / self.total_supply      # using balances ensures pro-rata distribution
    
        if not (round(amount0,5) >= round(amount0_min,5)):
            print('amount0 {} amount0_min {}'.format(round(amount0,5), round(amount0_min,5)))        
        
        assert amount0 > 0 and amount1 > 0, 'UniswapV2: INSUFFICIENT_LIQUIDITY_BURNED'
        assert round(amount0,5) >= round(amount0_min,5), 'UniswapV2Router: INSUFFICIENT_A_AMOUNT'
        assert round(amount1,5) >= round(amount1_min,5), 'UniswapV2Router: INSUFFICIENT_B_AMOUNT'
        
        ibalance0, ibalance1 = self._get_iamounts(balance0, balance1)
        iamount0, iamount1 = self._get_iamounts(amount0, amount1)
        
        hybrid_liquidity = min(self.hybrid_supply*iamount0/ibalance0,
                                self.hybrid_supply*iamount1/ibalance1)
        
        self._burn_hybrid(to, hybrid_liquidity)
        self.burn(to, liquidity, amount0, amount1)
        return amount0, amount1    
    
    def mint(self, to, _amount0, _amount1):
        
        """ mint

            Mint new liquidity based on amounts on each coin in the pair
                
            Parameters
            -------
            to : str
                receiving user address      
            _amount0 : float
                desired amount of A      
            _amount1 : float
                desired amount of B                   
        """          
        
        tokens = self.factory.token_from_exchange[self.name]
        assert tokens.get(self.token0) and tokens.get(self.token1), "Error"

        balance0 = tokens.get(self.token0).token_total
        balance1 = tokens.get(self.token1).token_total

        amount0 = balance0 - self.reserve0
        amount1 = balance1 - self.reserve1
        
        assert round(amount0,3) == round(_amount0,3)
        assert round(amount1,3) == round(_amount1,3)
    
        liquidity = self._calc_liquidity(amount0, amount1, 'standard')
        hybrid_liquidity = self._calc_liquidity(amount0, amount1, 'hybrid')

        assert liquidity > 0, 'UniswapV2: INSUFFICIENT_LIQUIDITY_MINTED'
        
        self._update(balance0, balance1)
        self._mint(to, liquidity)  
        self._mint_hybrid(to, hybrid_liquidity)
        
    def _calc_liquidity(self, amount0, amount1, liq_type):

        # keeping track of the liquidity providers
        if(liq_type == 'standard'):
            res0 = self.reserve0
            res1 = self.reserve1
            tot_supply = self.total_supply 
        elif(liq_type == 'hybrid'):
            res0, res1 = self._get_iamounts(self.reserve0, self.reserve1)    
            amount0, amount1 = self._get_iamounts(amount0, amount1)   
            tot_supply = self.hybrid_supply
        
        if tot_supply != 0:
            liquidity = min(
                amount0 * tot_supply / res0,
                amount1 * tot_supply / res1
            )
        else:
            liquidity = math.sqrt(amount0 * amount1) - MINIMUM_LIQUIDITY
            if(liq_type == 'standard'):
                self._mint("0", MINIMUM_LIQUIDITY)
            elif(liq_type == 'hybrid'):    
                self._mint_hybrid("0", MINIMUM_LIQUIDITY)                
                
        return liquidity  
    
    def _get_iamounts(self, amt0, amt1):

        tokens = self.factory.token_from_exchange[self.name]
        parent_lp = self.factory.parent_lp
        x_tkn = tokens.get(self.token0) 
        y_tkn = tokens.get(self.token1)

        if(x_tkn.type == 'index'):
            iamt0 = amt0
        else:    
            iamt0 = LPQuote().get_lp_from_amount(parent_lp, x_tkn, amt0)

        if(y_tkn.type == 'index'):
            iamt1 = amt1
        else:    
            iamt1 = LPQuote().get_lp_from_amount(parent_lp, y_tkn, amt1)

        return iamt0, iamt1  
        
    def _mint_hybrid(self, to, value):
        
        """ _mint_hybrid

            Update reserve amounts for both coins in the pair
                
            Parameters
            -------   
            to : str
                receiving user address       
            value : float
                amount of new liquidity                  
        """          
        
        if self.hybrid_liquidity_providers.get(to):
            self.hybrid_liquidity_providers[to] += value
        else:
            self.hybrid_liquidity_providers[to] = value

        self.hybrid_supply += value           
                   
    def _burn_hybrid(self, to, value):
        
        """ _burn

            Burn liquidity from both coins in the pair based on lp amount
                
            Parameters
            -------
            to : str
               receiving user address  
            value : float
                amount of liquidity to be burned                           
        """            
        
        available_liquidity = self.hybrid_liquidity_providers.get(to)
        self.hybrid_liquidity_providers[to] = available_liquidity - value
        self.hybrid_supply -= value          