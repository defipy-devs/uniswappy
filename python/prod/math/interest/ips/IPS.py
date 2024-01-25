# IPS.py
# Author: Ian Moore ( utiliwire@gmail.com )
# Date: Sept 2022

from abc import *

DAYS_IN_YEAR = 365.25
HOURS_IN_DAY = 24
SECONDS_IN_HOUR = 3600

class IPS(ABC):

    SECONDS_YEAR = DAYS_IN_YEAR*HOURS_IN_DAY*SECONDS_IN_HOUR
    
    @abstractmethod
    def calc_ips_from_state(self, state):
        pass
    
    def calc_ips(self, A0, A1, t_delta):
        pass
        
    
    