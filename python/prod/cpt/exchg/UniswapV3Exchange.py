# Copyright [2024] [Ian Moore]
# Distributed under the MIT License (license terms are at http://opensource.org/licenses/MIT).
# Email: defipy.devs@gmail.com

# Modified version of original MIT licenced UniswapPool class from chainflip-io
# - https://github.com/chainflip-io/chainflip-uniswapV3-python

import math
from decimal import Decimal
from dataclasses import dataclass
from ...erc import LPERC20
from ...utils.interfaces import IExchange
from ...utils.data import FactoryData
from ...utils.data import UniswapExchangeData
from ...utils.tools.v3.Shared import *
from ...utils.tools.v3 import Position, Tick, SqrtPriceMath, LiquidityMath
from ...utils.tools.v3 import SwapMath, TickMath, SafeMath, FullMath, UniV3Utils
from ...utils.tools.v3 import UniV3Helper

MINIMUM_LIQUIDITY = 1e-15
GWEI_PRECISION = 18

@dataclass
class Slot0:
    ## the current price
    sqrtPriceX96: int
    ## the current tick
    tick: int
    ## the current protocol fee as a percentage of the swap fee taken on withdrawal
    ## represented as an integer denominator (1#x)%
    feeProtocol: int
    
@dataclass
class ModifyPositionParams:
    ## the address that owns the position
    owner: str
    ## the lower and upper tick of the position
    tickLower: int
    tickUpper: int
    ## any change in liquidity
    liquidityDelta: int  

@dataclass
class SwapCache:
    ## the protocol fee for the input token
    feeProtocol: int
    ## liquidity at the beginning of the swap
    liquidityStart: int

@dataclass
class SwapState:
    ## the amount remaining to be swapped in#out of the input#output asset
    amountSpecifiedRemaining: int
    ## the amount already swapped out#in of the output#input asset
    amountCalculated: int
    ## current sqrt(price)
    sqrtPriceX96: int
    ## the tick associated with the current price
    tick: int
    ## the global fee growth of the input token
    feeGrowthGlobalX128: int
    ## amount of input token paid as protocol fee
    protocolFee: int
    ## the current liquidity in range
    liquidity: int

    ## list of ticks crossed during the swap
    ticksCrossed: list

@dataclass
class StepComputations:
    ## the price at the beginning of the step
    sqrtPriceStartX96: int
    ## the next tick to swap to from the current tick in the swap direction
    tickNext: int
    ## whether tickNext is initialized or not
    initialized: bool
    ## sqrt(price) for the next tick (1#0)
    sqrtPriceNextX96: int
    ## how much is being swapped in in this step
    amountIn: int
    ## how much is being swapped out
    amountOut: int
    ## how much fee is being paid in
    feeAmount: int

@dataclass
class ProtocolFees:
    token0: int
    token1: int

