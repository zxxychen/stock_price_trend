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

#BOLL

class Buy_bias(Qt_buy_base):
    def __init__(self, kl_pd, **kwargs):
        print('----init---{}'.format(self.__class__.__name__))
        super().__init__(kl_pd)
        self._init_self(**kwargs)
        self._bias_calculate_today()

    def _init_self(self, **kwargs):
        self.xd1 = kwargs['xd1']
        self.xd2 = kwargs['xd2']
        self.xd3 = kwargs['xd3']
        
        
    
    def _bias_calculate_today(self):
        kl_pd = self.kl_pd
        self.kl_pd.loc[:, 'xd1'] = kl_pd.close.rolling(self.xd1).mean()
        self.kl_pd.loc[:, 'bias1'] = (kl_pd.close - kl_pd.xd1) / kl_pd.xd1 * 100
        self.kl_pd.loc[:, 'xd2'] = kl_pd.close.rolling(self.xd2).mean()
        self.kl_pd.loc[:, 'bias2'] = (kl_pd.close - kl_pd.xd2) / kl_pd.xd2 * 100
        self.kl_pd.loc[:, 'xd3'] = kl_pd.close.rolling(self.xd3).mean()
        self.kl_pd.loc[:, 'bias3'] = (kl_pd.close - kl_pd.xd3) / kl_pd.xd3 * 100

        
    
    def fit_day(self, today):
        day_ind = today.key
        day_ind -= 1 ##要用昨天的值预测今天的结果
        if self.kl_pd.iloc[day_ind].xd1 > self.kl_pd.iloc[day_ind].xd2: #5日线在10日线上方
            if self.kl_pd.iloc[day_ind].xd2 > self.kl_pd.iloc[day_ind-1].xd2 and \
                self.kl_pd.iloc[day_ind-1].xd2 > self.kl_pd.iloc[day_ind-2].xd2: # 10日线上涨
                #回踩10日线买入
                today_price_thres = self.kl_pd.iloc[day_ind].xd2
                if today.low <= today_price_thres:
                    return self.make_buy_order(day_ind, price=today_price_thres) 
        return None

class Sell_bias(Qt_sell_base):
    def __init__(self, kl_pd, **kwargs):
        print('----init---{}'.format(self.__class__.__name__))
        super().__init__(kl_pd)
        self._init_self(**kwargs)
        self._bias_calculate_today()

    def _init_self(self, **kwargs):
        self.xd1 = kwargs['xd1']
        self.xd2 = kwargs['xd2']
        self.xd3 = kwargs['xd3']
        
        
    
    def _bias_calculate_today(self):
        kl_pd = self.kl_pd
        self.kl_pd.loc[:, 'xd1'] = kl_pd.close.rolling(self.xd1).mean()
        self.kl_pd.loc[:, 'bias1'] = (kl_pd.close - kl_pd.xd1) / kl_pd.xd1 * 100
        self.kl_pd.loc[:, 'xd2'] = kl_pd.close.rolling(self.xd2).mean()
        self.kl_pd.loc[:, 'bias2'] = (kl_pd.close - kl_pd.xd2) / kl_pd.xd2 * 100
        self.kl_pd.loc[:, 'xd3'] = kl_pd.close.rolling(self.xd3).mean()
        self.kl_pd.loc[:, 'bias3'] = (kl_pd.close - kl_pd.xd3) / kl_pd.xd3 * 100
        
    def fit_day(self, today):
        day_ind = today.key
        day_ind -= 1 ##要用昨天的值预测今天的结果
        if self.kl_pd.iloc[day_ind].xd1 > self.kl_pd.iloc[day_ind].xd2: #5日线在10日线上方
            if self.kl_pd.iloc[day_ind].xd2 > self.kl_pd.iloc[day_ind-1].xd2 and \
                self.kl_pd.iloc[day_ind-1].xd2 > self.kl_pd.iloc[day_ind-2].xd2: # 10日线上涨
                #回踩10日线买入
                today_price_thres = self.kl_pd.iloc[day_ind].xd2
                if today.low <= today_price_thres:
                    return self.make_sell_order(day_ind+1) 
        return None