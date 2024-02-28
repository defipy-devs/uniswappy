# Copyright [2024] [Ian Moore]
# Distributed under the MIT License (license terms are at http://opensource.org/licenses/MIT).
# Email: defipy.devs@gmail.com

import requests

from ..data import Chain0x

class API0x():
    
    """ API0x
    """      

    def __init__(self, chain: str = None, api_key: str = None) -> None:
        self.chain = Chain0x.ETHEREUM if chain == None else chain
        self.api_key = Chain0x().get_api_key() if api_key == None else api_key
        
    def apply(self, sell_tkn: str = None, buy_tkn: str = None, sell_amt: str = None):
        
        sell_tkn = Chain0x().get_sell_token() if sell_tkn == None else sell_tkn
        buy_tkn = Chain0x().get_buy_token() if buy_tkn == None else buy_tkn     
        sell_amt = Chain0x().get_api_sell_amount() if sell_amt == None else sell_amt 
        
        url = f'https://{self.chain}/swap/v1/quote?sellToken={sell_tkn}&buyToken={buy_tkn}&sellAmount={sell_amt}'
        
        headers = {
                'Content-type': 'application/json',
                '0x-api-key': self.api_key
            }

        search_response = requests.get(url, headers=headers)
        return search_response.json()
        