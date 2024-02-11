# Copyright [2023] [Ian Moore]
# Distributed under the MIT License (license terms are at http://opensource.org/licenses/MIT).
# Email: defipy.devs@gmail.com

import numpy as np

class BrownianModel():
    
    def __init__(self, x0=0):
        self.__x0 = float(x0)
    
    def gen_gbm(self, mu, sigma, n_step, T = 1):
        
        if n_step < 30:
            print("WARNING! The number of steps is small. It may not generate a good stochastic process sequence!")
                
        dt = float(T) / n_step
        path = np.zeros(n_step + 1, np.float64)
        path[0] = self.__x0
        for t in range(1, n_step + 1):
            rand = np.random.standard_normal()
            path[t] = path[t - 1] * np.exp((mu - 0.5 * sigma ** 2) * dt + sigma * np.sqrt(dt) * rand)
        return path
    
    
    def gen_gbms(self, mu, sigma, n_step, n_paths = 1, T = 1):
        paths = np.zeros((n_step+1, n_paths), np.float64)
        for k in range(n_paths):
            paths[:,k] = self.gen_gbm(mu, sigma, n_step, T)
        return paths      
    
    def gen_random_walk(self, n_step=100):
        
        # Warning about the small number of steps
        if n_step < 30:
            print("WARNING! The number of steps is small. It may not generate a good stochastic process sequence!")
        
        w = np.ones(n_step)*self.x0
        
        for i in range(1,n_step):
            # Sampling from the Normal distribution with probability 1/2
            yi = np.random.choice([1,-1])
            # Weiner process
            w[i] = w[i-1]+(yi/np.sqrt(n_step))
        
        return w
    
    def gen_normal(self, n_step=100):
        if n_step < 30:
            print("WARNING! The number of steps is small. It may not generate a good stochastic process sequence!")
        
        w = np.ones(n_step)*self.x0
        
        for i in range(1,n_step):
            # Sampling from the Normal distribution
            yi = np.random.normal()
            # Weiner process
            w[i] = w[i-1]+(yi/np.sqrt(n_step))
        
        return w
    