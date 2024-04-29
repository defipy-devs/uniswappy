# Copyright [2023] [Ian Moore]
# Distributed under the MIT License (license terms are at http://opensource.org/licenses/MIT).
# Email: defipy.devs@gmail.com

import numpy as np

class MaxDrop():

    """ Determine maximum percentage drop for any numerical array along with its
        starting and end points
    """   
    
    def __init__(self):
        self.__drop = None
        self.__pnt1 = None
        self.__pnt2 = None
    
    def apply(self, arr):
        
        """ apply

            Find maximum percentage drop

            Parameters
            ----------
            arr : numpy.array, shape (n_samples, 1)
                Numerical array 

            Returns
            -------
            x pnt, y pnt, drop : tuple, tuple, float
                Array of optimized leverage values              
        """        
        
        d_downs = self.calc_drawdowns(arr)
        arg_maxis = self.calc_arg_maximums(arr)
        maxis = self.calc_maximums(arr)
        idx = np.argmax(d_downs)
        self.__pnt1 = (arg_maxis[idx], maxis[idx])
        self.__pnt2 = (idx, arr[idx])
        self.__drop = self.calc_drop()
        return self.__pnt1, self.__pnt2, self.__drop  
 
    def calc(self):
        
        """ calc

            Calculate percentage drop given y_start and y_end values

            Returns
            -------
            percent drop : float
                Percentage drop             
        """         
        
        return (self.__pnt1[1]-self.__pnt2[1])/self.__pnt1[1]
    
    def get_pnt1(self):
        
        """ get_pnt1

            Get start point (x,y) of max percentage drop

            Returns
            -------
            self.__pnt1 : tuple
                Start point (x, y)            
        """         
        
        return self.__pnt1 
    
    def get_pnt2(self):
        
        """ get_pnt1

            Get end point (x,y) of max percentage drop

            Returns
            -------
            __pnt1 : tuple
                End point (x, y)            
        """         
        
        return self.__pnt2      
        
    def n_diff(self, arr, N):
        
        """ n_diff

            Generate N differenced time series
            
            Parameters
            ----------
            arr : numpy.array, shape (n_samples, 1)
                Numerical array  
            N : int
                Number of differences                 

            Returns
            -------
            arr_diff : numpy.array, shape (n_samples-1, 1)
                N differenced time series             
        """          
        
        arr = np.array(arr)
        return arr[N:] - arr[:-N]

    def calc_maximums(self, arr_in):  
        
        """ calc_maximums

            Generate monotone increasing array representing max events which increases at every 
            max event of input array
            
            Parameters
            ----------
            arr_in : numpy.array, shape (n_samples, 1)
                Numerical array  
             
            Returns
            -------
            maximums : numpy.array, shape (n_samples, 1)
                Generate monotone increasing array representing max events at every increase            
        """         
        
        N = len(arr_in)
        m = lambda arr, k: max(arr[:k]) if k > 0 else arr[0]   
        maximums = np.array([m(arr_in, k) for k in range(N)])
        return maximums 

    def calc_arg_maximums(self, arr_in):  
        
        """ calc_arg_maximums

            Generate monotone increasing array representing indices at max events which increases 
            at every max event of input array
            
            Parameters
            ----------
            arr_in : numpy.array, shape (n_samples, 1)
                Numerical array  
             
            Returns
            -------
            maximums : numpy.array, shape (n_samples, 1)
                Monotone increasing array representing max events at every increase            
        """          
        
        N = len(arr_in)
        arg_m = lambda arr, k: np.argmax(arr[:k]) if k > 0 else 0  
        arg_maximums = np.array([arg_m(arr_in, k) for k in range(N)])
        return arg_maximums 
    
    def calc_drawdowns(self, arr):
        
        """ calc_drawdowns

            Calculate running drawdowns from every max event of input array; running drawdown gets reset
            to zero when a new max event occurs
            
            Parameters
            ----------
            arr : numpy.array, shape (n_samples, 1)
                Numerical array  
             
            Returns
            -------
            running drawdowns : numpy.array, shape (n_samples, 1)
                Running drawdowns from every max event of input array           
        """      
    
        maxis = self.calc_maximums(arr)
        return (maxis - arr)/maxis

    def m_drawdown(self, arr):
        
        """ m_drawdown

            Calculate maximum drawdown from input array
            
            Parameters
            ----------
            arr : numpy.array, shape (n_samples, 1)
                Numerical array  
             
            Returns
            -------
            Maximum drawdown : float
                Maximum drawdown from input array           
        """         
        
        maxis = self.calc_maximums(arr)
        d_downs = (maxis - arr)/maxis
        idx = np.argmax(d_downs) 
        return d_downs[idx] 
        