import matplotlib as mpl
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mp
from matplotlib.gridspec import GridSpec
import numpy as np
import tushare as ts
from matplotlib.pylab import date2num
import datetime
from abc import ABCMeta, abstractmethod
from qt_base import K_line
from ProcessBase import Qt_buy_base, Qt_sell_base

class Buy_chan(Qt_buy_base):
    def __init__(self, kl_pd, **kwargs):
        print('--init-- Buy_chan------')
        super().__init__(kl_pd)
        self._init_self(**kwargs)

    def _init_self(self, **kwargs):
        self.xd =  kwargs['xd']

    
    def fit_day(self, today):
        kl_pd = self.kl_pd
        day_ind = int(today.key)
        if today.key > self.xd:
            if(today.close > kl_pd.high[day_ind - self.xd + 1 : day_ind].max()):
                return self.make_buy_order(day_ind+1)
            else:
                return None

class Sell_chan(Qt_sell_base):
    def __init__(self, kl_pd, **kwargs):
        super().__init__(kl_pd)
        self._init_self(**kwargs)


    def _init_self(self, **kwargs):
        self.xd =  kwargs['xd']
    
    def fit_day(self, today):
        kl_pd = self.kl_pd
        day_ind = int(today.key)
        if day_ind > self.xd:
            if(today.close < kl_pd.low[day_ind - self.xd + 1 : day_ind].min()):
                return self.make_sell_order(day_ind)
            else:
                return None


class Buy_mean(Qt_buy_base):
    def __init__(self, kl_pd, **kwargs):
        print('----init---{}'.format(self.__class__.__name__))
        super().__init__(kl_pd)
        self._init_self(**kwargs)

    def _init_self(self, **kwargs):
        self.xd =  kwargs['xd']

    
    def fit_day(self, today):
        kl_pd = self.kl_pd
        day_ind = int(today.key)
        if day_ind > self.xd:
            if(today.close > kl_pd['close'].rolling(self.xd).mean()[day_ind] \
                and kl_pd['close'].rolling(20).mean()[day_ind] > kl_pd['close'].rolling(60).mean()[day_ind]):
                return self.make_buy_order(day_ind+1)
            else:
                return None

class Sell_mean(Qt_sell_base):
    def __init__(self, kl_pd, **kwargs):
        print('----init---{}'.format(self.__class__.__name__))
        super().__init__(kl_pd)
        self._init_self(**kwargs)


    def _init_self(self, **kwargs):
        self.xd =  kwargs['xd']
    
    def fit_day(self, today):
        kl_pd = self.kl_pd
        day_ind = int(today.key)
        if day_ind > self.xd and day_ind < len(kl_pd)-2:
            if(today.close < kl_pd['close'].rolling(self.xd).mean()[day_ind]):
                return self.make_sell_order(day_ind+1)
            else:
                return None

class Buy_bias(Qt_buy_base):
    def __init__(self, kl_pd, **kwargs):
        print('----init---{}'.format(self.__class__.__name__))
        super().__init__(kl_pd)
        self._init_self(**kwargs)

    def _init_self(self, **kwargs):
        self.xd1 =  kwargs['xd1']
        self.xd2 =  kwargs['xd2']

    
    def fit_day(self, today):
        kl_pd = self.kl_pd
        day_ind = int(today.key)
        if day_ind > np.max(self.xd1, self.xd2):
            if(today.close > kl_pd['close'].rolling(self.xd).mean()[day_ind]):
                return self.make_buy_order(day_ind+1)
            else:
                return None

class Sell_bias(Qt_sell_base):
    def __init__(self, kl_pd, **kwargs):
        print('----init---{}'.format(self.__class__.__name__))
        super().__init__(kl_pd)
        self._init_self(**kwargs)


    def _init_self(self, **kwargs):
        self.xd =  kwargs['xd']
    
    def fit_day(self, today):
        kl_pd = self.kl_pd
        day_ind = int(today.key)
        if day_ind > self.xd and day_ind < len(kl_pd)-2:
            if(today.close < kl_pd['close'].rolling(self.xd).mean()[day_ind]):
                return self.make_sell_order(day_ind)
            else:
                return None