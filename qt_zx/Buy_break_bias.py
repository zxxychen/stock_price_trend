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


### 注意 bias 全部用百分数表示！！！也就是-100~100的值

class Buy_bias(Qt_buy_base):
    def __init__(self, kl_pd, **kwargs):
        print('----init---{}'.format(self.__class__.__name__))
        super().__init__(kl_pd)
        self._init_self(**kwargs)
        self._bias_calculate_today()
        if 'ratio' in kwargs:
            self.ratio = kwargs['ratio']
        else:
            self.ratio = 5

    def _init_self(self, **kwargs):
        self.xd1 = kwargs['xd1']
        self.xd2 = kwargs['xd2']
        self.xd3 = kwargs['xd3']
        
        
    
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
        if(day_ind == 245):
            t = 1
            pass
        day_ind -= 1 ##要用昨天的值预测今天的结果

        # # strategy1 上涨趋势 回踩10日线
        if self.kl_pd.iloc[day_ind].xd2 > self.kl_pd.iloc[day_ind].xd3: # xd2日线在xd3日线上方
            #回踩10日线买入 且保持5日线在10日线上方
            p1 = self.kl_pd.iloc[day_ind].xd1            
            p2 = self.kl_pd.iloc[day_ind].xd2
            if p1 > p2:
                diff = p1 - p2
                p = diff * 0.3 + p2
                if p > today.low and today.high > p:
                    res.append(self.make_buy_order(today.key, price=p, discribe='buy in when in middle xd2 and xd3!') )
            # 或者5日线在10日下方，但是上涨超过10日线
            elif p1 < p2:
                p = p2
                if p > today.low and today.high > p:
                    res.append(self.make_buy_order(today.key, price=p, discribe='buy in when in middle xd2 and xd3!') )

        # # strategy2 上涨趋势 回踩60日线，不跌破60日线然后, 然后向上突破10日线
        # if self.kl_pd.iloc[day_ind].xd2 > self.kl_pd.iloc[day_ind].xd3 and \
        #             self.kl_pd.iloc[day_ind].xd1 > self.kl_pd.iloc[day_ind].xd3 and \
        #             self.kl_pd.iloc[day_ind].xd3 > self.kl_pd.iloc[day_ind-1].xd3  and \
        #             self.kl_pd.iloc[day_ind-1].xd3 > self.kl_pd.iloc[day_ind-2].xd3 and \
        #             self.kl_pd.iloc[day_ind].xd2 > self.kl_pd.iloc[day_ind-1].xd2  and \
        #             self.kl_pd.iloc[day_ind-1].xd2 > self.kl_pd.iloc[day_ind-2].xd2 : 
        #             # xd2日线在xd3日线上方 且 前两天的 xd2 和xd3均线都是上涨的
        #     # 回踩到20日和60日均线的中间 则买入
        #     p = (self.kl_pd.iloc[day_ind].xd3 + self.kl_pd.iloc[day_ind].xd2) / 2
        #     if p > today.low and today.high > p:
        #         # 注意这里day_ind是昨天的标号！因此下边用 today.key, buy_order不指定买入值，因此用默认开盘价
        #         res.append(self.make_buy_order(today.key, price=p, discribe='buy in when in middle xd2 and xd3!') )
        return res

