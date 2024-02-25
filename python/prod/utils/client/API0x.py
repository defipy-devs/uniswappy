# Copyright [2024] [Ian Moore]
# Distributed under the MIT License (license terms are at http://opensource.org/licenses/MIT).
# Email: defipy.devs@gmail.com

import requests

from ..data import Chain0x

CHAIN = 'api.0x.org'
SELL_AMOUNT = '10000000'
SELL_TOKEN = '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48'
BUY_TOKEN = '0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2'
API_KEY = "6cbf2275-5cee-4659-8d67-5491399a9c5e"

class API0x():
    
    """ API0x
    """      

    def __init__(self, chain: str = None, api_key: str = None) -> None:
        self.chain = CHAIN if chain == None else chain
        self.api_key = API_KEY if api_key == None else api_key
        
    def apply(self, sell_tkn: str = None, buy_tkn: str = None, sell_amt: str = None):
        
        sell_tkn = SELL_TOKEN if sell_tkn == None else sell_tkn
        buy_tkn = BUY_TOKEN if buy_tkn == None else buy_tkn     
        sell_amt = SELL_AMOUNT if sell_amt == None else sell_amt 
        
        url = f'https://{self.chain}/swap/v1/quote?sellToken={sell_tkn}&buyToken={buy_tkn}&sellAmount={sell_amt}'
        
        headers = {
                'Content-type': 'application/json',
                '0x-api-key': self.api_key
            }

        search_response = requests.get(url, headers=headers)
        return search_response.json()
        