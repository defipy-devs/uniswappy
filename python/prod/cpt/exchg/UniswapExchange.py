# Copyright [2023] [Ian Moore]
# Distributed under the MIT License (license terms are at http://opensource.org/licenses/MIT).
# Email: defipy.devs@gmail.com

from ...erc import ERC20
from ...erc import LPERC20
from ...utils.interfaces import IExchange 
from ...utils.data import UniswapExchangeData
from ...utils.data import FactoryData
import math

MINIMUM_LIQUIDITY = 1e-15

class UniswapExchange(IExchange, LPERC20):
    
    """ 
        Uniswap V2 Exchange  

        Parameters
        -----------------
        factory_struct : FactoryInit
            Factory initialization data
        exchg_struct : UniswapExchangeInit
            Exchange initialization data           
    """          
    def __init__(self, factory_struct: FactoryData, exchg_struct: UniswapExchangeData):
        super().__init__(exchg_struct.tkn0.token_name+exchg_struct.tkn1.token_name, exchg_struct.address)
        self.version = exchg_struct.version
        self.factory = factory_struct
        self.token0 = exchg_struct.tkn0.token_name     
        self.token1 = exchg_struct.tkn1.token_name       
        self.reserve0 = 0             
        self.reserve1 = 0       
        self.fee0_arr = []
        self.fee1_arr = []
        self.aggr_fee0 = 0
        self.aggr_fee1 = 0
        self.collected_fee0 = 0
        self.collected_fee1 = 0              
        self.name =  f"{self.token0}-{self.token1}"
        self.symbol = exchg_struct.symbol
        self.liquidity_providers = {}
        self.last_liquidity_deposit = 0
        self.total_supply = 0

    def summary(self):

        """ summary
            Summary print-out of exchange, reserves and liquidity               
        """  
        
        print(f"Exchange {self.name} ({self.symbol})")
        print(f"Reserves: {self.token0} = {self.reserve0}, {self.token1} = {self.reserve1}")
        print(f"Liquidity: {self.total_supply} \n")

    def add_liquidity(self, _from_addr, amountADesired, amountBDesired, amountAMin, amountBMin):
        
        """ add_liquidity

            Add liquidity to both tokens in the pair
                
            Parameters
            -----------------
            _from_addr : str
                receiving user address      
            amountADesired : float
                desired amount of A      
            amountBDesired : float
                desired amount of B   
            amountAMin : float
                Minimum amount of A  
            amountBMin : float
                Minimum amount of B                 
        """           
        
        tokens = self.factory.token_from_exchange[self.name]
        assert tokens.get(self.token0) and tokens.get(self.token1), 'UniswapV2: TOKEN_UNAVAILABLE' 
        amountA, amountB = self._add_liquidity(amountADesired, amountBDesired, amountAMin, amountBMin)

        tokens.get(self.token0).deposit(_from_addr, amountA)
        tokens.get(self.token1).deposit(_from_addr, amountB)

        self.mint(_from_addr, amountA, amountB)
        return amountA, amountB

    def _add_liquidity(self, amountADesired, amountBDesired, amountAMin, amountBMin):
        
        """ _add_liquidity

            Add liquidity to both tokens in the pair
                
            Parameters
            -----------------    
            amountADesired : float
                desired amount of A      
            amountBDesired : float
                desired amount of B   
            amountAMin : float
                Minimum amount of A  
            amountBMin : float
                Minimum amount of B   
                
            Returns
            -------
            amount0 : float
                removed liquidity from reserve0    
            amount1 : float
                removed liquidity from reserve1                   
        """            
        
        tokens = self.factory.token_from_exchange[self.name]
        assert tokens.get(self.token0) and tokens.get(self.token1), 'UniswapV2: TOKEN_UNAVAILABLE' 

        if self.reserve0 == 0 and self.reserve1 == 0:
            amountA = amountADesired
            amountB = amountBDesired
        else:
            amountBOptimal = self.quote(amountADesired, self.reserve0, self.reserve1)
            if amountBOptimal <= amountBDesired:                
                assert round(amountBOptimal,5) >= round(amountBMin,5), 'UniswapV2: INSUFFICIENT_B_AMOUNT'
                amountA = amountADesired
                amountB = amountBOptimal
            else:
                amountAOptimal = self.quote(amountBDesired, self.reserve1, self.reserve0)
                assert round(amountAOptimal,5) <= round(amountADesired,5)
                assert round(amountAOptimal,5) >= round(amountAMin,5), 'UniswapV2: INSUFFICIENT_A_AMOUNT'
                amountA = amountAOptimal
                amountB = amountBDesired

        return amountA, amountB

    def get_amounts(self, to_addr, liquidity):
        
        """ get_amounts

            Remove liquidity from both coins in the pair based on lp amount
                
            Parameters
            -----------------
            to_addr : str
                receiving user address  
            liquidity : float
                lp amount                  
                
            Returns
            -------
            amountA : float
                liquidity portion of reserve0    
            amountB : float
                liquidity portion of reserve1                    
        """         
        
        tokens = self.factory.token_from_exchange[self.name]
        assert tokens.get(self.token0) and tokens.get(self.token1), 'UniswapV2: TOKEN_UNAVAILABLE' 

        balanceA = tokens.get(self.token0).token_total
        balanceB = tokens.get(self.token1).token_total
        total_liquidity = self.liquidity_providers[to_addr]
        if liquidity >= total_liquidity:
            liquidity = total_liquidity

        amountA = liquidity * balanceA / self.total_supply     
        amountB = liquidity * balanceB / self.total_supply    

        return amountA, amountB    
    
    def remove_liquidity(self, to_addr, liquidity, amountAMin, amountBMin):
        
        """ remove_liquidity

            Remove liquidity from both coins in the pair based on lp amount
                
            Parameters
            -----------------
            to_addr : str
                receiving user address  
            liquidity : float
                lp amount to removed                 
            amountAMin : float
                Minimum amount of A  
            amountBMin : float
                Minimum amount of B 
                
            Returns
            -------
            amountA : float
                removed liquidity from reserve0    
            amountB : float
                removed liquidity from reserve1                    
        """         
        
        tokens = self.factory.token_from_exchange[self.name]
        assert tokens.get(self.token0) and tokens.get(self.token1), 'UniswapV2: TOKEN_UNAVAILABLE' 

        balanceA = tokens.get(self.token0).token_total
        balanceB = tokens.get(self.token1).token_total
        total_liquidity = self.liquidity_providers[to_addr]
        if liquidity >= total_liquidity:
            liquidity = total_liquidity

        amountA = liquidity * balanceA / self.total_supply    
        amountB = liquidity * balanceB / self.total_supply  
        
        assert (round(amountA,5) >= round(amountAMin,5)), 'AMOUNTA {} AMOUNT_A_MIN {}'.format(round(amountA,5), round(amountAMin,5))
        assert amountA > 0 and amountB > 0, 'UniswapV2: INSUFFICIENT_LIQUIDITY_BURNED'
        assert round(amountA,5) >= round(amountAMin,5), 'UniswapV2: INSUFFICIENT_A_AMOUNT'
        assert round(amountB,5) >= round(amountBMin,5), 'UniswapV2: INSUFFICIENT_B_AMOUNT'
        
        self.burn(to_addr, liquidity, amountA, amountB)
        return amountA, amountB

    def swap_exact_tokens_for_tokens(self, amountIn, amountOutMin, token_in, to_addr):
        
        """ swap_exact_tokens_for_tokens

            Swap amt of token for min opposing token out
                
            Parameters
            -----------------
            amountIn : float
                swap amount in
            amountOutMin : float
                min swap amount in                
            token_in : ERC20
                Token to be swapped
            to_addr : str
               receiving user address  
                
            Returns
            -------
            amount_out_expected : float
                amount expected from the swap                    
        """          
        
        amount_out_expected = self.get_amount_out(amountIn, token_in)
        assert amount_out_expected >= amountOutMin, 'UniswapV2: INSUFFICIENT_OUTPUT_AMOUNT'

        tokens = self.factory.token_from_exchange[self.name]
        if(token_in.token_name == self.token0):
            tokens.get(self.token0).deposit(to_addr, amountIn)
            self.swap(0, amount_out_expected, to_addr)
        elif(token_in.token_name == self.token1):
            tokens.get(self.token1).deposit(to_addr, amountIn)
            self.swap(amount_out_expected, 0, to_addr)
            
        return amount_out_expected

    def burn(self, to_addr, liquidity, amountA, amountB):
        
        """ burn

            Burn liquidity from both coins in the pair based on lp amount
                
            Parameters
            -----------------
            to_addr : str
               receiving user address  
            liquidity : float
                amount of liquidity to be burned                  
            amountA : float
                est. amount from reserve0 to be burned
            amountB : float
                est. amount from reserve1 to be burned               
        """          
        
        self._burn(to_addr, liquidity)

        tokens = self.factory.token_from_exchange[self.name]
        tokens.get(self.token0).transfer(to_addr, amountA)
        tokens.get(self.token1).transfer(to_addr, amountB)

        balanceA = tokens.get(self.token0).token_total
        balanceB = tokens.get(self.token1).token_total

        self._update(balanceA, balanceB)

    def _burn(self, to_addr, value):
        
        """ _burn

            Burn liquidity from both coins in the pair based on lp amount
                
            Parameters
            -----------------
            to : str
               receiving user address  
            value : float
                amount of liquidity to be burned                           
        """            
        
        available_liquidity = self.liquidity_providers.get(to_addr)
        self.liquidity_providers[to_addr] = available_liquidity - value
        self.total_supply -= value

    def mint(self, to_addr, _amountA, _amountB):
        
        """ mint

            Mint new liquidity based on amounts on each coin in the pair
                
            Parameters
            -----------------
            to_addr : str
                receiving user address      
            _amountA : float
                desired amount of A      
            _amountB : float
                desired amount of B                   
        """          
        
        tokens = self.factory.token_from_exchange[self.name]
        assert tokens.get(self.token0) and tokens.get(self.token1), 'UniswapV2: TOKEN_UNAVAILABLE' 

        balanceA = tokens.get(self.token0).token_total
        balanceB = tokens.get(self.token1).token_total

        amountA = balanceA - self.reserve0
        amountB = balanceB - self.reserve1
        
        assert round(amountA,3) == round(_amountA,3)
        assert round(amountB,3) == round(_amountB,3)

        if self.total_supply != 0:
            liquidity = min(
                amountA * self.total_supply / self.reserve0,
                amountB * self.total_supply / self.reserve1
            )
        else:
            liquidity = math.sqrt(amountA * amountB) - MINIMUM_LIQUIDITY
            self._mint("0", MINIMUM_LIQUIDITY)

        assert liquidity > 0, 'UniswapV2: INSUFFICIENT_LIQUIDITY_MINTED'
        
        self._update(balanceA, balanceB)
        self._mint(to_addr, liquidity)

    def _update(self, balanceA, balanceB):
        
        """ _update

            Update reserve amounts for both coins in the pair
                
            Parameters
            -----------------   
            balanceA : float
                new reserve amount of A      
            balance1 : float
                new reserve amount of B                   
        """         
        
        self.reserve0 = balanceA
        self.reserve1 = balanceB

    def _mint(self, to_addr, value):
        
        """ _mint

            Update reserve amounts for both coins in the pair
                
            Parameters
            -----------------   
            to_addr : str
                receiving user address       
            value : float
                amount of new liquidity                  
        """          
        
        if self.liquidity_providers.get(to_addr):
            self.liquidity_providers[to_addr] += value
        else:
            self.liquidity_providers[to_addr] = value

        self.last_liquidity_deposit = value     
        self.total_supply += value
        
    def _tally_fees(self, fee0, fee1):
        
        """ _tally_fees

            Tally fee from swap and record last collected fee
                
            Parameters
            -----------------   
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
        
    def swap(self, amountA_out, amountB_out, to_addr):
        
        """ swap

            Remove liquidity from both coins in the pair based on lp amount
                
            Parameters
            -----------------
            amountA_out : float
                swap amountA out
            amountB_out : float
                swap amountB out               
            to_addr : str
               receiving user address                   
        """         
        
        assert amountA_out > 0 or amountB_out > 0, 'UniswapV2: INSUFFICIENT_OUTPUT_AMOUNT'
        assert amountA_out < self.reserve0 and amountB_out < self.reserve1, 'UniswapV2: INSUFFICIENT_LIQUIDITY'

        tokens = self.factory.token_from_exchange[self.name]
        assert tokens.get(self.token0).token_addr != to_addr, 'UniswapV2: INVALID_TO_ADDRESS'
        assert tokens.get(self.token1).token_addr != to_addr, 'UniswapV2: INVALID_TO_ADDRESS'

        tokens.get(self.token0).transfer(to_addr, amountA_out)
        tokens.get(self.token1).transfer(to_addr, amountB_out)    
        
        balanceA = tokens.get(self.token0).token_total
        balanceB = tokens.get(self.token1).token_total

        amountA_in = balanceA - (self.reserve0 - amountA_out) if balanceA > self.reserve0 - amountA_out else 0
        amountB_in = balanceB - (self.reserve1 - amountB_out) if balanceB > self.reserve1 - amountB_out else 0
        assert amountA_in > 0 or amountB_in > 0, 'UniswapV2: INSUFFICIENT_INPUT_AMOUNT'

        balanceA_adjusted = balanceA * 1000 - amountA_in * 3  
        balanceB_adjusted = balanceB * 1000 - amountB_in * 3  
 
        adj_digits = max(len(str(balanceA_adjusted * balanceB_adjusted))-11, 1)
        lside = round(math.ceil(balanceA_adjusted * balanceB_adjusted), -adj_digits)
        rside = round(math.ceil(self.reserve0 * self.reserve1 * 1000**2), -adj_digits)

        # ******** FIX ********
        #assert  lside  ==  rside , 'UniswapV2: K'
    
        self._update(balanceA, balanceB)
        self._tally_fees(amountA_in * 3 / 1000, amountB_in * 3 / 1000)           
 
    def quote(self, amountA, reserveA, reserveB):
        
        """ quote

            Given amount asset and reserves, return equivalent amount of other asset
                
            Parameters
            -----------------
            amountA : float
                amount of a given asset token
            reserveA : float
                total amount of asset A in LP              
            reserveB : float
                total amount of asset B in LP                    
        """          
        
        assert amountA > 0, 'UniswapV2Library: INSUFFICIENT_AMOUNT'
        assert reserveA > 0 and reserveB > 0, 'UniswapV2Library: INSUFFICIENT_LIQUIDITY'
        return (amountA * reserveB) / reserveA;        

    def get_amount_out(self, amount_in, token_in):

        """ get_amount_out

            Get maximum output of opposing asset given input amount of token
                
            Parameters
            -----------------
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

            Get maximum amount of other asset given input amount of an asset
                
            Parameters
            -----------------
            amount_in : float
                input amount of an asset
                          
            Returns
            -------
            amount_out out : float
                reserve1 * reserve0       
        """
        
        assert amount_in > 0, 'UniswapV2Library: INSUFFICIENT_INPUT_AMOUNT'
        assert self.reserve0 > 0 and self.reserve1 > 0, 'UniswapV2Library: INSUFFICIENT_LIQUIDITY'

        amount_in_with_fee = amount_in * 997  
        amount_out = (amount_in * 997  * self.reserve1) / (self.reserve0 * 1000 + amount_in_with_fee)

        return amount_out
    
    def get_amount_out1(self, amount_in):
        
        """ get_amount_out1

            Get maximum amount of other asset given input amount of an asset
                
            Parameters
            -----------------
            amount_in : float
                input amount of an asset
                          
            Returns
            -------
            amount_out out : float
                reserve1 * reserve0       
        """        
        
        assert amount_in > 0, 'UniswapV2Library: INSUFFICIENT_INPUT_AMOUNT'
        assert self.reserve0 > 0 and self.reserve1 > 0, 'UniswapV2Library: INSUFFICIENT_LIQUIDITY'

        amount_in_with_fee = amount_in * 997    
        amount_out = (amount_in_with_fee * self.reserve0) / (self.reserve1 * 1000 + amount_in_with_fee)

        return amount_out 

    def update_reserves(self, user_nm, amountA_update = None, amountB_update = None):
        
        """ update_reserves

            Update reserve assets of either or both assets in the pair
                
            Parameters
            -----------------
            user_nm : str
                acccount holder
            amountA_update : float
                update amount of asset A             
            amountB_update : float
                update amount of asset B      
        """          
        
        amountA_update = amountA_update if amount0_update != None else self.reserve0
        amountB_update = amountB_update if amountB_update != None else self.reserve1
        self.burn(user_nm, self.liquidity_providers[user_nm], self.reserve0, self.reserve1)
        tokens = self.factory.token_from_exchange[self.name]
        tokens.get(self.token0).deposit(user_nm, amountA_update)
        tokens.get(self.token1).deposit(user_nm, amountB_update)
        self.mint(user_nm, amountA_update, amountB_update)                  
                    
    def get_price(self, token):  
        
        """ get_price

            Get price of select token in the exchange pair
                
            Parameters
            -----------------
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
            assert False, 'UniswapV2: WRONG_INPUT_TOKEN'      

    def get_liquidity(self):  
        
        """ get_liquidity

            Get liquidity of exchange pool         
        """          

        return self.total_supply       
            
    def get_reserve(self, token):  
        
        """ get_reserve

            Get reserve amount of select token in the exchange pair
                
            Parameters
            -----------------
            token : ERC20
                ERC20 token                
        """         
        
        if(token.token_name == self.token0):
            return self.reserve0 
        elif(token.token_name == self.token1):
            return self.reserve1 
        else:
            assert False, 'UniswapV2: WRONG_INPUT_TOKEN'                