# Copyright [2024] [Ian Moore]
# Distributed under the MIT License (license terms are at http://opensource.org/licenses/MIT).
# Email: defipy.devs@gmail.com

from dataclasses import dataclass
from dataclasses import dataclass, field
from ...math.model import TokenDeltaModel

DEFAULT_CHAIN_NM = "ETHEREUM"
DEFAULT_BUY_TKN_NM = "WETH"
DEFAULT_BUY_TOKEN = '0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2'
DEFAULT_SELL_TKN_NM = "USDC"
DEFAULT_SELL_TOKEN = '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48'
DEFAULT_INIT_AMT = 1000
DEFAULT_TIME_WINDOW = 0.25
DEFAULT_TRADE_BIAS = 0.5
DEFAULT_INIT_INVESTMENT = 1
DEFAULT_GAMMA_SHAPE = 1
DEFAULT_GAMMA_SCALE = 1
DEFAULT_MAX_TRADE_PERCENT = 0.003
DEFAULT_API_KEY = "6cbf2275-5cee-4659-8d67-5491399a9c5e"
DEFAULT_API_SELL_AMOUNT = '10000000'

@dataclass
class Chain0x:
    
    # API Endpoints for Chains
    ETHEREUM = 'api.0x.org'
    ARBITRUM = 'arbitrum.api.0x.org'
    AVALANCHE = 'avalanche.api.0x.org'
    BASE = 'base.api.0x.org'
    BINANCE = 'bsc.api.0x.org'
    CELO = 'celo.api.0x.org'
    FANTOM = 'fantom.api.0x.org'
    OPTIMISM = 'optimism.api.0x.org'
    POLYGON = 'polygon.api.0x.org'    
    
    # Buy tokens
    WETH = "WETH"
    LINK = "LINK"
    UNI = "UNI"
    WBTC = "WBTC"
    BNB = "BNB"  
    
    # Sell tokens
    USDC = "USDC"
    USDT = "USDT"
    DAI = "DAI"

    chain_nm: str = DEFAULT_CHAIN_NM
    buy_tkn_nm: str = DEFAULT_BUY_TKN_NM
    sell_tkn_nm: str = DEFAULT_SELL_TKN_NM
    max_trade_percent: float = DEFAULT_MAX_TRADE_PERCENT
    time_window: float = DEFAULT_TIME_WINDOW
    trade_bias: float = DEFAULT_TRADE_BIAS 
    init_investment: float = DEFAULT_INIT_INVESTMENT 
    api_key: float = DEFAULT_API_KEY
    api_sell_amount: str = DEFAULT_API_SELL_AMOUNT
    
    def get_api_key(self) -> str:
        return self.api_key
    
    def get_api_sell_amount(self) -> str:
        return self.api_sell_amount    

    def get_chain_name(self) -> str:

        match self.chain_nm:
            case self.ETHEREUM:
                select_chain_name = 'api.0x.org'
            case self.ARBITRUM:
                select_chain_name = 'arbitrum.api.0x.org'
            case self.AVALANCHE:
                select_chain_name = 'avalanche.api.0x.org'
            case self.BASE:
                select_chain_name = 'base.api.0x.org'
            case self.BINANCE:
                select_chain_name = 'bsc.api.0x.org'
            case self.CELO:
                select_chain_name = 'celo.api.0x.org'
            case self.FANTOM:
                select_chain_name = 'fantom.api.0x.org'
            case self.OPTIMISM:
                select_chain_name = 'optimism.api.0x.org'
            case self.POLYGON:
                select_chain_name = 'polygon.api.0x.org'    

        return select_chain_name   
    
    def get_buy_token(self) -> str:

        match self.buy_tkn_nm:
            case self.WETH:
                select_buy_token = '0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2'
            case self.LINK:
                select_buy_token = '0x514910771AF9Ca656af840dff83E8264EcF986CA'
            case self.UNI:
                select_buy_token = '0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984'
            case self.WBTC:
                select_buy_token = '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599'
            case self.BNB:
                select_buy_token = '0xB8c77482e45F1F44dE1745F52C74426C631bDD52'

        return select_buy_token   
    
    def get_sell_token(self) -> str:

        match self.sell_tkn_nm:
            case self.USDC:
                select_sell_token = '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48'
            case self.USDT:
                select_sell_token = '0xdAC17F958D2ee523a2206206994597C13D831ec7'
            case self.DAI:
                select_sell_token = '0x6B175474E89094C44Da98b954EedeAC495271d0F'

        return select_sell_token      
    
    def get_buy_init_amt(self) -> float:

        match self.buy_tkn_nm:
            case self.WETH:
                select_buy_init_amt = 1000
            case self.LINK:
                select_buy_init_amt = 100000
            case self.UNI:
                select_buy_init_amt = 100000
            case self.WBTC:
                select_buy_init_amt = 100
            case self.BNB:
                select_buy_init_amt = 10000

        return select_buy_init_amt 
    
    def get_td_model(self) -> TokenDeltaModel:
        buy_init_amt = self.get_buy_init_amt()
        return TokenDeltaModel(max_trade = self.max_trade_percent*buy_init_amt, 
                                    shape = DEFAULT_GAMMA_SHAPE, # Gamma Dist. shape  
                                    scale = DEFAULT_GAMMA_SCALE) # Gamma Dist. scale     
    
    
             
                
                
                
