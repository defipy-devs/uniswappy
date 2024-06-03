# Copyright [2023] [Ian Moore]
# Distributed under the MIT License (license terms are at http://opensource.org/licenses/MIT).
# Email: defipy.devs@gmail.com

from ...erc import ERC20
from .Vault import Vault 
from ..index import RebaseIndexToken

INDEX_TOKEN = 'INDEX'

class IndexVault(Vault):
    
    """ Vault of index tokens

        Parameters
        ----------
        token_name : str
            Token name 
        token_addr : str
            Token address  
        lp_providers : dictionary
            Map of LP providers to their respective holdings
        lp_tokens : dictionary
            Map of LPs to their ERC20 tokens and total amounts
        index_tokens : dictionary
            Map of index tokens to their ERC20 tokens and total amounts            
    """  
    
    
    def __init__(self, name: str, addr: str) -> None:
        self.token_name = name
        self.token_addr = addr 
        self.lp_providers = {}
        self.lp_tokens = {}
        self.index_tokens = {}
      
    def rebase_index_tkn(self, lp_token, token = None, lwr_tick = None, upr_tick = None):
        
        """ rebase_index_tkn

            Mint index token from LP and specified token from pair
                
            Parameters
            -------
            lp_token : DAOSYSERC20
                LP token 
            token : ERC20
                specified token from pair                                 
        """         
        
        if(token != None):
            self.__rebase_index_tkn(lp_token, token, lwr_tick, upr_tick)
            self.update_accounts(lp_token, token, lwr_tick, upr_tick)
        else:  
            tokens = lp_token.factory.exchange_to_tokens[lp_token.name]
            self.__rebase_index_tkn(lp_token, tokens[lp_token.token0], lwr_tick, upr_tick)
            self.__rebase_index_tkn(lp_token, tokens[lp_token.token1], lwr_tick, upr_tick)
            self.update_accounts(lp_token, tokens[lp_token.token0])
            self.update_accounts(lp_token, tokens[lp_token.token1])  
            self.update_index_tkn(lp_token, token)    
        
    def deposit_lp_tkn(self, _to, lp_tkn, amt):
        
        """ deposit_lp_tkn

            Deposit specified amount of LP token to a user account
                
            Parameters
            -------
            _to : str
                account holder            
            token : DAOSYSERC20
                LP token 
            amt : float
                amount of LP to be deposited                                
        """          
        
        if self.__chk_tkn(lp_tkn):
            self.lp_tokens[lp_tkn.token_name]['total_amount'] += amt
            self.lp_tokens[lp_tkn.token_name]['last_deposit'] = amt
        else:
            self.__init_tkn(lp_tkn, amt)
            
        if self.__chk_nm(_to):
            if self.__chk_tkn_nm(_to, lp_tkn):
                self.lp_providers[_to][lp_tkn.token_name]['amount'] += amt
            else:
                self.lp_providers[_to][lp_tkn.token_name] = {}
                self.lp_providers[_to][lp_tkn.token_name]['amount'] = amt                
        else:
            self.lp_providers[_to] = {}
            self.lp_providers[_to][lp_tkn.token_name] = {}
            self.lp_providers[_to][lp_tkn.token_name]['amount'] = amt    
            

    def remove_lp_tkn(self, _to, lp_tkn, amt):   
        
        """ remove_lp_tkn

            Remove specified amount of LP token from a user account
                
            Parameters
            -------
            _to : str
                account holder            
            lp_tkn : DAOSYSERC20
                LP token 
            amt : float
                amount of LP to be deposited                                
        """       
        
        removed = True
        
        if self.__chk_tkn_nm(_to, lp_tkn):
            if(amt <= self.lp_providers[_to][lp_tkn.token_name]['amount']):
                self.lp_providers[_to][lp_tkn.token_name]['amount'] -= amt
                self.lp_tokens[lp_tkn.token_name]['total_amount'] -= amt
                self.lp_tokens[lp_tkn.token_name]['last_deposit'] = -amt
            else:
                print('ERROR: not enough amount in {} account'.format(_to))
                removed = False
        else:
            print('ERROR: token not in vault')
            removed = False
            
        return removed    
            
    def burn_lp_token(self, _from, lp_tkn, token, lp_amt):
        
        """ burn_lp_token

            Burn specified amount of LP token from a user account referencing its parent pairing token
                
            Parameters
            -------
            _from : str
                account holder            
            lp_tkn : DAOSYSERC20
                LP token
            token : ERC20
                parent pairing token                
            lp_amt : float
                amount of LP to be burned
                
            Returns
            -------
            res : dictionary
                map of pair tokens and their respective amounts                 
        """          
        
        res = {}
        if(self.check_token_account(token, _from)):
            removed = self.remove_lp_tkn(_from, lp_tkn, lp_amt)
            if(removed):
                amount0 = lp_amt*lp_tkn.reserve0/lp_tkn.total_supply
                amount1 = lp_amt*lp_tkn.reserve1/lp_tkn.total_supply              
                lp_tkn.remove_liquidity(_from, lp_amt, amount0, amount1)
                self.rebase_index_tkn(lp_tkn, token)
                self.update_accounts(lp_tkn, token)            
            
        return {lp_tkn.token0: amount0, lp_tkn.token1: amount1} if removed else res

            
    def get_tkn_pair_amount(self, lp_tkn, token, liq, lwr_tick = None, upr_tick = None):
        
        """ get_tkn_pair_amount

            Get amount of specified token from LP pairing 
                
            Parameters
            -------         
            lp_tkn : DAOSYSERC20
                LP token
            token : ERC20
                parent pairing token                
            liq : float
                amount of LP to be burned   
                
            Returns
            -------
            amt : float
                amount of specified token from pairing                 
        """          
        amt = RebaseIndexToken().apply(lp_tkn, token, liq, lwr_tick, upr_tick)
        return amt
    
    def get_token_type(self, token):
        
        """ get_token_type

            Get token type (ie, LP, ERC20, Index)
                
            Parameters
            -------         
            token : ERC20
                parent pairing token                
                
            Returns
            -------
            type : str
                token type                  
        """         
        
        return token.__class__.__name__   
    
    def update_accounts(self, lp_tkn, tkn, lwr_tick, upr_tick): 

        """ update_accounts

            Update specified token across all accounts
                
            Parameters
            -------         
            lp_tkn : DAOSYSERC20
                parent pairing token                
            tkn : ERC20
                parent pairing token

            Returns
            -------
            type : str
                token type                  
        """         
        
        index_tokens = {}
        exchange = lp_tkn.token_name
        index_tokens[tkn.token_name] = 'i'+tkn.token_name
        
        self.update_index_tkn(lp_tkn, tkn, lwr_tick, upr_tick)
        
        new_total = 0
        tkn_nm = tkn.token_name
        for account in self.lp_providers:
            amt = self.lp_providers[account][exchange]['amount']
            exch_tkn = lp_tkn.factory.token_from_exchange[lp_tkn.name][tkn_nm]
            self.lp_providers[account][index_tokens[tkn_nm]] = {}
            self.lp_providers[account][index_tokens[tkn_nm]]['amount'] = self.get_tkn_pair_amount(lp_tkn, exch_tkn, amt, lwr_tick, upr_tick)             
                  
    def update_account(self, lp_tkn, tkn, _from): 
        
        """ update_accounts

            Update specified token from specified account
                
            Parameters
            -------         
            lp_tkn : DAOSYSERC20
                parent pairing token                
            tkn : ERC20
                parent pairing token
            _from : str
                account holder                                
        """         

        index_tokens = {}
        exchange = lp_tkn.token_name
        index_tokens[tkn.token_name] = 'i'+tkn.token_name

        for tkn_nm in index_tokens.keys():
            amt = self.lp_providers[_from][exchange]['amount']
            exch_tkn = lp_tkn.factory.token_from_exchange[lp_tkn.name][tkn_nm]
            self.lp_providers[_from][index_tokens[tkn_nm]] = {}
            self.lp_providers[_from][index_tokens[tkn_nm]]['amount'] = self.get_tkn_pair_amount(lp_tkn, exch_tkn, amt)  
            
        if(self.lp_providers[_from][lp_tkn.token_name]['amount'] == 0):
            self.lp_providers.pop(_from)            
                
    def get_account(self, _from):
        
        """ get_account

            Get LP information from account holder
                
            Parameters
            -------         
            _from : str
                account holder                

            Returns
            -------
            type : dictionary
                LP account with amount of holdings                
        """           
        
        return self.lp_providers[_from]
    
    
    def check_token_account(self, token, _from):
        
        """ check_token_account

            Check if account holder is holding specified token
                
            Parameters
            -------  
            token : ERC20
                specified query token             
            _from : str
                account holder                

            Returns
            -------
            is_tkn_account : boolean
                boolean if account exists for specified token                
        """             
        
        is_tkn_account = False
        for tkn_nm in self.lp_providers[_from].keys():
            is_tkn_account = True if tkn_nm == 'i'+token.token_name and not is_tkn_account else is_tkn_account
        return is_tkn_account    
    
    def __rebase_index_tkn(self, lp_token, token, lwr_tick, upr_tick):
        
        """ __rebase_index_tkn

            Mint index token based on the amount of LP in account
                
            Parameters
            -------  
            lp_token : ERC20
                specified parent token             
            token : DAOSYSERC20
                LP token                              
        """          
        
        mint_tkn_name = 'i'+token.token_name
        liq = self.lp_tokens[lp_token.token_name]['total_amount']
        last_liq = self.lp_tokens[lp_token.token_name]['last_deposit']
        delta_amt = self.get_tkn_pair_amount(lp_token, token, last_liq, lwr_tick, upr_tick)
        amt = self.get_tkn_pair_amount(lp_token, token, liq, lwr_tick, upr_tick)
        tkn = ERC20(mint_tkn_name, None)
        tkn.deposit(None, amt) 
        
        if mint_tkn_name not in self.index_tokens:    
            self.index_tokens[mint_tkn_name] = {}
            self.index_tokens[mint_tkn_name]['token'] = tkn 
            self.index_tokens[mint_tkn_name]['total'] = self.get_tkn_pair_amount(lp_token, token, liq, lwr_tick, upr_tick) 
            self.index_tokens[mint_tkn_name]['total_lp'] = liq
            self.index_tokens[mint_tkn_name]['last_deposit'] = tkn.token_total
            self.index_tokens[mint_tkn_name]['last_lp_deposit'] = amt
            self.index_tokens[mint_tkn_name]['parent_token'] = token.token_name
            self.index_tokens[mint_tkn_name]['exchange'] = lp_token.token_name
        else:          
            prev_total = self.index_tokens[mint_tkn_name]['total']
            self.index_tokens[mint_tkn_name]['token'] = tkn 
            self.index_tokens[mint_tkn_name]['total'] = self.get_tkn_pair_amount(lp_token, token, liq, lwr_tick, upr_tick) 
            self.index_tokens[mint_tkn_name]['total_lp'] = liq
            self.index_tokens[mint_tkn_name]['last_deposit'] = delta_amt
            self.index_tokens[mint_tkn_name]['last_lp_deposit'] = last_liq
               
            
    def update_index_tkn(self, lp_token, token, lwr_tick, upr_tick):   
        mint_tkn_name = 'i'+token.token_name
        if mint_tkn_name in self.index_tokens:  
            liq = self.lp_tokens[lp_token.token_name]['total_amount']
            last_liq = self.lp_tokens[lp_token.token_name]['last_deposit']
            self.index_tokens[mint_tkn_name]['total'] = self.get_tkn_pair_amount(lp_token, token, liq, lwr_tick, upr_tick)  
            self.index_tokens[mint_tkn_name]['last_deposit'] = self.get_tkn_pair_amount(lp_token, token, last_liq, lwr_tick, upr_tick)  
            self.index_tokens[mint_tkn_name]['total_lp'] = liq  
            self.index_tokens[mint_tkn_name]['last_lp_deposit'] = last_liq             
            
    def __chk_nm(self, _to):
        
        """ __chk_nm

            Determine if account exisits under holder name 
                
            Parameters
            -------  
            _to : str
                account holder to check 
                
            Returns
            -------
            is_account : boolean
                boolean of whether account exisits                   
        """          
        
        return True if _to in self.lp_providers else False

    def __init_tkn(self, token, amt):
        
        """ __init_tkn

            Initialize token at specified amount 
                
            Parameters
            -------  
            token : ERC20
                specified token   
            amt : float
                amount of new inititalized token                 
        """          
        
        self.lp_tokens[token.token_name] = {}
        self.lp_tokens[token.token_name]['token'] = token 
        self.lp_tokens[token.token_name]['total_amount'] = amt
        self.lp_tokens[token.token_name]['last_deposit'] = amt
     
    def __chk_tkn(self, lp_token):
        
        """ __chk_tkn

            Determine if LP token exisits
                
            Parameters
            -------  
            lp_token : DAOSYSERC20
                LP token to check 
                
            Returns
            -------
            is_token : boolean
                boolean of whether LP token exisits                   
        """         
        
        return True if lp_token.token_name in self.lp_tokens else False

    def __chk_tkn_nm(self, _to, lp_token):
        
        """ __chk_tkn_nm

            Determine if LP token exisits for specified account 
                
            Parameters
            -------  
            _to : str
                account name             
            lp_token : DAOSYSERC20
                LP token to check 
                
            Returns
            -------
            is_chk_nm : boolean
                boolean of whether LP token exisits for specified account                  
        """          
        
        if self.__chk_nm(_to): 
            return True if lp_token.token_name in self.lp_providers[_to] else False
        else:
            return False            
        