TEST_PATH = "python/test/defi/process/burn"

import os
import sys
import unittest   
sys.path.append(os.getcwd().replace(TEST_PATH,""))

from python.prod.cpt.erc import ERC20
from python.prod.cpt.factory import Factory
from python.prod.cpt.vault import IndexVault
from python.prod.defi.process.burn import IndexTokenBurn
import numpy as np 

USER0 = 'user0'
USER1 = 'user1' 
LP_AMT = 1500

class Test_IndexTokenBurn(unittest.TestCase):
   
    def setup_lp(self, eth, tkn):
        eth_amount = 1000
        tkn_amount = 100000
        factory = Factory("ETH pool factory", "0x2")
        lp_tkn = factory.create_exchange(eth, tkn, symbol="LP_TKN", address="0x011")
        lp_tkn.add_liquidity(USER0, eth_amount, tkn_amount, eth_amount, tkn_amount)
        lp_tkn.add_liquidity(USER1, eth_amount, tkn_amount, eth_amount, tkn_amount)   
        return lp_tkn
    
    def setup_vault(self, lp_tkn, token):
        ivault = IndexVault('iVault', "0x7")
        ivault.deposit_lp_tkn(USER0, lp_tkn, LP_AMT)
        ivault.deposit_lp_tkn(USER1, lp_tkn, LP_AMT)        
        ivault.mint_index_tkn(lp_tkn, token)
        return ivault    
          
    def test_burn1(self):
        lp_burn = 300
        tkn = ERC20("TKN", "0x111")
        eth = ERC20("ETH", "0x09")        
        lp_tkn = self.setup_lp(eth, tkn)
        ivault = self.setup_vault(lp_tkn, eth)
        tburn = IndexTokenBurn(ivault).apply(lp_tkn, eth, USER0, lp_burn)        
        self.assertEqual(ivault.lp_providers[USER0]['iETH']['amount'], 160.0)
        self.assertEqual(ivault.lp_providers[USER0]['ETHTKN-LP']['amount'], 1200)

    def test_burn2(self):
        lp_burn = 300
        tkn = ERC20("TKN", "0x111")
        eth = ERC20("ETH", "0x09")        
        lp_tkn = self.setup_lp(eth, tkn)
        ivault = self.setup_vault(lp_tkn, tkn)
        tburn = IndexTokenBurn(ivault).apply(lp_tkn, tkn, USER0, lp_burn)     
        self.assertEqual(ivault.lp_providers[USER0]['iTKN']['amount'], 16000.0)
        self.assertEqual(ivault.lp_providers[USER0]['ETHTKN-LP']['amount'], 1200)

if __name__ == '__main__':
    unittest.main()