class UniswapV3Exchange(IExchange, LPERC20):

    """ 
        Uniswap V3 Exchange  

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
        self.fee = exchg_struct.fee
        self.fee0_arr = []
        self.fee1_arr = []
        self.aggr_fee0 = 0
        self.aggr_fee1 = 0
        self.collected_fee0 = 0
        self.collected_fee1 = 0              
        self.name =  f"{self.token0}-{self.token1}"
        self.symbol = exchg_struct.symbol
        self.precision = exchg_struct.precision
        self.last_liquidity_deposit = 0
        self.total_supply = 0
        self.slot0 = Slot0(0, 0, 0)
        self.positions = {}
        self.ticks = {}
        self.feeGrowthGlobal0X128 = 0
        self.feeGrowthGlobal1X128 = 0  
        self.protocolFees = ProtocolFees(0, 0)
        self.tickSpacing = exchg_struct.tick_spacing
        self.maxLiquidityPerTick = Tick.tickSpacingToMaxLiquidityPerTick(self.tickSpacing)      

    def summary(self):

        """ summary
            Summary print-out of exchange, reserves and liquidity              
        """         
        
        tokens = self.factory.token_from_exchange[self.name] 
        x_tkn = tokens[self.token0]
        y_tkn = tokens[self.token1]          
        print(f"Exchange {self.name} ({self.symbol})")
        if (self.precision == UniswapExchangeData.TYPE_GWEI):
            print(f"Real Reserves:   {self.token0} = {self.reserve0}, {self.token1} = {self.reserve1}")
            print(f"Gross Liquidity: {self.total_supply} \n")
        else:  
            res0 = UniV3Helper().gwei2dec(self.reserve0)
            res1 = UniV3Helper().gwei2dec(self.reserve1)
            print(f"Real Reserves:   {self.token0} = {res0}, {self.token1} = {res1}")
            print(f"Gross Liquidity: {UniV3Helper().gwei2dec(self.total_supply)} \n")            

    def initialize(self, sqrtPriceX96):

        """ initialize

            Sets the initial price for the pool
                
            Parameters
            -----------------
            sqrtPriceX96 : float
                the initial sqrt price of the pool as a Q64.96                     
        """  
        
        checkInputTypes(uint160=(sqrtPriceX96))
        assert self.slot0.sqrtPriceX96 == 0, "UniswapV3: AI"

        tick = TickMath.getTickAtSqrtRatio(sqrtPriceX96)

        self.slot0 = Slot0(
            sqrtPriceX96,
            tick,
            0,
        )
    
    def mint(self, recipient, tickLower, tickUpper, amount): 

        """ mint

            Adds liquidity for the given recipient/tickLower/tickUpper position. The final amounts 
            calculated are automatically transferred from the swapper to the pool and vice verse. 
            The amount of token0/token1 due depends on tickLower, tickUpper, the amount of liquidity, 
            and the current price.
                
            Parameters
            -----------------    
            recipient : str
                Address for which the liquidity will be created      
            tickLower : int
                Lower tick of the position in which to add liquidity  
            tickUpper : int
                Upper tick of the position in which to add liquidity 
            amount : int
                Amount of liquidity to mint  
                
            Returns
            -------
            amount0 : float
                Amount of token0 that was paid to mint the given amount of liquidity.   
            amount1 : float
                Amount of token1 that was paid to mint the given amount of liquidity.                   
        """          
        amount = self._convert_to_machine(amount)
        
        checkInputTypes(
            accounts=(recipient), int24=(tickLower, tickUpper), uint128=(amount)
        )
        assert amount > 0

        (_, amount0Int, amount1Int) = self._modifyPosition(
            ModifyPositionParams(recipient, tickLower, tickUpper, amount)
        )

        amount0 = toUint256(abs(amount0Int))
        amount1 = toUint256(abs(amount1Int))
        
        tokens = self.factory.token_from_exchange[self.name]
        assert tokens.get(self.token0) and tokens.get(self.token1), 'UniswapV3: TOKEN_UNAVAILABLE' 

        balance0Before = tokens.get(self.token0).token_total
        balance1Before = tokens.get(self.token1).token_total 
        
        tokens.get(self.token0).deposit(recipient, amount0)
        tokens.get(self.token1).deposit(recipient, amount1)  

        balanceA = tokens.get(self.token0).token_total
        balanceB = tokens.get(self.token1).token_total

        self._update(balanceA, balanceB)
    
        assert balance0Before + amount0 <= tokens.get(self.token0).token_total, 'UniswapV3: M0' 
        assert balance1Before + amount1 <= tokens.get(self.token1).token_total, 'UniswapV3: M0' 
 
        amount0 = self._convert_to_human(amount0)
        amount1 = self._convert_to_human(amount1)        
              
        return (amount0, amount1)
        

    def collect(self, recipient, tickLower, tickUpper, amount0Requested, amount1Requested):

        """ collect

            Collects tokens owed to a position. Does not recompute fees earned, which must be done either 
            via mint or burn of any amount of liquidity. Collect must be called by the position owner. 
            To withdraw only token0 or only token1, amount0Requested or amount1Requested may be set to zero. 
            To withdraw all tokens owed, caller may pass any value greater than the actual tokens owed, e.g. 
            type(uint128).max. Tokens owed may be from accumulated swap fees or burned liquidity.
                
            Parameters
            -----------------    
            recipient : str
                Address for which the liquidity will be created      
            tickLower : int
                Lower tick of the position in which to add liquidity  
            tickUpper : int
                Lower tick of the position in which to add liquidity                 
            amount0Requested : int
                How much token0 should be withdrawn from the fees owed
            amount1Requested : int
                How much token1 should be withdrawn from the fees owed  
                
            Returns
            -------
            amount0 : float
                Amount of token0 that was paid to mint the given amount of liquidity.   
            amount1 : float
                Amount of token1 that was paid to mint the given amount of liquidity.                   
        """ 

        amount0Requested = self._convert_to_machine(amount0Requested)
        amount1Requested = self._convert_to_machine(amount1Requested)
        
        checkInputTypes(
            accounts=(recipient),
            int24=(tickLower, tickUpper),
            uint128=(amount0Requested, amount1Requested),
        )
        # Add this check to prevent creating a new position if the position doesn't exist or it's empty
        position = Position.assertPositionExists(
            self.positions, recipient, tickLower, tickUpper
        )

        amount0 = (
            position.tokensOwed0
            if (amount0Requested > position.tokensOwed0)
            else amount0Requested
        )
        amount1 = (
            position.tokensOwed1
            if (amount1Requested > position.tokensOwed1)
            else amount1Requested
        )

        tokens = self.factory.token_from_exchange[self.name]
        assert tokens.get(self.token0) and tokens.get(self.token1), 'UniswapV3: TOKEN_UNAVAILABLE' 
        
        if amount0 > 0:
            position.tokensOwed0 -= amount0
            tokens.get(self.token0).deposit(recipient, amount0)
            #self.ledger.transferToken(self, recipient, self.token0, amount0)
        if amount1 > 0:
            position.tokensOwed1 -= amount1
            tokens.get(self.token1).deposit(recipient, amount1) 
            #self.ledger.transferToken(self, recipient, self.token1, amount1)
  
        amount0 = self._convert_to_human(amount0)
        amount1 = self._convert_to_human(amount1)        

        return (recipient, tickLower, tickUpper, amount0, amount1)   
        

    def burn(self, recipient, tickLower, tickUpper, amount):

        """ burn

            Burn liquidity from the sender and account tokens owed for the liquidity to the position. Can 
            be used to trigger a recalculation of fees owed to a position by calling with an amount of 0. 
            Fees must be collected separately via a call to collect
                
            Parameters
            -----------------    
            recipient : str
                Address for which the liquidity will be created      
            tickLower : int
                Lower tick of the position in which to add liquidity  
            tickUpper : int
                Lower tick of the position in which to add liquidity                 
            amount : int
                How much liquidity to burn
                
            Returns
            -------
            recipient : str
                Address for which the liquidity will be created 
            amount0 : int
                Delta of the balance of token0 of the pool, exact when negative, minimum when positive
            amount1 : int
                Delta of the balance of token1 of the pool, exact when negative, minimum when positive               
            amount : int
                How much liquidity to burn                  
        """  
        amount = self._convert_to_machine(amount)
        
        checkInputTypes(
            accounts=(recipient), int24=(tickLower, tickUpper), uint128=(amount)
        )

        # Add check if the position exists - when poking an uninitialized position it can be that
        # getFeeGrowthInside finds a non-initialized tick before Position.update reverts.
        Position.assertPositionExists(self.positions, recipient, tickLower, tickUpper)

        # Added extra recipient input variable to mimic msg.sender
        (position, amount0Int, amount1Int) = self._modifyPosition(
            ModifyPositionParams(recipient, tickLower, tickUpper, -amount)
        )

        tokens = self.factory.token_from_exchange[self.name]
        tokens.get(self.token0).deposit(recipient, amount0Int)
        tokens.get(self.token1).deposit(recipient, amount1Int)     

        balanceA = tokens.get(self.token0).token_total
        balanceB = tokens.get(self.token1).token_total

        self._update(balanceA, balanceB)        

        # Mimic conversion to uint256
        amount0 = abs(-amount0Int) & (2**256 - 1)
        amount1 = abs(-amount1Int) & (2**256 - 1)        

        if amount0 > 0 or amount1 > 0:
            position.tokensOwed0 += amount0
            position.tokensOwed1 += amount1

        amount = self._convert_to_human(amount)   
        amount0 = self._convert_to_human(amount0)
        amount1 = self._convert_to_human(amount1)
             
        return (recipient, tickLower, tickUpper, amount, amount0, amount1)



    def swapExact0For1(self, recipient, amount, sqrtPriceLimit):

        """ swapExact0For1

            Swap exact value of token0 for token1
                
            Parameters
            -----------------    
            recipient : str
                Address for which the liquidity will be created      
            amount : int
                How much token to swap
            sqrtPriceLimit : int
                Used to determine the highest price in the swap, and needs to be set when swapping on 
                the pool directly.       
                
            Returns
            -------
            recipient : str
                Address for which the liquidity will be created 
            amount0 : int
                Delta of the balance of token0 of the pool, exact when negative, minimum when positive
            amount1 : int
                Delta of the balance of token1 of the pool, exact when negative, minimum when positive                             
        """         
        amount = self._convert_to_machine(amount)
        sqrtPriceLimitX96 = (
            sqrtPriceLimit
            if sqrtPriceLimit != None
            else UniV3Utils.getSqrtPriceLimitX96('Token0')
        )

        return self._swap(UniV3Utils.TEST_TOKENS[0], [amount, 0], recipient, sqrtPriceLimitX96)  

    def swap0ForExact1(self, recipient,  amount, sqrtPriceLimit):

        """ swapExact0For1

            Swap token0 for exact value of token1
                
            Parameters
            -----------------    
            recipient : str
                Address for which the liquidity will be created      
            amount : int
                How much token to swap
            sqrtPriceLimit : int
                Used to determine the highest price in the swap, and needs to be set when swapping 
                on the pool directly.       
                
            Returns
            -------
            recipient : str
                Address for which the liquidity will be created 
            amount0 : int
                Delta of the balance of token0 of the pool, exact when negative, minimum when positive
            amount1 : int
                Delta of the balance of token1 of the pool, exact when negative, minimum when positive                             
        """           
        
        amount = self._convert_to_machine(amount)
        sqrtPriceLimitX96 = (
            sqrtPriceLimit
            if sqrtPriceLimit != None
            else UniV3Utils.getSqrtPriceLimitX96(UniV3Utils.TEST_TOKENS[0])
        )
        return self._swap(UniV3Utils.TEST_TOKENS[0], [0, amount], recipient, sqrtPriceLimitX96)  


    def swapExact1For0(self, recipient,  amount, sqrtPriceLimit):

        """ swapExact0For1

            Swap exact value of token1 for token0
                
            Parameters
            -----------------    
            recipient : str
                Address for which the liquidity will be created      
            amount : int
                How much token to swap
            sqrtPriceLimit : int
                Used to determine the highest price in the swap, and needs to be set when swapping 
                on the pool directly.       
                
            Returns
            -------
            recipient : str
                Address for which the liquidity will be created 
            amount0 : int
                Delta of the balance of token0 of the pool, exact when negative, minimum when positive
            amount1 : int
                Delta of the balance of token1 of the pool, exact when negative, minimum when positive                             
        """          
        
        amount = amount if self.precision == UniswapExchangeData.TYPE_GWEI else UniV3Helper().dec2gwei(amount)
        sqrtPriceLimitX96 = (
            sqrtPriceLimit
            if sqrtPriceLimit != None
            else UniV3Utils.getSqrtPriceLimitX96(UniV3Utils.TEST_TOKENS[1])
        )
        return self._swap(UniV3Utils.TEST_TOKENS[1], [amount, 0], recipient, sqrtPriceLimitX96)
    
    def swap1ForExact0(self, recipient, amount, sqrtPriceLimit):

        """ swapExact0For1

            Swap token1 for exact value of token0
                
            Parameters
            -----------------    
            recipient : str
                Address for which the liquidity will be created      
            amount : int
                How much token to swap
            sqrtPriceLimit : int
                Used to determine the highest price in the swap, and needs to be set when swapping 
                on the pool directly.       
                
            Returns
            -------
            recipient : str
                Address for which the liquidity will be created 
            amount0 : int
                Delta of the balance of token0 of the pool, exact when negative, minimum when positive
            amount1 : int
                Delta of the balance of token1 of the pool, exact when negative, minimum when positive                             
        """         

        amount = self._convert_to_machine(amount)
        sqrtPriceLimitX96 = (
            sqrtPriceLimit
            if sqrtPriceLimit != None
            else UniV3Utils.getSqrtPriceLimitX96(UniV3Utils.TEST_TOKENS[1])
        )
        return self._swap(UniV3Utils.TEST_TOKENS[1], [0, amount], recipient, sqrtPriceLimitX96)     

    def swap(self, recipient, zeroForOne, amountSpecified, sqrtPriceLimitX96):

        """ swap

            Swap token0 for token1, or token1 for token0. The tokens are automatically transferred 
            at the end of the swapping function.
                
            Parameters
            -----------------    
            recipient : str
                Address for which the liquidity will be created      
            zeroForOne : int
                the direction of the swap, true for token0 to token1, false for token1 to token0 
            amountSpecified : int
                The amount of the swap, which implicitly configures the swap as exact input 
                (positive), or exact output (negative)        
            sqrtPriceLimitX96 : int
                The Q64.96 sqrt price limit. If zero for one, the price cannot be less than this 
                value after the swap. If one for zero, the price cannot be greater than this 
                value after the swap
                
            Returns
            -------
            recipient : str
                Address for which the liquidity will be created 
            amount0 : int
                Delta of the balance of token0 of the pool, exact when negative, minimum when positive
            amount1 : int
                Delta of the balance of token1 of the pool, exact when negative, minimum when positive                             
        """ 
        
        checkInputTypes(
            accounts=(recipient),
            bool=(zeroForOne),
            int256=(amountSpecified),
            uint160=(sqrtPriceLimitX96),
        )
        assert amountSpecified != 0, "UniswapV3: AS"

        slot0Start = self.slot0        
        
        if zeroForOne:
            assert (
                sqrtPriceLimitX96 < slot0Start.sqrtPriceX96
                and sqrtPriceLimitX96 > TickMath.MIN_SQRT_RATIO
            ), "UniswapV3: ZEROFORONE SPL"
        else:
            assert (
                sqrtPriceLimitX96 > slot0Start.sqrtPriceX96
                and sqrtPriceLimitX96 < TickMath.MAX_SQRT_RATIO
            ), "UniswapV3: ONEFORZERO SPL"
  
        feeProtocol = (
            (slot0Start.feeProtocol % 16)
            if zeroForOne
            else (slot0Start.feeProtocol >> 4)
        )

        cache = SwapCache(feeProtocol, self.total_supply)

        exactInput = amountSpecified > 0

        state = SwapState(
            amountSpecified,
            0,
            slot0Start.sqrtPriceX96,
            slot0Start.tick,
            self.feeGrowthGlobal0X128 if zeroForOne else self.feeGrowthGlobal1X128,
            0,
            cache.liquidityStart,
            [],
        )

        while (
            state.amountSpecifiedRemaining != 0
            and state.sqrtPriceX96 != sqrtPriceLimitX96
        ):
            step = StepComputations(0, 0, 0, 0, 0, 0, 0)
            step.sqrtPriceStartX96 = state.sqrtPriceX96

            (step.tickNext, step.initialized) = self.nextTick(state.tick, zeroForOne)

            ## get the price for the next tick
            step.sqrtPriceNextX96 = TickMath.getSqrtRatioAtTick(step.tickNext)

            ## compute values to swap to the target tick, price limit, or point where input#output amount is exhausted
            if zeroForOne:
                sqrtRatioTargetX96 = (
                    sqrtPriceLimitX96
                    if step.sqrtPriceNextX96 < sqrtPriceLimitX96
                    else step.sqrtPriceNextX96
                )
            else:
                sqrtRatioTargetX96 = (
                    sqrtPriceLimitX96
                    if step.sqrtPriceNextX96 > sqrtPriceLimitX96
                    else step.sqrtPriceNextX96
                )

            (
                state.sqrtPriceX96,
                step.amountIn,
                step.amountOut,
                step.feeAmount,
            ) = SwapMath.computeSwapStep(
                state.sqrtPriceX96,
                sqrtRatioTargetX96,
                state.liquidity,
                state.amountSpecifiedRemaining,
                self.fee,
            )

            if exactInput:
                state.amountSpecifiedRemaining -= step.amountIn + step.feeAmount
                state.amountCalculated = SafeMath.subInts(
                    state.amountCalculated, step.amountOut
                )
            else:
                state.amountSpecifiedRemaining += step.amountOut
                state.amountCalculated = SafeMath.addInts(
                    state.amountCalculated, step.amountIn + step.feeAmount
                )

            ## if the protocol fee is on, calculate how much is owed, decrement feeAmount, and increment protocolFee
            if cache.feeProtocol > 0:
                delta = abs(step.feeAmount // cache.feeProtocol)
                step.feeAmount -= delta
                state.protocolFee += delta & (2**128 - 1)

            ## update global fee tracker
            if state.liquidity > 0:
                state.feeGrowthGlobalX128 += FullMath.mulDiv(
                    step.feeAmount, FixedPoint128_Q128, state.liquidity
                )
                # Addition can overflow in Solidity - mimic it
                state.feeGrowthGlobalX128 = toUint256(state.feeGrowthGlobalX128)

            ## shift tick if we reached the next price
            if state.sqrtPriceX96 == step.sqrtPriceNextX96:
                ## if the tick is initialized, run the tick transition
                ## @dev: here is where we should handle the case of an uninitialized boundary tick
                if step.initialized:
                    liquidityNet = Tick.cross(
                        self.ticks,
                        step.tickNext,
                        state.feeGrowthGlobalX128
                        if zeroForOne
                        else self.feeGrowthGlobal0X128,
                        self.feeGrowthGlobal1X128
                        if zeroForOne
                        else state.feeGrowthGlobalX128,
                    )
                    ## if we're moving leftward, we interpret liquidityNet as the opposite sign
                    ## safe because liquidityNet cannot be type(int128).min
                    if zeroForOne:
                        liquidityNet = -liquidityNet

                    state.liquidity = LiquidityMath.addDelta(
                        state.liquidity, liquidityNet
                    )

                state.tick = (step.tickNext - 1) if zeroForOne else step.tickNext
            elif state.sqrtPriceX96 != step.sqrtPriceStartX96:
                ## recompute unless we're on a lower tick boundary (i.e. already transitioned ticks), and haven't moved
                state.tick = TickMath.getTickAtSqrtRatio(state.sqrtPriceX96)

        ## End of swap loop
        ## update tick
        if state.tick != slot0Start.tick:
            self.slot0.sqrtPriceX96 = state.sqrtPriceX96
            self.slot0.tick = state.tick
        else:
            ## otherwise just update the price
            self.slot0.sqrtPriceX96 = state.sqrtPriceX96

        ## update liquidity if it changed
        if cache.liquidityStart != state.liquidity:
            self.liquidity = state.liquidity

        ## update fee growth global and, if necessary, protocol fees
        ## overflow is acceptable, protocol has to withdraw before it hits type(uint128).max fees

        if zeroForOne:
            self.feeGrowthGlobal0X128 = state.feeGrowthGlobalX128
            if state.protocolFee > 0:
                self.protocolFees.token0 += state.protocolFee
        else:
            self.feeGrowthGlobal1X128 = state.feeGrowthGlobalX128
            if state.protocolFee > 0:
                self.protocolFees.token1 += state.protocolFee

        (amount0, amount1) = (
            (amountSpecified - state.amountSpecifiedRemaining, state.amountCalculated)
            if (zeroForOne == exactInput)
            else (
                state.amountCalculated,
                amountSpecified - state.amountSpecifiedRemaining,
            )
        )
        
        tokens = self.factory.token_from_exchange[self.name]
        if zeroForOne: 
            tokens.get(self.token0).deposit(recipient, abs(amount0))
            self._swap_tokens(0, abs(amount1), recipient)            
        else: 
            tokens.get(self.token1).deposit(recipient, abs(amount1))
            self._swap_tokens(abs(amount0), 0, recipient)            

        amount0 = self._convert_to_human(amount0)
        amount1 = self._convert_to_human(amount1)
        liquidity = self._convert_to_human(state.liquidity)
        self._update_fees()
        
        return (
            recipient,
            amount0,
            amount1,
            state.sqrtPriceX96,
            liquidity,
            state.tick,
        )

    def setFeeProtocol(self, feeProtocol0, feeProtocol1):

        """ setFeeProtocol

            Set the denominator of the protocol's % share of the fees
            
            Parameters
            -----------------    
            feeProtocol0 : int
                New protocol fee for token0 of the pool      
            feeProtocol1 : int
                New protocol fee for token1 of the pool                        
        """ 
        
        checkInputTypes(uint8=(feeProtocol0, feeProtocol1))
        assert (feeProtocol0 == 0 or (feeProtocol0 >= 4 and feeProtocol0 <= 10)) and (
            feeProtocol1 == 0 or (feeProtocol1 >= 4 and feeProtocol1 <= 10)
        )

        feeProtocolOld = self.slot0.feeProtocol
        feeProtocolNew = feeProtocol0 + (feeProtocol1 << 4)
        # Health check
        checkUInt8(feeProtocolNew)
        self.slot0.feeProtocol = feeProtocolNew
        return (feeProtocolOld % 16, feeProtocolOld >> 4, feeProtocol0, feeProtocol1)

    def checkTicks(self, tickLower, tickUpper):

        """ checkTicks

            Common checks for valid tick inputs
            
            Parameters
            -----------------    
            tickLower : int
                Lower tick of the position in which to add liquidity  
            tickUpper : int
                Lower tick of the position in which to add liquidity                    
        """ 
        
        checkInputTypes(int24=(tickLower, tickUpper))
        assert tickLower < tickUpper, "UniswapV3: TLU"
        assert tickLower >= TickMath.MIN_TICK, "UniswapV3: TLM"
        assert tickUpper <= TickMath.MAX_TICK, "UniswapV3: TUM"        

    def nextTick(self, tick, lte):

        """ nextTick

            It is assumed that the keys are within [MIN_TICK , MAX_TICK], which should always be the 
            case. We don't run the risk of overshooting tickNext (out of boundaries) as long as ticks 
            (keys) have been initialized within the boundaries. However, if there is no initialized 
            tick to the left or right we will return the next boundary. Then we need to return the 
            initialized bool to indicate that we are at the boundary and it is not an initalized tick.
            
            Parameters
            -----------------    
            tick : int
                The starting tick    
            lte : int
                Whether to search for the next initialized tick to the left (less than or equal to the starting tick)
                
            Returns
            -------
            nextTick : int
                Next tick with liquidity to be used in the swap function                      
        """ 
        
        checkInputTypes(int24=(tick), bool=(lte))

        keyList = list(self.ticks.keys())

        # If tick doesn't exist in the mapping we fake it (easier than searching for nearest value). This is probably not the
        # best way, but it is a simple and intuitive way to reproduce the behaviour of the logic.
        if not self.ticks.__contains__(tick):
            keyList += [tick]
        sortedKeyList = sorted(keyList)
        indexCurrentTick = sortedKeyList.index(tick)

        if lte:
            # If the current tick is initialized (not faked), we return the current tick
            if self.ticks.__contains__(tick):
                return tick, True
            elif indexCurrentTick == 0:
                # No tick to the left
                return TickMath.MIN_TICK, False
            else:
                nextTick = sortedKeyList[indexCurrentTick - 1]
        else:

            if indexCurrentTick == len(sortedKeyList) - 1:
                # No tick to the right
                return TickMath.MAX_TICK, False
            nextTick = sortedKeyList[indexCurrentTick + 1]

        # Return tick within the boundaries
        return nextTick, True  

    def get_price(self, token):  
        
        """ get_price

            Get price of select token in the exchange pair
                
            Parameters
            -----------------
            token : ERC20
                ERC20 token                
        """          
        sqrt_P = self.slot0.sqrtPriceX96/2**96
        
        if(token.token_name == self.token0):
            if(self.reserve0 == 0):
                return None 
            else:
                return sqrt_P**2 
        elif(token.token_name == self.token1):
            if(self.reserve1 == 0):
                return None
            else:
                return 1/sqrt_P**2 
        else:
            assert False, 'UniswapV2: WRONG_INPUT_TOKEN'   
                  
    def get_liquidity(self):  
        
        """ get_liquidity

            Get liquidity of exchange pool         
        """          

        return UniV3Helper().gwei2dec(self.total_supply)        
            
    def get_reserve(self, token):  
        
        """ get_reserve

            Get reserve amount of select token in the exchange pair
                
            Parameters
            -----------------
            token : ERC20
                ERC20 token                
        """         
        
        if(token.token_name == self.token0):
            return UniV3Helper().gwei2dec(self.reserve0) 
        elif(token.token_name == self.token1):
            return UniV3Helper().gwei2dec(self.reserve1)
        else:
            assert False, 'UniswapV2: WRONG_INPUT_TOKEN'      

    def get_virtual_reserve(self, token):  
        
        """ get_virtual_reserve

            Get virtual reserve amount of select token in the exchange pair
                
            Parameters
            -----------------
            token : ERC20
                ERC20 token                
        """         
        
        sqrt_P = self.slot0.sqrtPriceX96/2**96
        liq = self.get_liquidity()
        
        if(token.token_name == self.token0):
            return liq/sqrt_P
        elif(token.token_name == self.token1):
            return liq*sqrt_P
        else:
            assert False, 'UniswapV2: WRONG_INPUT_TOKEN'           

    def _convert_to_human(self, val): 
        val = val if self.precision == UniswapExchangeData.TYPE_GWEI else UniV3Helper().gwei2dec(val)
        return val

    def _convert_to_machine(self, val): 
        val = val if self.precision == UniswapExchangeData.TYPE_GWEI else UniV3Helper().dec2gwei(val)
        return val   

    def _update_fees(self): 
        liquidity = UniV3Helper().gwei2dec(self.total_supply)
        self.collected_fee0 = liquidity*self.feeGrowthGlobal0X128/2**128
        self.collected_fee1 = liquidity*self.feeGrowthGlobal1X128/2**128
    
    def _swap(self, inputToken, amounts, recipient, sqrtPriceLimitX96):
        [amountIn, amountOut] = amounts
        exactInput = amountOut == 0
        amount = amountIn if exactInput else amountOut

        if inputToken == 'Token0':
            if exactInput:
                checkInt128(amount)
                return self.swap(recipient, True, amount, sqrtPriceLimitX96)
            else:
                checkInt128(-amount)
                return self.swap(recipient, True, -amount, sqrtPriceLimitX96)
        else:
            if exactInput:
                checkInt128(amount)
                return self.swap(recipient, False, amount, sqrtPriceLimitX96)                  
            else:
                checkInt128(-amount)
                return self.swap(recipient, False, -amount, sqrtPriceLimitX96)      
    
    def _swap_tokens(self, amountA_out, amountB_out, to_addr):
        
        """ _swap_tokens

            Remove liquidity from both coins in the pair based on lp amount
                
            Parameters
            -----------------
            amountA_out : float
                Swap amountA out
            amountB_out : float
                Swap amountB out               
            to_addr : str
                Receiving user address                   
        """         
        
        assert amountA_out > 0 or amountB_out > 0, 'UniswapV3: INSUFFICIENT_OUTPUT_AMOUNT'
        assert amountA_out < self.reserve0 and amountB_out < self.reserve1, 'UniswapV3: INSUFFICIENT_LIQUIDITY'

        tokens = self.factory.token_from_exchange[self.name]
        assert tokens.get(self.token0).token_addr != to_addr, 'UniswapV3: INVALID_TO_ADDRESS'
        assert tokens.get(self.token1).token_addr != to_addr, 'UniswapV3: INVALID_TO_ADDRESS'
        
        tokens.get(self.token0).transfer(to_addr, amountA_out)
        tokens.get(self.token1).transfer(to_addr, amountB_out)    
        
        balanceA = tokens.get(self.token0).token_total
        balanceB = tokens.get(self.token1).token_total

        amountA_in = balanceA - (self.reserve0 - amountA_out) if balanceA > self.reserve0 - amountA_out else 0
        amountB_in = balanceB - (self.reserve1 - amountB_out) if balanceB > self.reserve1 - amountB_out else 0

        assert amountA_in > 0 or amountB_in > 0, 'UniswapV3: INSUFFICIENT_INPUT_AMOUNT'
    
        self._update(balanceA, balanceB)    
    


    def _update(self, balanceA, balanceB):
        
        """ _update

            Update reserve amounts for both coins in the pair
                
            Parameters
            -----------------   
            balanceA : float
                New reserve amount of A      
            balance1 : float
                New reserve amount of B                   
        """         
        
        self.reserve0 = balanceA
        self.reserve1 = balanceB    
    
    def _modifyPosition(self, params):

        checkInputTypes(
            accounts=(params.owner),
            int24=(params.tickLower, params.tickUpper),
            int128=(params.liquidityDelta),
        )
        self.checkTicks(params.tickLower, params.tickUpper)

        # Initialize values
        amount0 = amount1 = 0

        position = self._updatePosition(
            params.owner,
            params.tickLower,
            params.tickUpper,
            params.liquidityDelta,
            self.slot0.tick,
        )

        if params.liquidityDelta != 0:
            if self.slot0.tick < params.tickLower:
                ## current tick is below the passed range; liquidity can only become in range by crossing from left to
                ## right, when we'll need _more_ token0 (it's becoming more valuable) so user must provide it
                amount0 = SqrtPriceMath.getAmount0DeltaHelper(
                    TickMath.getSqrtRatioAtTick(params.tickLower),
                    TickMath.getSqrtRatioAtTick(params.tickUpper),
                    params.liquidityDelta,
                )
            elif self.slot0.tick < params.tickUpper:
                ## current tick is inside the passed range
                amount0 = SqrtPriceMath.getAmount0DeltaHelper(
                    self.slot0.sqrtPriceX96,
                    TickMath.getSqrtRatioAtTick(params.tickUpper),
                    params.liquidityDelta,
                )
                amount1 = SqrtPriceMath.getAmount1DeltaHelper(
                    TickMath.getSqrtRatioAtTick(params.tickLower),
                    self.slot0.sqrtPriceX96,
                    params.liquidityDelta,
                )
                self.total_supply = LiquidityMath.addDelta(
                    self.total_supply, params.liquidityDelta
                )
                self.last_liquidity_deposit = self._convert_to_human(params.liquidityDelta)
            else:
                ## current tick is above the passed range; liquidity can only become in range by crossing from right to
                ## left, when we'll need _more_ token1 (it's becoming more valuable) so user must provide it
                amount1 = SqrtPriceMath.getAmount1DeltaHelper(
                    TickMath.getSqrtRatioAtTick(params.tickLower),
                    TickMath.getSqrtRatioAtTick(params.tickUpper),
                    params.liquidityDelta,
                )

        return (position, amount0, amount1)  
    
    def _updatePosition(self, owner, tickLower, tickUpper, liquidityDelta, tick):
        checkInputTypes(
            accounts=(owner),
            int24=(tickLower, tickUpper, tick),
            int128=(liquidityDelta),
        )
        # This will create a position if it doesn't exist

        
        position = Position.get(self.positions, owner, tickLower, tickUpper)

        # Initialize values
        flippedLower = flippedUpper = False

        ## if we need to update the ticks, do it
        if liquidityDelta != 0:
            flippedLower = Tick.update(
                self.ticks,
                tickLower,
                tick,
                liquidityDelta,
                self.feeGrowthGlobal0X128,
                self.feeGrowthGlobal1X128,
                False,
                self.maxLiquidityPerTick,
            )
            flippedUpper = Tick.update(
                self.ticks,
                tickUpper,
                tick,
                liquidityDelta,
                self.feeGrowthGlobal0X128,
                self.feeGrowthGlobal1X128,
                True,
                self.maxLiquidityPerTick,
            )

        if flippedLower:
            assert tickLower % self.tickSpacing == 0  ## ensure that the tick is spaced
        if flippedUpper:
            assert tickUpper % self.tickSpacing == 0  ## ensure that the tick is spaced

        (feeGrowthInside0X128, feeGrowthInside1X128) = Tick.getFeeGrowthInside(
            self.ticks,
            tickLower,
            tickUpper,
            tick,
            self.feeGrowthGlobal0X128,
            self.feeGrowthGlobal1X128,
        )

        Position.update(
            position, liquidityDelta, feeGrowthInside0X128, feeGrowthInside1X128
        )

        ## clear any tick data that is no longer needed
        if liquidityDelta < 0:
            if flippedLower:
                Tick.clear(self.ticks, tickLower)
            if flippedUpper:
                Tick.clear(self.ticks, tickUpper)
        return position    
    
