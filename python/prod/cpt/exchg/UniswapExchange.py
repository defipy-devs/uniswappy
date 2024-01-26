# Exchange.py
# Author: Ian Moore ( utiliwire@gmail.com )
# Date: May 2023

from ...erc import ERC20
from ...erc import LPERC20
import math

MINIMUM_LIQUIDITY = 1e-15

class UniswapExchange(LPERC20):
    
    """ 
        Exchanges is how uniswap calls the liquidity pools. Each exchange is associated with a single ERC20 
        token and hold a liquidity pool of ETH and the token.
        - The algorithm used is the constant product automated market maker
            - which works by maintaning the relationship token_1 * token_2 = liquidity
            - This liquidity is held constant during trades    

        Parameters
        ----------
        self.factory : Factory
            Token name 
        self.token0 : str
            Token 0 name  
        self.token1 : str
            Token 1 name 
        self.reserve0 : float
            Reserve for token 0            
        self.reserve1 : float
            Reserve for token 1              
        self.fee : float
            Transaction fee
        self.name : str
            Name of exchange   
        self.symbol : str
            Name of exchange symbol  
        self.total_supply : float
            Total supply in exchange             

        References
        ----------   
        - https://docs.uniswap.org/protocol/V1/guides/connect-to-uniswap#token-interface
        - https://github.com/rsarai/liquidity-pool/blob/main/lp.py
    """      
    
    
    def __init__(self, factory_struct: {}, token0_name: str, token1_name: str, 
                       name: str, symbol: str, addr : str) -> None:
        super().__init__(token0_name+token1_name, addr)
        self.factory = factory_struct
        self.token0 = token0_name       # addresses or names. Actual tokens get stored in another place
        self.token1 = token1_name       # addresses or names. Actual tokens get stored in another place
        self.reserve0 = 0               # single storage slot
        self.reserve1 = 0               # single storage slot
        self.fee0_arr = []
        self.fee1_arr = []
        self.aggr_fee0 = 0
        self.aggr_fee1 = 0
        self.collected_fee0 = 0
        self.collected_fee1 = 0              
        self.name = name
        self.symbol = symbol
        self.liquidity_providers = {}
        self.last_liquidity_deposit = 0
        self.total_supply = 0

    def info(self):
        print(f"Exchange {self.name} ({self.symbol})")
        print(f"Coins: {self.token0}/{self.token1}")
        print(f"Reserves: {self.token0} = {self.reserve0} | {self.token1} = {self.reserve1}")
        print(f"Liquidity: {self.total_supply} \n")

    def doc(self):
        print(f"Available features:\n- Add liquidity\n- Remove liquidity\n- Exchange tokens\n")

    def add_liquidity(self, _from, balance0, balance1, balance0Min, balance1Min):
        
        """ add_liquidity

            Add liquidity to both coins in the pair
                
            Parameters
            -------
            _from : str
                receiving user address      
            balance0 : float
                desired amount of A      
            balance1 : float
                desired amount of B   
            balance0Min : float
                Minimum amount of A  
            balance1Min : float
                Minimum amount of B                 
        """           
        
        tokens = self.factory.exchange_to_tokens[self.name]
        assert tokens.get(self.token0) and tokens.get(self.token1), "Error"
        amount0, amount1 = self._add_liquidity(balance0, balance1, balance0Min, balance1Min)

        tokens.get(self.token0).deposit(_from, amount0)
        tokens.get(self.token1).deposit(_from, amount1)

        self.mint(_from, amount0, amount1)
        return amount0, amount1

    def _add_liquidity(self, balance0, balance1, balance0Min, balance1Min):
        
        """ _add_liquidity

            In practice, Uniswap applies a 0.30% fee to trades, which is added to
            reserves. As a result, each trade actually increases k. This functions
            as a payout to liquidity providers, for simplicity I have removed fee
            related logic.
                
            Parameters
            -------    
            balance0 : float
                desired amount of A      
            balance1 : float
                desired amount of B   
            balance0Min : float
                Minimum amount of A  
            balance1Min : float
                Minimum amount of B 
                
            Returns
            -------
            amount0 : float
                removed liquidity from reserve0    
            amount1 : float
                removed liquidity from reserve1                   
        """            
        
        tokens = self.factory.exchange_to_tokens[self.name]
        assert tokens.get(self.token0) and tokens.get(self.token1), "Error"

        if self.reserve0 == 0 and self.reserve1 == 0:
            amount0 = balance0
            amount1 = balance1
        else:
            balance1Optimal = self.quote(balance0, self.reserve0, self.reserve1)
            if balance1Optimal <= balance1:                
                assert round(balance1Optimal,5) >= round(balance1Min,5), 'UniswapV2Router: INSUFFICIENT_B_AMOUNT'
                amount0 = balance0
                amount1 = balance1Optimal
            else:
                balance0Optimal = self.quote(balance1, self.reserve1, self.reserve0)
                assert round(balance0Optimal,5) <= round(balance0,5)
                assert round(balance0Optimal,5) >= round(balance0Min,5), 'UniswapV2Router: INSUFFICIENT_A_AMOUNT'
                amount0 = balance0Optimal
                amount1 = balance1

        return amount0, amount1

    def get_amounts(self, to, liquidity):
        
        """ get_amounts

            Remove liquidity from both coins in the pair based on lp amount
                
            Parameters
            -------
            to : str
                receiving user address  
            liquidity : float
                lp amount                  
                
            Returns
            -------
            amount0 : float
                liquidity portion of reserve0    
            amount1 : float
                liquidity portion of reserve1                    
        """         
        
        tokens = self.factory.exchange_to_tokens[self.name]
        assert tokens.get(self.token0) and tokens.get(self.token1), "Error"

        balance0 = tokens.get(self.token0).token_total
        balance1 = tokens.get(self.token1).token_total
        total_liquidity = self.liquidity_providers[to]
        if liquidity >= total_liquidity:
            liquidity = total_liquidity

        amount0 = liquidity * balance0 / self.total_supply      # using balances ensures pro-rata distribution
        amount1 = liquidity * balance1 / self.total_supply      # using balances ensures pro-rata distribution

        return amount0, amount1    
    
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
        
        tokens = self.factory.exchange_to_tokens[self.name]
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
        
        self.burn(to, liquidity, amount0, amount1)
        return amount0, amount1

    def swap_exact_tokens_for_tokens(self, amount0_in, amount1_out_min, token_in, to):
        
        """ swap_exact_tokens_for_tokens

            Swap amt of token for min opposing token out
                
            Parameters
            -------
            amount0_in : float
                swap amount in
            amount1_out_min : float
                min swap amount in                
            token_in : ERC20
                Token to be swapped
            to : str
               receiving user address  
                
            Returns
            -------
            amount1_out_expected : float
                amount expected from the swap                    
        """          
        
        amount1_out_expected = self.get_amount_out(amount0_in, token_in)
        assert amount1_out_expected >= amount1_out_min, 'UniswapV2Router: INSUFFICIENT_OUTPUT_AMOUNT'

        tokens = self.factory.exchange_to_tokens[self.name]
        if(token_in.token_name == self.token0):
            tokens.get(self.token0).deposit(to, amount0_in)
            self.swap(0, amount1_out_expected, to)
        elif(token_in.token_name == self.token1):
            tokens.get(self.token1).deposit(to, amount0_in)
            self.swap(amount1_out_expected, 0, to)
            
        return amount1_out_expected

    def burn(self, to, liquidity, amount0, amount1):
        
        """ burn

            Burn liquidity from both coins in the pair based on lp amount
                
            Parameters
            -------
            to : str
               receiving user address  
            liquidity : float
                amount of liquidity to be burned                  
            amount0 : float
                est. amount from reserve0 to be burned
            amount1 : float
                est. amount from reserve1 to be burned               
        """          
        
        self._burn(to, liquidity)

        tokens = self.factory.exchange_to_tokens[self.name]
        tokens.get(self.token0).transfer(to, amount0)
        tokens.get(self.token1).transfer(to, amount1)

        balance0 = tokens.get(self.token0).token_total
        balance1 = tokens.get(self.token1).token_total

        self._update(balance0, balance1)

    def _burn(self, to, value):
        
        """ _burn

            Burn liquidity from both coins in the pair based on lp amount
                
            Parameters
            -------
            to : str
               receiving user address  
            value : float
                amount of liquidity to be burned                           
        """            
        
        available_liquidity = self.liquidity_providers.get(to)
        self.liquidity_providers[to] = available_liquidity - value
        self.total_supply -= value

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
        
        tokens = self.factory.exchange_to_tokens[self.name]
        assert tokens.get(self.token0) and tokens.get(self.token1), "Error"

        balance0 = tokens.get(self.token0).token_total
        balance1 = tokens.get(self.token1).token_total

        amount0 = balance0 - self.reserve0
        amount1 = balance1 - self.reserve1
        
        assert round(amount0,3) == round(_amount0,3)
        assert round(amount1,3) == round(_amount1,3)

        # keeping track of the liquidity providers
        if self.total_supply != 0:
            liquidity = min(
                amount0 * self.total_supply / self.reserve0,
                amount1 * self.total_supply / self.reserve1
            )
        else:
            liquidity = math.sqrt(amount0 * amount1) - MINIMUM_LIQUIDITY
            self._mint("0", MINIMUM_LIQUIDITY)

        assert liquidity > 0, 'UniswapV2: INSUFFICIENT_LIQUIDITY_MINTED'
        
        self._update(balance0, balance1)
        self._mint(to, liquidity)

    def _update(self, balance0, balance1):
        
        """ _update

            Update reserve amounts for both coins in the pair
                
            Parameters
            -------   
            balance0 : float
                new reserve amount of A      
            balance1 : float
                new reserve amount of B                   
        """         
        
        self.reserve0 = balance0
        self.reserve1 = balance1

    def _mint(self, to, value):
        
        """ _mint

            Update reserve amounts for both coins in the pair
                
            Parameters
            -------   
            to : str
                receiving user address       
            value : float
                amount of new liquidity                  
        """          
        
        if self.liquidity_providers.get(to):
            self.liquidity_providers[to] += value
        else:
            self.liquidity_providers[to] = value

        self.last_liquidity_deposit = value     
        self.total_supply += value
        
    def _tally_fees(self, fee0, fee1):
        
        """ _tally_fees

            Tally fee from swap and record last collected fee
                
            Parameters
            -------   
            fee0 : float
                fee from reserve0      
            fee1 : float
                fee from reserve1                 
        """         
        self.fee0_arr.append(fee0)
        self.fee1_arr.append(fee1)
        self.collected_fee0 += fee0 
        self.collected_fee1 += fee1        
        self.aggr_fee0 += fee0 
        self.aggr_fee1 += fee1
        
    def swap(self, amount0_out, amount1_out, to):
        
        """ swap

            Remove liquidity from both coins in the pair based on lp amount
                
            Parameters
            -------
            amount0_out : float
                swap amount 0 out
            amount1_out : float
                swap amount 1 out               
            to : str
               receiving user address                   
        """         
        
        assert amount0_out > 0 or amount1_out > 0, 'UniswapV2: INSUFFICIENT_OUTPUT_AMOUNT'
        assert amount0_out < self.reserve0 and amount1_out < self.reserve1, 'UniswapV2: INSUFFICIENT_LIQUIDITY'

        tokens = self.factory.exchange_to_tokens[self.name]
        assert tokens.get(self.token0).token_addr != to, 'UniswapV2: INVALID_TO'
        assert tokens.get(self.token1).token_addr != to, 'UniswapV2: INVALID_TO'

        tokens.get(self.token0).transfer(to, amount0_out)
        tokens.get(self.token1).transfer(to, amount1_out)    
        
        balance0 = tokens.get(self.token0).token_total
        balance1 = tokens.get(self.token1).token_total

        amount0_in = balance0 - (self.reserve0 - amount0_out) if balance0 > self.reserve0 - amount0_out else 0
        amount1_in = balance1 - (self.reserve1 - amount1_out) if balance1 > self.reserve1 - amount1_out else 0
        assert amount0_in > 0 or amount1_in > 0, 'UniswapV2: INSUFFICIENT_INPUT_AMOUNT'

        balance0_adjusted = balance0 * 1000 - amount0_in * 3  # trading fee
        balance1_adjusted = balance1 * 1000 - amount1_in * 3  # trading fee
 
        adj_digits = max(len(str(balance0_adjusted * balance1_adjusted))-11, 1)
        lside = round(math.ceil(balance0_adjusted * balance1_adjusted), -adj_digits)
        rside = round(math.ceil(self.reserve0 * self.reserve1 * 1000**2), -adj_digits)

        # ******** FIX ********
        #assert  lside  ==  rside , 'UniswapV2: K'
    
        self._update(balance0, balance1)
        self._tally_fees(amount0_in * 3 / 1000, amount1_in * 3 / 1000)           
 
    def quote(self, amount0, reserve0, reserve1):
        
        """ quote

            Given some amount of an asset and pair reserves, returns an equivalent amount of
            the other asset
                
            Parameters
            -------
            amount0 : float
                amount of a given asset token
            reserve0 : float
                total amount of asset A in LP              
            reserve1 : float
                total amount of asset B in LP                    
        """          
        
        assert amount0 > 0, 'UniswapV2Library: INSUFFICIENT_AMOUNT'
        assert reserve0 > 0 and reserve1 > 0, 'UniswapV2Library: INSUFFICIENT_LIQUIDITY'
        return (amount0 * reserve1) / reserve0;        

    def get_amount_out(self, amount_in, token_in):

        """ get_amount_out

            Get amount of
                
            Parameters
            -------
            amount_in : float
                input amount of an asset
            token_in : ERC20
                asset token  
                          
            Returns
            -------
            amount out : float
                amount of opposing asset                       
        """         
        
        if(token_in.token_name == self.token0):    
            return self.get_amount_out0(amount_in) 
        elif(token_in.token_name == self.token1):
            return self.get_amount_out1(amount_in) 
        else:
            return -1    
    
    def get_amount_out0(self, amount_in):
        
        """ get_amount_out0

            Given an input amount of an asset and pair reserves, returns the maximum output amount of the
            other asset
                
            Parameters
            -------
            amount_in : float
                input amount of an asset
                          
            Returns
            -------
            amount_out out : float
                (reserve0 + amount_in_with_fee) * (reserve1 - amount_out) = reserve1 * reserve0       
        """
        
        assert amount_in > 0, 'UniswapV2Library: INSUFFICIENT_INPUT_AMOUNT'
        assert self.reserve0 > 0 and self.reserve1 > 0, 'UniswapV2Library: INSUFFICIENT_LIQUIDITY'

        #amount_in_with_fee = amount_in * 1000              # disconsidering the fee here: amount_in * 997
        amount_in_with_fee = amount_in * 997              # disconsidering the fee here: amount_in * 997
        numerator = amount_in_with_fee * self.reserve1
        denominator = self.reserve0 * 1000 + amount_in_with_fee
        amount_out = numerator / denominator

        return amount_out
    
    def get_amount_out1(self, amount_in):
        
        """ get_amount_out1

            Given an input amount of an asset and pair reserves, returns the maximum output amount of the
            other asset
                
            Parameters
            -------
            amount_in : float
                input amount of an asset
                          
            Returns
            -------
            amount_out out : float
                (reserve0 + amount_in_with_fee) * (reserve1 - amount_out) = reserve1 * reserve0       
        """        
        
        assert amount_in > 0, 'UniswapV2Library: INSUFFICIENT_INPUT_AMOUNT'
        assert self.reserve0 > 0 and self.reserve1 > 0, 'UniswapV2Library: INSUFFICIENT_LIQUIDITY'

        #amount_in_with_fee = amount_in * 1000              # disconsidering the fee here: amount_in * 997
        amount_in_with_fee = amount_in * 997              # disconsidering the fee here: amount_in * 997
        numerator = amount_in_with_fee * self.reserve0
        denominator = self.reserve1 * 1000 + amount_in_with_fee
        amount_out = numerator / denominator

        return amount_out 

    def update_reserves(self, user_nm, amount0_update = None, amount1_update = None):
        
        """ update_reserves

            Update reserve assets of either or both assets in the pair
                
            Parameters
            -------
            user_nm : str
                acccount holder
            amount0_update : float
                update amount of asset A             
            amount1_update : float
                update amount of asset B      
        """          
        
        amount0_update = amount0_update if amount0_update != None else self.reserve0
        amount1_update = amount1_update if amount1_update != None else self.reserve1
        self.burn(user_nm, self.liquidity_providers[user_nm], self.reserve0, self.reserve1)
        tokens = self.factory.exchange_to_tokens[self.name]
        tokens.get(self.token0).deposit(user_nm, amount0_update)
        tokens.get(self.token1).deposit(user_nm, amount1_update)
        self.mint(user_nm, amount0_update, amount1_update)      
    

    def simulate_transaction(self, amount_t0, token_in):

        
        """ simulate_transaction

            Estimate opposing token return given a predetermined amount of exchange token
                
            Parameters
            -------
            amount_t0 : float
                amount of token
            token_in : ERC20
                exchange token                
        """          
        
        result = self.get_amount_out(amount_t0, token_in)
        if(token_in.token_name == self.token0):
            print(f"{amount_t0} {self.token0} receive {round(result, 2)} {self.token1}")
        elif(token_in.token_name == self.token1):
            print(f"{amount_t0} {self.token1} receive {round(result, 2)} {self.token0}")
        else:
            print('ERROR: wrong input token')
            
                    
    def get_price(self, token):  
        
        """ get_price

            Get price of select token in the exchange pair
                
            Parameters
            -------
            token : ERC20
                ERC20 token                
        """          
        
        if(token.token_name == self.token0):
            if(self.reserve0 == 0):
                return None 
            else:
                return self.reserve1/self.reserve0 
        elif(token.token_name == self.token1):
            if(self.reserve1 == 0):
                return None
            else:
                return self.reserve0/self.reserve1
        else:
            print('ERROR: wrong input token')        
            
    def get_reserve(self, token):  
        
        """ get_reserve

            Get reserve amount of select token in the exchange pair
                
            Parameters
            -------
            token : ERC20
                ERC20 token                
        """         
        
        if(token.token_name == self.token0):
            return self.reserve0 
        elif(token.token_name == self.token1):
            return self.reserve1 
        else:
            print('ERROR: wrong input token')               