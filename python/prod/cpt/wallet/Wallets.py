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

class Wallets():
    
    def __init__(self):
        self.accounts = {}
        self.tokens = {}
        
    def update(self, _to, tkn, amt):
        
        if(amt >= 0):
            self.deposit(_to, tkn, amt)
        else:
            self.remove(_to, tkn, abs(amt))
        
    def deposit(self, _to, tkn, amt):
             
        if self.__chk_tkn(tkn):
            self.tokens[tkn.token_name]['total_amount'] += amt
            self.tokens[tkn.token_name]['last_deposit'] = amt
        else:
            self.__init_tkn(tkn, amt)
            
        if self.__chk_nm(_to):
            if self.__chk_tkn_nm(_to, tkn):
                self.accounts[_to][tkn.token_name]['amount'] += amt
            else:
                self.accounts[_to][tkn.token_name] = {}
                self.accounts[_to][tkn.token_name]['amount'] = amt                
        else:
            self.accounts[_to] = {}
            self.accounts[_to][tkn.token_name] = {}
            self.accounts[_to][tkn.token_name]['amount'] = amt
            

    def remove(self, _to, tkn, amt):   
              
        removed = True
        
        if self.__chk_tkn_nm(_to, tkn):
            if(amt <= self.accounts[_to][tkn.token_name]['amount']):
                self.accounts[_to][tkn.token_name]['amount'] -= amt
                self.tokens[tkn.token_name]['total_amount'] -= amt
                self.tokens[tkn.token_name]['last_deposit'] = -amt
            else:
                print('WALLET ERROR: not enough amount in {} account'.format(_to))
                removed = False
        else:
            print('WALLET ERROR: token not in vault')
            removed = False
            
        return removed  
    
    def get_token_amount(self, tkn):
        return self.tokens[tkn.token_name]['total_amount']
    
    def __init_tkn(self, token, amt):        
        self.tokens[token.token_name] = {}
        self.tokens[token.token_name]['token'] = token 
        self.tokens[token.token_name]['total_amount'] = amt
        self.tokens[token.token_name]['last_deposit'] = amt 
        
    def __chk_tkn(self, token):        
        return True if token.token_name in self.tokens else False  
    
    def __chk_tkn_nm(self, _to, token):        
        if self.__chk_nm(_to): 
            return True if token.token_name in self.accounts[_to] else False
        else:
            return False    
        
    def __chk_nm(self, _to):        
        return True if _to in self.accounts else False        