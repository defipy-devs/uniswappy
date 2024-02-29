# Copyright [2024] [Ian Moore]
# Distributed under the MIT License (license terms are at http://opensource.org/licenses/MIT).
# Email: defipy.devs@gmail.com

from dataclasses import dataclass
from ...math.model import TokenDeltaModel

DEFAULT_CHAIN_NM = "api.0x.org"
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
    
    """ 
        Data class handling all data for BUIDL week ETHDenver Simulator application
    """    
    
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
    
    # Set defaults
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
        
        """ get_api_key

            Get 0x API key
                
            Returns
            -----------------
            api_key : str
                0x API key                 
        """          
        
        return self.api_key
    
    def get_api_sell_amount(self) -> str:
        
        """ get_api_sell_amount

            Get 0x API sell amount setting
                
            Returns
            -----------------
            api_sell_amount : str
                0x API sell amount setting                
        """          
        
        return self.api_sell_amount    

    def get_chain_name(self) -> str:
        
        """ get_chain_name

            Get URL name for 0x api
                
            Returns
            -----------------
            select_chain_name : str
                URL name for 0x api             
        """            

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
        
        """ get_buy_token

            Get buy token contract address for 0x api
                
            Returns
            -----------------
            select_buy_token : str
                Buy token contract address for 0x api           
        """         

        match self.buy_tkn_nm:
            case self.WETH if self.chain_nm in self.ETHEREUM:
                select_buy_token = '0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2'
            case self.LINK if self.chain_nm in self.ETHEREUM:
                select_buy_token = '0x514910771AF9Ca656af840dff83E8264EcF986CA'
            case self.UNI if self.chain_nm in self.ETHEREUM:
                select_buy_token = '0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984'
            case self.WBTC if self.chain_nm in self.ETHEREUM:
                select_buy_token = '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599'
            case self.BNB if self.chain_nm in self.ETHEREUM:
                select_buy_token = '0xB8c77482e45F1F44dE1745F52C74426C631bDD52'
                
            case self.WETH if self.chain_nm in self.POLYGON:
                select_buy_token = '0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619'
            case self.LINK if self.chain_nm in self.POLYGON:
                select_buy_token = '0xb0897686c545045aFc77CF20eC7A532E3120E0F1'
            case self.UNI if self.chain_nm in self.POLYGON:
                select_buy_token = '0xb33EaAd8d922B1083446DC23f610c2567fB5180f'
            case self.WBTC if self.chain_nm in self.POLYGON:
                select_buy_token = '0x1BFD67037B42Cf73acF2047067bd4F2C47D9BfD6'
            case self.BNB if self.chain_nm in self.POLYGON:
                select_buy_token = '0x3BA4c387f786bFEE076A58914F5Bd38d668B42c3'  
                
            case self.WETH if self.chain_nm in self.AVALANCHE:
                select_buy_token = '0x49D5c2BdFfac6CE2BFdB6640F4F80f226bc10bAB'
            case self.LINK if self.chain_nm in self.AVALANCHE:
                select_buy_token = '0x5947BB275c521040051D82396192181b413227A3'
            case self.UNI if self.chain_nm in self.AVALANCHE:
                select_buy_token = '0x8eBAf22B6F053dFFeaf46f4Dd9eFA95D89ba8580'
            case self.WBTC if self.chain_nm in self.AVALANCHE:
                select_buy_token = '0x50b7545627a5162F82A992c33b87aDc75187B218'
            case self.BNB if self.chain_nm in self.AVALANCHE:
                select_buy_token = '0x264c1383EA520f73dd837F915ef3a732e204a493'                   
                
            case self.WETH if self.chain_nm in self.OPTIMISM:
                select_buy_token = '0xe50fA9b3c56FfB159cB0FCA61F5c9D750e8128c8'
            case self.LINK if self.chain_nm in self.OPTIMISM:
                select_buy_token = '0x350a791Bfc2C21F9Ed5d10980Dad2e2638ffa7f6'
            case self.WBTC if self.chain_nm in self.OPTIMISM:
                select_buy_token = '0x68f180fcCe6836688e9084f035309E29Bf0A2095'                 

        return select_buy_token   
    
    def get_sell_token(self) -> str:
        
        """ get_buy_token

            Get sell token contract address for 0x api
                
            Returns
            -----------------
            select_buy_token : str
                Sell token contract address for 0x api           
        """           
        
        match self.sell_tkn_nm:
            case self.USDC if self.chain_nm in self.ETHEREUM:
                select_sell_token = '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48'
            case self.USDT if self.chain_nm in self.ETHEREUM:
                select_sell_token = '0xdAC17F958D2ee523a2206206994597C13D831ec7'
            case self.DAI if self.chain_nm in self.ETHEREUM:
                select_sell_token = '0x6B175474E89094C44Da98b954EedeAC495271d0F'
                
            case self.USDC if self.chain_nm in self.POLYGON:
                select_sell_token = '0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359'
            case self.USDT if self.chain_nm in self.POLYGON:
                select_sell_token = '0xc2132D05D31c914a87C6611C10748AEb04B58e8F'
            case self.DAI if self.chain_nm in self.POLYGON:
                select_sell_token = '0x8f3Cf7ad23Cd3CaDbD9735AFf958023239c6A063'    
                
            case self.USDC if self.chain_nm in self.OPTIMISM:
                select_sell_token = '0x0b2C639c533813f4Aa9D7837CAf62653d097Ff85'
            case self.USDT if self.chain_nm in self.OPTIMISM:
                select_sell_token = '0x9702230A8Ea53601f5cD2dc00fDBc13d4dF4A8c7'
            case self.DAI if self.chain_nm in self.OPTIMISM:
                select_sell_token = '0x94b008aA00579c1307B0EF2c499aD98a8ce58e58'      
                
            case self.USDC if self.chain_nm in self.AVALANCHE:
                select_sell_token = '0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E'
            case self.USDT if self.chain_nm in self.AVALANCHE:
                select_sell_token = '0x9702230A8Ea53601f5cD2dc00fDBc13d4dF4A8c7'
            case self.DAI if self.chain_nm in self.AVALANCHE:
                select_sell_token = '0xbA7dEebBFC5fA1100Fb055a87773e1E99Cd3507a'                  

                
        return select_sell_token      
    
    def get_buy_init_amt(self) -> float:
        
        """ get_buy_init_amt

            Get x init amount for pool initialization
                
            Returns
            -----------------
            select_buy_init_amt : int
                x init amount for pool initialization         
        """           

        match self.buy_tkn_nm:
            case self.WETH:
                select_buy_init_amt = 10000
            case self.LINK:
                select_buy_init_amt = 1000000
            case self.UNI:
                select_buy_init_amt = 1000000
            case self.WBTC:
                select_buy_init_amt = 1000
            case self.BNB:
                select_buy_init_amt = 100000

        return select_buy_init_amt 
    
    def get_td_model(self) -> TokenDeltaModel:
        
        """ get_td_model

            Get token delta model which is the non-deterministic model for incoming swap amounts; set 
            to Gamma distribution with paramaters set to scale = 1 and shape = 1 (by default)
                
            Returns
            -----------------
            td_model : TokenDeltaModel
                Token delta model      
        """             
        
        buy_init_amt = self.get_buy_init_amt()
        return TokenDeltaModel(max_trade = self.max_trade_percent*buy_init_amt, 
                                    shape = DEFAULT_GAMMA_SHAPE, # Gamma Dist. shape  
                                    scale = DEFAULT_GAMMA_SCALE) # Gamma Dist. scale     
    
    
             
                
                
                
