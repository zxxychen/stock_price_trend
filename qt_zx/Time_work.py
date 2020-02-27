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
from Buy_break_chan import Buy_chan, Sell_chan, Buy_mean, Sell_mean
from Buy_break_bias import Buy_bias


class TimeWorker:
    def __init__(self, kl_pd, buy_sell_factors):
        self.kl_pd = kl_pd
        self.kl_pd.loc[:,'signal'] = SELL
        self.kl_pd.loc[:,'benchmark'] = np.log(self.kl_pd.pct_chg / 100 + 1)
        self.factors = list()
        self.order = list()
        self._factor_init(buy_sell_factors)
        self.status = SELL
            
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
            if order is not None and order.order_deal == True:
                today_orders.append(order)
        if len(today_orders) > 0:
            self._order_process(today, today_orders)
        else:
            self._no_order_process(today)
                
    
    def _order_process(self, today, orders):
        sell_price = 0
        sell_order_cnt = 0
        buy_price = 0
        buy_order_cnt = 0
        for order in orders:            
            if order.signal == SELL:  
                # 要卖掉该股票
                if self.status == BUY:
                    # 如果以前有持仓才能卖
                    self.status = SELL
                    sell_price += order.price
                    sell_order_cnt += 1
        if sell_order_cnt > 0:
            # 如果有几个卖价，平均一下
            sell_price /= sell_order_cnt
            self.kl_pd.loc[today.key, 'signal'] = SELL
            self.kl_pd.loc[today.key, 'benchmark'] = np.log( (sell_price - today.pre_close) / today.open + 1)
            
        for order in orders:            
            if order.signal == BUY:
                # 要买该股票
                if self.status == SELL:
                    # 如果以前没有持仓才能买
                    self.status = BUY
                    buy_price += order.price
                    buy_order_cnt += 1
        if buy_order_cnt > 0:
            # 如果有几个买价，平均一下
            buy_price /= buy_order_cnt
            self.kl_pd.loc[today.key, 'signal'] = BUY
            self.kl_pd.loc[today.key, 'benchmark'] = np.log( (today.close - buy_price) / buy_price + 1)

    def _no_order_process(self, today):
        self.kl_pd.loc[today.key, 'signal'] = HOLD
        self.kl_pd.loc[today.key, 'benchmark'] = np.log( (today.close - today.pre_close) / today.pre_close + 1)
            
    def fit(self, *args,  **kwargs):
        self.kl_pd.apply(self._day_task, axis=1)
        print(self.kl_pd.tail(20))


    def draw_trend_profit(self, ax=None, show=True):
        kl_pd = self.kl_pd
        
        kl_pd.loc[:, 'signal'].fillna(method='ffill', inplace=True)
        kl_pd.loc[:, 'benchmark'] = np.log(kl_pd.pct_chg / 100 + 1)
        kl_pd.loc[:, 'profit_trend'] = kl_pd.benchmark * kl_pd.signal

        # start_price = kl_pd.loc[0].close
        kl_pd.loc[:, 'benchmark'] = kl_pd.benchmark.cumsum() 
        kl_pd.loc[:, 'profit_trend'] = kl_pd.profit_trend.cumsum() 
        # print(kl_pd.loc[140:150, ['pct_chg', 'benchmark', 'signal']])
        
        print('stock {} from date {} to {}'.format(kl_pd.loc[0, 'ts_code'], kl_pd.loc[0, 'trade_date'], kl_pd.iloc[-1]['trade_date']))
        print('benchmark is {}%'.format(np.around(kl_pd.iloc[-1].benchmark*100, decimals=2)))
        print('final profit is {}%'.format(np.around(kl_pd.iloc[-1].profit_trend*100, decimals=2)))
        print('final profit is {:.2f}%'.format(kl_pd.iloc[-1].profit_trend*100))

        #画出买卖区间：
        if ax:
            self._draw_buy_sell_date(ax)

        if show:
            kl_pd[['profit_trend', 'benchmark']].plot(grid=True, figsize=(14,7))
            plt.show()
    
    def _draw_buy_sell_date(self, ax):
        #画出买卖区间：
        kl_pd = self.kl_pd
        draw_sig = 0
        start_date = 0
        end_date = 0
        keep = 0
        
        for _, row in kl_pd.iterrows():
            if row.signal == 1 and keep == 0:
                start_date = row.key
                keep = 1
            if keep == 1 and row.signal == 0:
                keep = 0
                end_date =  row.key
                draw_sig = 1
            if draw_sig == 1:
                ax.fill_between(kl_pd.key[start_date:end_date]+0.5, 0, kl_pd.close[start_date:end_date], color='red', alpha=0.2)
                draw_sig = 0



if __name__ == "__main__":

    stock = K_line('600105.SH', '20180102', '20201231',get_klines=False)
    stock.load_temp_csv()
    stock.print_k_lines()
    
    stock.candle_plot()
    stock.k_lines_mean_plot([20,5, 30])
    buy_factors =[{'xd1':5, 'xd2':20, 'xd3':30, 'class':Buy_bias, 'ax': stock.ax2}]
    sell_factors=[{'xd':20, 'class': Sell_mean}]
    factors = buy_factors + sell_factors
    print(factors)
    worker = TimeWorker(stock.k_lines[:], factors)
    worker.fit()

    worker.draw_trend_profit(ax=stock.ax1)