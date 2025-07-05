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

import requests

from ..data import Chain0x

class API0x():
    
    """ 0x API class which calls Chain0x data class for data
    
        Parameters
        -----------------
        chain : str
            API endpoint url indicating which chain to make API call (eg, api.0x.org)
        api_key : str
            0x API key (see dashboard.0x.org for more info)  
    
    """      

    def __init__(self, chain: str = None, api_key: str = None) -> None:
        self.chain = Chain0x.ETHEREUM if chain == None else chain
        self.api_key = Chain0x().get_api_key() if api_key == None else api_key
        
    def apply(self, sell_tkn: str = None, buy_tkn: str = None, sell_amt: str = None):
        
        """ apply

            Apply call to 0x API 
            
            Parameters
            -----------------
            buy_token : str
                Buy token contract address (ie, pulled from Chain0x data class)
            sell_token : str
                Buy token contract address (ie, pulled from Chain0x data class)  
            sell_amt : str
                0x API requirement (set to 10000000 by default)                
                
            Returns
            -----------------
            0x api data : dictionary
                JSON structured 0x api call data                 
        """         
        
        sell_tkn = Chain0x().get_sell_token() if sell_tkn == None else sell_tkn
        buy_tkn = Chain0x().get_buy_token() if buy_tkn == None else buy_tkn     
        sell_amt = Chain0x().get_api_sell_amount() if sell_amt == None else sell_amt 
        
        url = f'https://{self.chain}/swap/v1/quote?sellToken={sell_tkn}&buyToken={buy_tkn}&sellAmount={sell_amt}'
        
        headers = {
                'Content-type': 'application/json',
                '0x-api-key': self.api_key
            }

        search_response = requests.get(url, headers=headers).json()
        return search_response if 'price' in search_response else {}
        