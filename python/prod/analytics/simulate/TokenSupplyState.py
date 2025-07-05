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

import numpy as np
import pandas as pd
from termcolor import colored
from ...cpt.quote import LPQuote
from ...process.swap import Swap
from ...math.model import TokenDeltaModel

class TokenSupplyState():
    
    def __init__(self, stochastic = True, tDel = None):
        self.tDel = TokenDeltaModel(500) if tDel == None else tDel
        self.stochastic = stochastic
        self.current_state = [[0, 0, 0, 0]]
        self.states = self.current_state

    def gen_states(self, N):   
        for k in range(N):
            self.next_state(self.tDel.delta())
        return self.get_state_df()          
        
    def next_state(self, minted = None):
        P = self.gen_trans_matrix(self.stochastic)     
        self.current_state = np.dot(self.current_state, P)
        minted = self.tDel.delta() if minted == None else minted
        self.current_state = self.current_state  + np.array([[minted, 0.0, 0.0, 0.0]])
        self.states = np.append(self.states, self.current_state, axis=0)
        
    def update_current_state(self, amt, stat_cat = 'LP'):
        if(stat_cat == 'LP'):
            self.states[-1,1] += amt  # Add to held
            self.states[-1,2] -= amt  # Remove from vault
             
    def get_current_state(self, colnm = None):  
        df_states = self.get_state_df(self.states[-2:])
        return df_states.iloc[-1] if colnm == None else df_states[colnm].iloc[-1]
    
    def get_state_df(self, state_arr = []): 
        state_arr = self.states[1:,] if len(state_arr) == 0 else state_arr
        df_states = pd.DataFrame(self.states[1:,])    
        df_states.columns = ['Mint', 'Held', 'LP', 'Burn'] 
        df_states['dHeld'] = np.insert(np.diff(df_states['Held'].values), 0, 0)
        df_states['dLP'] = np.insert(np.diff(df_states['LP'].values), 0, 0)
        df_states['dBurn'] = np.insert(np.diff(df_states['Burn'].values), 0, 0) 
        return df_states
        
    def scale_x(self, x):
        return list(x/np.sum(x))
    
    def rBeta(self, a, b, mx = None, mn =None):
        p = np.random.beta(a,b)
        p = p if mn == None else max(p, mn)
        p = p if mx == None else min(p, mx)                  
        return p   

    def gen_trans_matrix(self, stochastic = True):

        P_stochastic = np.array([ [0, 1, 0, 0],
                           [0, self.rBeta(19,81), self.rBeta(4,1), self.rBeta(1,99)],
                           [0, self.rBeta(1,4, mn = 0.2, mx = 0.3), self.rBeta(4,1, mn = 0.7, mx = 0.8), 0],
                           [0, 0, 0, 1]])

        P_deterministic = np.array([ [0, 1, 0, 0],
                           [0, 0.18, 0.8, 0.02],
                           [0, 0.2, 0.8, 0],
                           [0, 0, 0, 1]])    

        P = P_stochastic if stochastic else P_deterministic  
        return np.array(list(map(self.scale_x, P))) 
    
    def inspect_states(self, tail = True, num_states = 5):
        dfDistrLP1 = self.get_state_df()
        return dfDistrLP1.tail(num_states) if tail else dfDistrLP1.head(num_states)  

    def check_states(self):
        dfDistrLP = self.get_state_df()
        states_balanced = round(sum(dfDistrLP.iloc[-1,1:4]),8) == round(sum(dfDistrLP.iloc[:-1,0]),8)
        test_outcome = colored('PASS', 'green', attrs=['bold']) if states_balanced else colored('FAIL', 'red', attrs=['bold'])            
        print(f'Amount of tokens retained across states: {test_outcome}')   