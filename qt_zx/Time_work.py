import matplotlib as mpl
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mp
from matplotlib.gridspec import GridSpec
import numpy as np
import tushare as ts
from matplotlib.pylab import date2num
import datetime
import copy
from abc import ABCMeta, abstractmethod
from qt_base import K_line
from global_paras import *
from ProcessBase import Qt_sell_base, Qt_buy_base, Qt_order 
from Buy_break_yao import Buy_yao, Sell_mean
from Buy_break_bias import Buy_bias, Sell_bias
from Buy_safe_and_positive_strategy import Buy_safe, Sell_safe


class TimeWorker:
    def __init__(self, kl_pd, buy_sell_factors):
        self.kl_pd = kl_pd
        self.kl_pd.loc[:,'signal'] = HOLD
        self.kl_pd.loc[:,'profit'] = np.log(self.kl_pd.pct_chg / 100 + 1)
        # self.kl_pd.loc[:,'price'] = self.kl_pd.close
        self.factors = list()  #买入卖出策略类
        self._factor_init(buy_sell_factors)

        self.orders = pd.DataFrame(columns=['buy_date', 'sell_date', 'buy_price', 'sell_price', 'profit'])
        self.status = SELL
        self.buy_price = 0
        self.buy_date = 0
            
    def _factor_init(self, buy_sell_factors):
        for factor in buy_sell_factors:
            if  factor is None:
                continue
            if 'class' not in factor:
                raise ValueError('Factor  class key must name class!!!')
            # factor = copy.deepcopy(factor)
            class_fac = copy.deepcopy(factor['class'])
            # del factor['class']
            #del 之后，buy_factor只剩下‘xd’等信息
            print(factor, type(factor))
            buy_sell_factor = class_fac(self.kl_pd, **factor)
            self.factors.append(buy_sell_factor)


    def _day_task(self, today):
        today_orders = list()
        for factor in self.factors:
            order = factor.fit_day(today)
            today_orders += order #两个列表相加，把元素连到一起，不能用append
        if len(today_orders) > 0:
            self._order_process(today, today_orders)
        else:
            self._no_order_process(today)
                
    
    def _order_process(self, today, orders):
        ## 均采用当天买入当天卖出的策略方式！！！
        sell_price = 0
        sell_order_cnt = 0
        buy_price = 0
        buy_order_cnt = 0

        ##------- Sell orders 处理 -------------------
        reason = ''   #可以打印卖出原因       
        for order in orders:              
            if order.signal == SELL:  
                # 要卖掉该股票
                if self.status == BUY:
                    # 如果以前有持仓才能卖
                    self.status = SELL
                    sell_price += order.price
                    sell_order_cnt += 1
                    reason += ' ' + order.discribe
        if sell_order_cnt > 0:
            # 如果有几个卖价，平均一下
            sell_price /= sell_order_cnt
            self.kl_pd.loc[today.key, 'signal'] = SELL # 当天卖出，但是当天还有收益，所以第二天为SELL

            self.kl_pd.loc[today.key-1, 'profit'] += np.log( (sell_price - today.pre_close) / today.pre_close + 1)
            print('Sell at day:{}, at price:{:.4f}, holding {} days, profit={:.2f}%, sell reason:{}'.format(today.key, sell_price,\
                                                today.key - self.buy_date,(sell_price - self.buy_price)*100/self.buy_price,\
                                                    reason))
            self.orders = self.orders.append({'buy_date':self.buy_date, \
                                                'sell_date':today.key+1, \
                                                'buy_price': self.buy_price,\
                                                'sell_price': sell_price,\
                                                'profit': (sell_price - self.buy_price)*100/self.buy_price},\
                                                ignore_index=True)

        ##------- Buy orders 处理 ------------------- 
        reason = ''       #可以打印买入原因  
        if  sell_order_cnt == 0:  ## 当天如果有卖出，就不再买入
            for order in orders:                       
                if order.signal == BUY:
                    # 要买该股票
                    if self.status == SELL:
                        # 如果以前没有持仓才能买
                        self.status = BUY
                        buy_price += order.price
                        buy_order_cnt += 1
                        reason += ' ' + order.discribe
        if buy_order_cnt > 0:
            # 如果有几个买价，平均一下
            buy_price /= buy_order_cnt
            self.buy_date = today.key
            self.buy_price = buy_price
            self.kl_pd.loc[today.key, 'signal'] = BUY
            self.kl_pd.loc[today.key, 'profit'] = np.log( (today.close - buy_price) / buy_price + 1)
            print('Buy at day:{}, at price:{:.2f}， buy reason:{}'.format(today.key, self.buy_price, reason))

    def _no_order_process(self, today):
        self.kl_pd.loc[today.key, 'signal'] = HOLD
        self.kl_pd.loc[today.key, 'profit'] = np.log( (today.close - today.pre_close) / today.pre_close + 1)
            
    def fit(self, *args,  **kwargs):
        self.kl_pd.apply(self._day_task, axis=1)
        # self.kl_pd[['bias1', 'bias2', 'bias3']].plot(grid=True)
        # temp = self.kl_pd['xd1'] / self.kl_pd['xd3'] 
        # fig = plt.figure(figsize=(14,7))
        # ax = plt.subplot()
        # ax.grid(True)
        # ax.plot(np.arange(len(temp)), temp)
        # plt.show()


    def draw_trend_profit(self, ax=None, show=True):
        kl_pd = self.kl_pd
        kl_pd.loc[0, 'signal'] = SELL
        kl_pd.loc[:, 'signal'].fillna(method='ffill', inplace=True)
        kl_pd.loc[:, 'benchmark'] = np.log(kl_pd.pct_chg / 100 + 1)
        kl_pd.loc[:, 'profit_trend'] = kl_pd.profit * kl_pd.signal

        # start_price = kl_pd.loc[0].close
        kl_pd.loc[:, 'benchmark'] = kl_pd.benchmark.cumsum() 
        kl_pd.loc[:, 'profit_trend'] = kl_pd.profit_trend.cumsum() 
        # print(kl_pd.loc[140:150, ['pct_chg', 'benchmark', 'signal']])
        # kl_pd.to_csv('./gen/profit.csv', columns=kl_pd.columns, index=True)
        print('stock {} from date {} to {}'.format(kl_pd.loc[0, 'ts_code'], kl_pd.loc[0, 'trade_date'], kl_pd.iloc[-1]['trade_date']))
        print('benchmark is {}%'.format(np.around(kl_pd.iloc[-1].benchmark*100, decimals=2)))
        # print('final profit is {}%'.format(np.around(kl_pd.iloc[-1].profit_trend*100, decimals=2)))
        print('final profit is {:.2f}%'.format(kl_pd.iloc[-1].profit_trend*100))

        #画出买卖区间：
        if ax:
            self._draw_buy_sell_date(ax)

        if show:
            kl_pd[['profit_trend', 'benchmark']].plot(grid=True, figsize=(14,7))
            plt.show()
        
        return kl_pd.iloc[-1].profit_trend*100
    
    def _draw_buy_sell_date(self, ax):
        #画出买卖区间：
        kl_pd = self.kl_pd
        
        for _, order in self.orders.iterrows():
            start_date = int(order.buy_date)
            end_date = int(order.sell_date)
            # print('-----------', start_date, end_date)
            ax.fill_between(kl_pd.key[start_date:end_date]+0.5, 0, kl_pd.close[start_date:end_date], color='red', alpha=0.2)


if __name__ == "__main__":

    stock = K_line('600992.SH', '20180102', '20201231',get_klines=False)
    stock.load_temp_csv()
    # stock.print_k_lines()
    
    stock.candle_plot()
    stock.k_lines_mean_plot([20,5, 60])
    # stock.k_lines_BOLL_plot(20)
    buy_factors =[{'xd1':3, 'xd2':20, 'xd3':60, 'class':Buy_safe, 'ax':stock.ax1}]
    sell_factors=[{'xd1':5, 'xd2':20, 'xd3':60, 'class':Sell_safe, 'ratio':0}]
    factors = buy_factors + sell_factors
    print(factors)
    worker = TimeWorker(stock.k_lines[:], factors)
    worker.fit()

    worker.draw_trend_profit(ax=stock.ax1, show=True)