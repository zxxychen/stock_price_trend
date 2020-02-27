import matplotlib as mpl
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mp
from matplotlib.gridspec import GridSpec
import numpy as np
import tushare as ts
from matplotlib.pylab import date2num
import datetime
from global_paras import *
from abc import ABC, abstractmethod
from qt_base import K_line


class Qt_buy_base(ABC):
    def __init__(self, kl_pd):
        self.kl_pd = kl_pd
        pass

    @abstractmethod
    def fit_day(self,  **kwargs):
        pass

    def make_buy_order(self, day_ind, **kwargs):
        """
        根据交易发生的时间索引，依次进行交易订单生成，交易时间序列特征生成，
        :param day_ind: 交易发生的时间索引，即对应self.kl_pd.key
        """
        self.today_ind = day_ind

        order = Qt_order()
        # AbuOrde对象根据交易发生的时间索引生成交易订单
        order.fit_buy_order(day_ind, self, **kwargs)
        return order


class Qt_sell_base(ABC):
    def __init__(self, kl_pd):
        self.kl_pd = kl_pd
        pass

    @abstractmethod
    def fit_day(self, **kwargs):
        pass  

    def make_sell_order(self, day_ind, **kwargs):
        """
        根据交易发生的时间索引，依次进行交易订单生成，交易时间序列特征生成，
        :param day_ind: 交易发生的时间索引，即对应self.kl_pd.key
        """
        self.today_ind = day_ind

        order = Qt_order()
        # AbuOrde对象根据交易发生的时间索引生成交易订单
        order.fit_sell_order(day_ind, self, **kwargs)
        return order

class Qt_order():
    def __init__(self):
        self.order_deal = False
           
    def fit_buy_order(self, day_ind, factors,  **kwargs):        
        #factors: Qt_buy_base
        self.day_ind = day_ind

        self.price = factors.kl_pd.iloc[day_ind].open
        # signal = 1 代表买入
        self.signal = BUY
        self.order_deal = True
        if 'price' in kwargs:
            buy_price = kwargs['price']
            self.price = buy_price
        if factors.kl_pd.iloc[day_ind].open == factors.kl_pd.iloc[day_ind].close and \
            factors.kl_pd.iloc[day_ind].open == factors.kl_pd.iloc[day_ind].high and \
            factors.kl_pd.iloc[day_ind].open == factors.kl_pd.iloc[day_ind].low:
            if factors.kl_pd.iloc[day_ind].pct_chg > 5: #涨停 无法买入
                self.signal = HOLD


    def fit_sell_order(self, day_ind, factors, **kwargs):
        #factors: Qt_buy_base
        self.day_ind = day_ind
        self.price = factors.kl_pd.iloc[day_ind].close
        # signal = 0 代表卖出
        self.signal = SELL
        self.order_deal = True
        if 'sell_price' in kwargs:
            self.price = kwargs['sell_price']
        if factors.kl_pd.iloc[day_ind].open == factors.kl_pd.iloc[day_ind].close and \
            factors.kl_pd.iloc[day_ind].open == factors.kl_pd.iloc[day_ind].high and \
            factors.kl_pd.iloc[day_ind].open == factors.kl_pd.iloc[day_ind].low:
            if factors.kl_pd.iloc[day_ind].pct_chg < 5: #跌停 无法卖出
                self.signal = HOLD

    def __str__(self):
        return 'the day {}  signal= {} at price {}'.format(self.day_ind, 'buy' if self.signal else 'sell', self.price)