class Sell_bias(Qt_sell_base):
    def __init__(self, kl_pd, **kwargs):
        print('----init---{}'.format(self.__class__.__name__))
        super().__init__(kl_pd)
        self._init_self(**kwargs)
        self._bias_calculate_today()
        self.ready_to_sell = 0
        if 'ratio' in kwargs:
            self.ratio = kwargs['ratio']
        else:
            self.ratio = 20

    def _init_self(self, **kwargs):
        self.xd1 = kwargs['xd1']
        self.xd2 = kwargs['xd2']
        self.xd3 = kwargs['xd3']
        if 'N_BOLL' in kwargs:
            self.NBOLL = kwargs['N_BOLL']
        else:
            self.NBOLL = 20
        
    
    def _bias_calculate_today(self):
        kl_pd = self.kl_pd
        # self.kl_pd.loc[:, 'xd1'] = kl_pd.close.rolling(self.xd1).mean()
        # self.kl_pd.loc[:, 'bias1'] = (kl_pd.xd1 - kl_pd.xd1.shift(1)) / kl_pd.xd1 * 100
        # self.kl_pd.loc[:, 'xd2'] = kl_pd.close.rolling(self.xd2).mean()
        # self.kl_pd.loc[:, 'bias2'] = (kl_pd.xd2 - kl_pd.xd2.shift(1)) / kl_pd.xd2 * 100
        # self.kl_pd.loc[:, 'xd3'] = kl_pd.close.rolling(self.xd3).mean()
        # self.kl_pd.loc[:, 'bias3'] = (kl_pd.xd3 - kl_pd.xd3.shift(1)) / kl_pd.xd3 * 100

        # 布林线
        N = self.NBOLL
        self.kl_pd.loc[:, 'Nmean'] = self.kl_pd['close'].rolling(N).mean()
        # 求标准差
        kl_pd.loc[:, 'std'] = kl_pd.close - kl_pd.Nmean
        kl_pd.loc[:, 'std'] = kl_pd['std'].rolling(N).std()
        
        self.kl_pd.loc[:, 'Nup'] = kl_pd.Nmean + 2 * kl_pd.loc[:,'std']
        self.kl_pd.loc[:, 'Ndn'] = kl_pd.Nmean - 2 * kl_pd.loc[:, 'std']
        
    def fit_day(self, today):
        res = list()
        day_ind = today.key
        ##day_ind  #卖出用当天的价格！

        # # 预测值1
        # if self.kl_pd.iloc[day_ind].xd1 > self.kl_pd.iloc[day_ind].xd2: #5日线在10日线上方
        #     if self.kl_pd.iloc[day_ind].xd2 > self.kl_pd.iloc[day_ind-1].xd2 and \
        #         self.kl_pd.iloc[day_ind-1].xd2 > self.kl_pd.iloc[day_ind-2].xd2: # 10日线上涨
        #         # 5日线的bias > ratio
        #         yesterday_mean = self.kl_pd.iloc[day_ind].xd1
        #         ratio = self.ratio
        #         xd = self.xd1
        #         today_price_thres = (xd - 1) * yesterday_mean * (ratio + 1) / (4 - ratio)
        #         if today.high >= today_price_thres:
        #             # print('Sell_bias at day:{}, at price:{}'.format(day_ind, today_price_thres))
        #             res.append(self.make_sell_order(day_ind, price=today_price_thres) )

        # strategy1-止盈：因为5日均线波动大，采用标准差策略，大于两倍标准差则卖出 BOLL指标类似
        # 假设当前价格为p, p的60日均线的乖离率达到某个值，则卖出
        

        p = self.kl_pd.iloc[day_ind-1].Nup ## 注意！！！ BOLL线是用的昨天数据计算的
        # 如果能够突破up线，则准备卖
        if self.ready_to_sell == 0 :
            if today.close > p:
                self.ready_to_sell = 1
        else:
            if today.close < p:
                self.ready_to_sell = 0
                res.append(self.make_sell_order(day_ind, price=today.close, discribe='sell out BOLL!'))

        
        # 如果低于10日均线 卖出
        p = self.kl_pd.iloc[day_ind-1].xd2
        if p > today.low and p < today.high:
            self.ready_to_sell = 0
            res.append(self.make_sell_order(day_ind, price=p, discribe='sell out lower than xd2!'))

        # mean20 = self.kl_pd.iloc[day_ind-1].xd2
        # p = mean20 * (1 + self.ratio/100)
        # if p > today.low and p < today.high:
        #     res.append(self.make_sell_order(day_ind, price=p, discribe='sell out when bias3 > ratio!'))
        # elif p <= today.low:
        #     res.append(self.make_sell_order(day_ind, price=today.low))

        ## 20日和60日均线的差为diff， 上升到20日均线加diff*r则卖出
        # diff = self.kl_pd.iloc[day_ind-1].xd2 - self.kl_pd.iloc[day_ind-1].xd3
        # p = self.kl_pd.iloc[day_ind-1].xd2 + diff * 2
        # if p > today.low and p < today.high:
        #     res.append(self.make_sell_order(day_ind, price=p, discribe='sell out when diff is enough!'))
        # elif p <= today.low:
        #     res.append(self.make_sell_order(day_ind, price=today.low, discribe='sell out when diff is enough!'))

        
        
        # 止损值1
        # if self.kl_pd.iloc[day_ind].xd1 < self.kl_pd.iloc[day_ind].xd2: #5日线在10日线上方
        #     if self.kl_pd.iloc[day_ind].xd2 < self.kl_pd.iloc[day_ind-1].xd2 and \
        #         self.kl_pd.iloc[day_ind-1].xd2 < self.kl_pd.iloc[day_ind-2].xd2: # 10日线持平
        #         # 5日线的bias > ratio
        #         yesterday_mean = self.kl_pd.iloc[day_ind].xd1
        #         today_price_thres = yesterday_mean
        #         # print('Sell_bias at day:{}, at price:{}'.format(day_ind, today_price_thres))
        #         res.append( self.make_sell_order(day_ind, price=today_price_thres))


        # 止损值2 # 如果低于跌破60日均线则卖出
        p = self.kl_pd.iloc[day_ind-1].xd3 
        if p > today.low and p < today.high:
            res.append(self.make_sell_order(day_ind, price=p, discribe='sell out when price lower than xd3!'))
        elif p >= today.high:
            res.append(self.make_sell_order(day_ind, price=today.close, discribe='sell out when price lower than xd3!'))

        return res


