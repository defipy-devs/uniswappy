# swap_revenue_test.py
# Author: Ian Moore ( imoore@syscoin.org )
# Date: Aug 2023

TEST_PATH = "python/test/defi/process/swap"

import os
import sys
import unittest   
sys.path.append(os.getcwd().replace(TEST_PATH,""))

from python.prod.cpt.factory import Factory
from python.prod.cpt.exchg import Exchange
from python.prod.cpt.erc import ERC20
from python.prod.cpt.erc import DOASYSERC20
from python.prod.cpt.erc import IndexERC20
from python.prod.cpt.vault import IndexVault
from python.prod.defi.process.liquidity import AddLiquidity
from python.prod.defi.process.mint import SwapIndexMint
from python.prod.defi.process.liquidity import AddLiquidity
from python.prod.defi.process.liquidity import RemoveLiquidity
from python.prod.defi.process.swap import WithdrawSwap
from python.prod.defi.process.deposit import SwapDeposit
from python.prod.cpt.index import RebaseIndexToken
from python.prod.cpt.quote import LPQuote
from python.prod.cpt.quote import IndexTokenQuote
import numpy as np 

USER_NM = 'user0'
DAI_AMT = 10000
SYS_AMT = 100000

class Test_SwapRevenue(unittest.TestCase):
   
    def setup_lp(self, factory, tkn1, tkn2, lp_nm):
        return factory.create_exchange(tkn1, tkn2, symbol=lp_nm, address="0x012")
    
    def add_liquidity1(self, tkn_x, itkn_y, lp_in, iVault, amt_in):
        parent_lp = lp_in.factory.parent_lp
        parent_tkn = itkn_y.parent_tkn
        itkn_nm = itkn_y.token_name
        SwapIndexMint(iVault).apply(parent_lp, parent_tkn, USER_NM, amt_in)
        mint_itkn_deposit = iVault.index_tokens[itkn_nm]['last_lp_deposit']
        tkn_amount1 = LPQuote(False).get_amount_from_lp(parent_lp, tkn_x, mint_itkn_deposit) 
        price_itkn = tkn_amount1/mint_itkn_deposit 
        AddLiquidity(price_itkn).apply(lp_in, itkn_y, USER_NM, mint_itkn_deposit)  
        
    def add_liquidity2(self, itkn, lp_in, iVault, amt_in):
        itkn_nm = itkn.token_name
        parent_tkn = itkn.parent_tkn
        parent_lp = lp_in.factory.parent_lp
        SwapIndexMint(iVault).apply(parent_lp, parent_tkn, USER_NM, amt_in)
        mint_itkn_deposit = iVault.index_tokens[itkn_nm]['last_lp_deposit']
        tkn_amount1 = LPQuote(False).get_amount_from_lp(parent_lp, parent_tkn, mint_itkn_deposit) 
        price_itkn = tkn_amount1/mint_itkn_deposit 

        itkn1_deposit = 0.5*mint_itkn_deposit
        itkn2_deposit = 0.5*mint_itkn_deposit
        lp_in.add_liquidity(USER_NM, itkn1_deposit, itkn2_deposit, itkn1_deposit, itkn2_deposit)   
        
    def calc_tkn_settlement(self, lp, token_in, dL):

        if(token_in.token_name == lp.token1):
            x = lp.reserve0
            y = lp.reserve1
        else: 
            x = lp.reserve1
            y = lp.reserve0

        L = lp.total_supply
        a0 = dL*x/L
        a1 = dL*y/L
        gamma = 997/1000

        dy1 = a1
        dy2 = gamma*a0*(y - a1)/(x - a0 + gamma*a0)
        itkn_amt = dy1 + dy2

        return itkn_amt          
    
    def setup(self, sys1, dai1):
        
        iVault1 = IndexVault('iVault1', "0x7")
        iVault2 = IndexVault('iVault2', "0x7")        
        
        factory = Factory("SYS pool factory", "0x2")
        lp = self.setup_lp(factory, sys1, dai1, 'LP')
        lp.add_liquidity(USER_NM, SYS_AMT, DAI_AMT, SYS_AMT, DAI_AMT)           
              
        sys2 = ERC20("SYS", "0x09")
        isys1 = IndexERC20("iSYS", "0x09", sys1, lp)         
        lp1 = self.setup_lp(factory, sys2, isys1, 'LP1')
        self.add_liquidity1(sys2, isys1, lp1, iVault1, 10000)
        
        dai2 = ERC20("DAI", "0x09")
        isys2 = IndexERC20("iSYS", "0x09", sys1, lp)          
        lp2 = self.setup_lp(factory, dai2, isys2, 'LP2')
        self.add_liquidity1(dai2, isys2, lp2, iVault1, 10000)
        
        dai3 = ERC20("DAI", "0x09")
        idai1 = IndexERC20("iDAI", "0x09", dai1, lp)         
        lp3 = self.setup_lp(factory, dai3, idai1, 'LP3')
        self.add_liquidity1(dai3, idai1, lp3, iVault1, 1000)
        
        sys3 = ERC20("SYS", "0x09")
        idai2 = IndexERC20("iDAI", "0x09", dai1, lp)           
        lp4 = self.setup_lp(factory, sys3, idai2, 'LP4')
        self.add_liquidity1(sys3, idai2, lp4, iVault1, 1000)  
        
        isys3 = IndexERC20("iSYS", "0x09", sys1, lp)
        idai3 = IndexERC20("iDAI", "0x09", dai1, lp)          
        lp5 = self.setup_lp(factory, isys3, idai3, 'LP5')
        self.add_liquidity2(isys3, lp5, iVault1, 10000)
        self.add_liquidity2(idai3, lp5, iVault2, 1000)        
        
        return lp, lp1, lp2, lp3, lp4, lp5

    
    def test_swap_revenue0(self):
        
        sys1 = ERC20("SYS", "0x09") 
        dai1 = ERC20("DAI", "0x111")
        lp, lp1, lp2, lp3, lp4, lp5 = self.setup(sys1, dai1)
        
        pre_dai_amt = LPQuote(False).get_amount_from_lp(lp, dai1, 1)
        pre_lp_amt = lp.liquidity_providers[USER_NM]
        pre_sys_reserve = lp.reserve0

        N_RUNS = 100
        for k in range(N_RUNS):
            requested_liquidity_in = 500
            sys_settlement_amt = RebaseIndexToken().apply(lp, sys1, requested_liquidity_in) 
            dep = SwapDeposit().apply(lp, sys1, USER_NM, sys_settlement_amt)
            get_deposit = IndexTokenQuote().get_x(lp, lp.last_liquidity_deposit)
            out = WithdrawSwap().apply(lp, sys1, USER_NM, get_deposit)      
           
        post_dai_amt = LPQuote(False).get_amount_from_lp(lp, dai1, 1)
        post_lp_amt = lp.liquidity_providers[USER_NM]
        post_sys_reserve = lp.reserve0
        
        self.assertTrue(round(pre_sys_reserve,8) < round(post_sys_reserve,8))
        self.assertTrue(round(pre_dai_amt,8) == round(post_dai_amt,8))   
        self.assertTrue(round(pre_lp_amt,8) == round(post_lp_amt,8)) 

    def test_swap_revenue2(self):
        
        sys1 = ERC20("SYS", "0x09") 
        dai1 = ERC20("DAI", "0x111")
        
        lp, lp1, lp2, lp3, lp4, lp5 = self.setup(sys1, dai1) 
        
        pre_dai_amt = LPQuote(False).get_amount_from_lp(lp, dai1, 1)
        pre_lp_amt = lp.liquidity_providers[USER_NM]        
        pre_dai_amt2 = LPQuote(False).get_amount_from_lp(lp2, dai1, 1)
        pre_lp_amt2 = lp2.liquidity_providers[USER_NM]
        
        N_RUNS = 3
        for k in range(N_RUNS):
            requested_liquidity_out = 500
            dai_settlement_amt = self.calc_tkn_settlement(lp2, dai1, requested_liquidity_out)
            dai_amt_out = WithdrawSwap().apply(lp2, dai1, USER_NM, dai_settlement_amt)
            dep = SwapDeposit().apply(lp2, dai1, USER_NM, dai_settlement_amt)          
           
        post_dai_amt = LPQuote(False).get_amount_from_lp(lp, dai1, 1)
        post_lp_amt = lp.liquidity_providers[USER_NM]        
        post_dai_amt2 = LPQuote(False).get_amount_from_lp(lp2, dai1, 1)
        post_lp_amt2 = lp2.liquidity_providers[USER_NM]

        self.assertTrue(round(pre_dai_amt,8) == round(post_dai_amt,8))   
        self.assertTrue(round(pre_lp_amt,8) == round(post_lp_amt,8))         
        self.assertTrue(round(pre_dai_amt2,8) < round(post_dai_amt2,8))   
        self.assertTrue(round(pre_lp_amt2,8) > round(post_lp_amt2,8))    
       
        
    def test_swap_revenue4(self):
        
        sys1 = ERC20("SYS", "0x09") 
        dai1 = ERC20("DAI", "0x111")
        
        lp, lp1, lp2, lp3, lp4, lp5 = self.setup(sys1, dai1)
        
        pre_sys_amt = LPQuote(False).get_amount_from_lp(lp, sys1, 1)
        pre_lp_amt = lp.liquidity_providers[USER_NM]        
        pre_sys_amt4 = LPQuote(False).get_amount_from_lp(lp4, sys1, 1)
        pre_lp_amt4 = lp4.liquidity_providers[USER_NM]
        
        N_RUNS = 3
        for k in range(N_RUNS):            
            requested_liquidity_out = 500
            sys_settlement_amt = self.calc_tkn_settlement(lp4, sys1, requested_liquidity_out)
            sys_amt_out = WithdrawSwap().apply(lp4, sys1, USER_NM, sys_settlement_amt)
            dep = SwapDeposit().apply(lp4, sys1, USER_NM, sys_settlement_amt)            
           
        post_sys_amt = LPQuote(False).get_amount_from_lp(lp, sys1, 1)
        post_lp_amt = lp.liquidity_providers[USER_NM]        
        post_sys_amt4 = LPQuote(False).get_amount_from_lp(lp4, sys1, 1)
        post_lp_amt4 = lp4.liquidity_providers[USER_NM]
        
        self.assertTrue(round(pre_sys_amt,8) == round(post_sys_amt,8))   
        self.assertTrue(round(pre_lp_amt,8) == round(post_lp_amt,8))         
        self.assertTrue(round(pre_sys_amt4,8) < round(post_sys_amt4,8))   
        self.assertTrue(round(pre_lp_amt4,8) > round(post_lp_amt4,8))   
        
if __name__ == '__main__':
    unittest.main()                  