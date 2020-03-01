import matplotlib as mpl
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mp
from matplotlib.gridspec import GridSpec
import numpy as np
import tushare as ts
from global_paras import *
from matplotlib.pylab import date2num
import datetime
from abc import ABCMeta, abstractmethod
from qt_base import K_line
from ProcessBase import Qt_buy_base, Qt_sell_base

### 注意 bias 全部用百分数表示！！！也就是-100~100的值

class Buy_safe(Qt_buy_base):
    def __init__(self, kl_pd, **kwargs):
        print('----init---{}'.format(self.__class__.__name__))
        # 安全等级
        self.safety = SAFE0 
        # 准备买入信号
        self.ready_to_buy = 0

        super().__init__(kl_pd)
        self._init_self(**kwargs)
        self._bias_calculate_today()
        

    def _init_self(self, **kwargs):
        self.xd1 = kwargs['xd1']
        self.xd2 = kwargs['xd2']
        self.xd3 = kwargs['xd3']
        if 'ratio' in kwargs:
            self.ratio = kwargs['ratio']
        else:
            self.ratio = 5
        
        
    
    def _bias_calculate_today(self):
        kl_pd = self.kl_pd
        self.kl_pd.loc[:, 'xd1'] = kl_pd.close.rolling(self.xd1).mean()
        self.kl_pd.loc[:, 'bias1'] = (kl_pd.high - kl_pd.xd1) / kl_pd.xd1 * 100
        self.kl_pd.loc[:, 'xd2'] = kl_pd.close.rolling(self.xd2).mean()
        self.kl_pd.loc[:, 'bias2'] = (kl_pd.high - kl_pd.xd2) / kl_pd.xd2 * 100
        self.kl_pd.loc[:, 'xd3'] = kl_pd.close.rolling(self.xd3).mean()
        self.kl_pd.loc[:, 'bias3'] = (kl_pd.high - kl_pd.xd3) / kl_pd.xd3 * 100

        
    
    def fit_day(self, today):
        res = list()
        day_ind = today.key
        day_ind -= 1 ##要用昨天的值预测今天的结果

        if self.ready_to_buy == 0:
            # # strategy1 上涨趋势 触发准备买入信号
            if self.kl_pd.iloc[day_ind].xd2 > self.kl_pd.iloc[day_ind].xd3: # xd2日线在xd3日线上方
                #回踩5日线买入 但是先观察前几日5日线的bias值
                # 如果突破过去5日的最大值，发出买入信号
                if today.close > np.max(self.kl_pd.iloc[day_ind-self.xd1:day_ind+1].close):
                    self.ready_to_buy = 1
            else:
                # 如果此时10日线下降到60日线下方，则不能买入
                self.ready_to_buy = 0

        else:
            # 如果跌破新低，取消准备买入
            if self.kl_pd.iloc[day_ind].low < np.min(self.kl_pd.iloc[day_ind-self.xd1+1:day_ind].low):
                self.ready_to_buy = 0
            # 预测今天均线值为：用前两天的均线预测今天均线
            mean_thres = self.kl_pd.iloc[day_ind].xd1 + (self.kl_pd.iloc[day_ind].xd1 - self.kl_pd.iloc[day_ind-1].xd1)
            p = mean_thres * (1 + self.ratio / 100)
            if self.ready_to_buy == 1:
                if p > today.low and today.high > p:
                    res.append(self.make_buy_order(today.key, price=p, discribe='buy in break up MA5!') )
                    self.ready_to_buy = 0

        # 突破5日新高就买入
        # if self.kl_pd.iloc[day_ind].xd2 > self.kl_pd.iloc[day_ind].xd3: # xd2日线在xd3日线上方
        #     if today.high > np.max(self.kl_pd.iloc[day_ind-self.xd1+1:day_ind+1].high):
        #         #             self.ready_to_buy = 1
        #         p = np.max(self.kl_pd.iloc[day_ind-self.xd1+1:day_ind+1].high)
        #         res.append(self.make_buy_order(today.key, price=p, discribe='buy in break up MA5!') )
        return res

class Sell_safe(Qt_sell_base):
    def __init__(self, kl_pd, **kwargs):
        print('----init---{}'.format(self.__class__.__name__))
        super().__init__(kl_pd)
        self._init_self(**kwargs)
        self._bias_calculate_today()
        self.ready_to_sell = 0
        self.safety = SAFE0 
        

    def _init_self(self, **kwargs):
        self.xd1 = kwargs['xd1']
        self.xd2 = kwargs['xd2']
        self.xd3 = kwargs['xd3']
        if 'ratio' in kwargs:
            self.ratio = kwargs['ratio']
        else:
            self.ratio = 5
        
    
    def _bias_calculate_today(self):
        pass
        
    def fit_day(self, today):
        res = list()
        day_ind = today.key
        ##day_ind  #卖出用当天的价格！       
        # 跌破五日最低价则卖出
        p = np.min(self.kl_pd.iloc[day_ind-self.xd1+1:day_ind].low) 
        # 如果能够突破up线，则准备卖
    
        if today.low < p:
            if p < today.high:
                res.append(self.make_sell_order(day_ind, price=p, discribe='sell out break down MA5 low'))
            else:
                # 直接跳空跌破前五日最小值
                p = (today.high +today.low) / 2
                res.append(self.make_sell_order(day_ind, price=p, discribe='sell out break down MA5 low'))
        
        # 止损 如果5日线在10日线上方，价格低于10日均线 卖出
        p = self.kl_pd.iloc[day_ind-1].xd2
        if p > today.low and p < today.high and self.kl_pd.iloc[day_ind-1].xd1 > self.kl_pd.iloc[day_ind-1].xd2:
            self.ready_to_sell = 0
            res.append(self.make_sell_order(day_ind, price=p, discribe='sell out lower than MA10!'))
        
        # 止损 如果跌幅超过7%则卖出
        if today.low / self.kl_pd.iloc[day_ind-1].close < 0.93:
            p = self.kl_pd.iloc[day_ind-1].close * 0.93
            res.append(self.make_sell_order(day_ind, price=p, discribe='sell out today went down %7!'))

        return res


