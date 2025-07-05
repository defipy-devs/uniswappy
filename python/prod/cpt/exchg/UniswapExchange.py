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

from ...erc import LPERC20
from ...utils.interfaces import IExchange 
from ...utils.data import UniswapExchangeData
from ...utils.data import FactoryData
from ...utils.tools.v3 import UniV3Helper
from ...utils.tools import SaferMath
import math


#MINIMUM_LIQUIDITY = 1e-15
MINIMUM_LIQUIDITY = 1000

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
        self.precision = exchg_struct.precision
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

        reserve0 = self.convert_to_human(self.reserve0)
        reserve1 = self.convert_to_human(self.reserve1)
        total_supply = self.convert_to_human(self.total_supply)
        
        print(f"Exchange {self.name} ({self.symbol})")
        print(f"Reserves: {self.token0} = {reserve0}, {self.token1} = {reserve1}")
        print(f"Liquidity: {total_supply} \n")    

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

        amountADesired = self.convert_to_machine(amountADesired)
        amountBDesired = self.convert_to_machine(amountBDesired)
        amountAMin = self.convert_to_machine(amountAMin)
        amountBMin = self.convert_to_machine(amountBMin)

        tokens = self.factory.token_from_exchange[self.name]
        assert tokens.get(self.token0) and tokens.get(self.token1), 'UniswapV2: TOKEN_UNAVAILABLE' 
        amountA, amountB = self._add_liquidity(amountADesired, amountBDesired, amountAMin, amountBMin)
        
        tokens.get(self.token0).deposit(_from_addr, int(amountA))
        tokens.get(self.token1).deposit(_from_addr, int(amountB))

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
                assert round(int(amountBOptimal),-25) >= round(int(amountBMin),-25), 'UniswapV2: INSUFFICIENT_B_AMOUNT'
                amountA = amountADesired
                amountB = amountBOptimal
            else:
                amountAOptimal = self.quote(amountBDesired, self.reserve1, self.reserve0)                
                assert round(int(amountAOptimal),-20) <= round(int(amountADesired),-20)
                assert round(int(amountAOptimal),-20) >= round(int(amountAMin),-20), 'UniswapV2: INSUFFICIENT_A_AMOUNT'
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

        amountA = SaferMath().mul_div_round(liquidity, balanceA, self.total_supply)
        amountB = SaferMath().mul_div_round(liquidity, balanceB, self.total_supply)
        
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
     
        liquidity = self.convert_to_machine(liquidity)
        amountAMin = self.convert_to_machine(amountAMin)
        amountBMin = self.convert_to_machine(amountBMin)

        tokens = self.factory.token_from_exchange[self.name]
        assert tokens.get(self.token0) and tokens.get(self.token1), 'UniswapV2: TOKEN_UNAVAILABLE' 

        balanceA = tokens.get(self.token0).token_total
        balanceB = tokens.get(self.token1).token_total
        total_liquidity = self.liquidity_providers[to_addr]
        if liquidity >= total_liquidity:
            liquidity = total_liquidity

        amountA = SaferMath().mul_div_round(liquidity, balanceA, self.total_supply)
        amountB = SaferMath().mul_div_round(liquidity, balanceB, self.total_supply)

        assert (round(int(amountA),-20) >= round(int(amountAMin),-20)), 'AMOUNTA {} AMOUNT_A_MIN {}'.format(round(amountA,5), round(amountAMin,5))
        assert amountA > 0 and amountB > 0, 'UniswapV2: INSUFFICIENT_LIQUIDITY_BURNED'
        assert round(int(amountA),-20) >= round(int(amountAMin),-20), 'UniswapV2: INSUFFICIENT_A_AMOUNT'
        assert round(int(amountB),-20) >= round(int(amountBMin),-20), 'UniswapV2: INSUFFICIENT_B_AMOUNT'
        
        self.burn(to_addr, liquidity, amountA, amountB)
        return self.convert_to_human(amountA), self.convert_to_human(amountB)

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

        amount_out_expected = self.convert_to_machine(amount_out_expected)
        amountIn = self.convert_to_machine(amountIn)
        amountOutMin = self.convert_to_machine(amountOutMin)        

        tokens = self.factory.token_from_exchange[self.name]
        if(token_in.token_name == self.token0):
            tokens.get(self.token0).deposit(to_addr, amountIn)
            self.swap(0, amount_out_expected, to_addr)
        elif(token_in.token_name == self.token1):
            tokens.get(self.token1).deposit(to_addr, amountIn)
            self.swap(amount_out_expected, 0, to_addr)

        return self.convert_to_human(amount_out_expected)

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
        
        assert round(int(amountA),-10) == round(int(_amountA),-10)
        assert round(int(amountB),-10) == round(int(_amountB),-10) 

        if self.total_supply != 0:
            liquidity = min(
                SaferMath().mul_div_round(amountA, self.total_supply, self.reserve0),
                SaferMath().mul_div_round(amountB, self.total_supply, self.reserve1)
            )
        else:
            liquidity = math.isqrt(amountA * amountB) - MINIMUM_LIQUIDITY
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
        
        self.reserve0 = int(balanceA)  
        self.reserve1 = int(balanceB)

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
        self._tally_fees(SaferMath().mul_div_round(amountA_in, 3, 1000), SaferMath().mul_div_round(amountB_in, 3, 1000))             
 
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

        amountA = self.convert_to_machine(amountA)
        reserveA = self.convert_to_machine(reserveA)
        reserveB = self.convert_to_machine(reserveB)
        
        assert amountA > 0, 'UniswapV2Library: INSUFFICIENT_AMOUNT'
        assert reserveA > 0 and reserveB > 0, 'UniswapV2Library: INSUFFICIENT_LIQUIDITY'
        quote_out = SaferMath().mul_div_round(amountA, reserveB, reserveA)   
        
        return self.convert_to_human(quote_out)

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

        amount_in = self.convert_to_machine(amount_in)
        
        assert amount_in > 0, 'UniswapV2Library: INSUFFICIENT_INPUT_AMOUNT'
        assert self.reserve0 > 0 and self.reserve1 > 0, 'UniswapV2Library: INSUFFICIENT_LIQUIDITY'

        amount_in_with_fee = amount_in * 997  
        amount_out =  SaferMath().div_round(amount_in * 997  * self.reserve1, self.reserve0 * 1000 + amount_in_with_fee)

        return self.convert_to_human(amount_out) 
    
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

        amount_in = self.convert_to_machine(amount_in)
        
        assert amount_in > 0, 'UniswapV2Library: INSUFFICIENT_INPUT_AMOUNT'
        assert self.reserve0 > 0 and self.reserve1 > 0, 'UniswapV2Library: INSUFFICIENT_LIQUIDITY'

        amount_in_with_fee = amount_in * 997    
        amount_out = SaferMath().div_round(amount_in_with_fee * self.reserve0, self.reserve1 * 1000 + amount_in_with_fee)

        return self.convert_to_human(amount_out)  

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
        
        amountA_update = amountA_update if amountA_update != None else self.reserve0
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
                #return SaferMath().div_round(self.reserve0, self.reserve1)
        else:
            assert False, 'UniswapV2: WRONG_INPUT_TOKEN'      

    def get_last_liquidity_deposit(self):  
        
        """ get_last_liquidity_deposit

            Get the last liquidity deposit that went into pool         
        """          

        return self.convert_to_human(self.last_liquidity_deposit)     


    def get_liquidity_from_provider(self, provider_account):  
        
        """ get_liquidity_from_provider

            Get liquidity from provider  
            
            Parameters
            -----------------
            provider_account : str
                Provider account name  
            
        """          

        return self.convert_to_human(self.liquidity_providers[provider_account])      
                

    
    def get_liquidity(self):  
        
        """ get_liquidity

            Get liquidity of exchange pool         
        """          

        return self.convert_to_human(self.total_supply)       
            
    def get_reserve(self, token):  
        
        """ get_reserve

            Get reserve amount of select token in the exchange pair
                
            Parameters
            -----------------
            token : ERC20
                ERC20 token                
        """         
        
        if(token.token_name == self.token0):
            return self.convert_to_human(self.reserve0)
        elif(token.token_name == self.token1):
            return self.convert_to_human(self.reserve1) 
        else:
            assert False, 'UniswapV2: WRONG_INPUT_TOKEN'  

    def get_fee(self, token):  
        
        """ get_fee

            Get last fee amount of select token in the exchange pair
                
            Parameters
            -----------------
            token : ERC20
                ERC20 token                
        """         
        
        if(token.token_name == self.token0):
            return self.convert_to_human(self.collected_fee0)
        elif(token.token_name == self.token1):
            return self.convert_to_human(self.collected_fee1) 
        else:
            assert False, 'UniswapV2: WRONG_INPUT_TOKEN'  

    def convert_to_human(self, val): 
        val = val if self.precision == UniswapExchangeData.TYPE_GWEI else UniV3Helper().gwei2dec(val)
        return val

    def convert_to_machine(self, val): 
        val = int(val) if self.precision == UniswapExchangeData.TYPE_GWEI else UniV3Helper().dec2gwei(val)
        return val   
    
        