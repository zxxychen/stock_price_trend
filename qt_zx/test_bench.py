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
from qt_base import K_line, K_line_list
from global_paras import *
from ProcessBase import Qt_sell_base, Qt_buy_base, Qt_order 
from Buy_break_yao import Buy_yao, Sell_mean
from Buy_break_bias import Buy_bias, Sell_bias
from Buy_safe_and_positive_strategy import Buy_safe, Sell_safe
from Time_work import TimeWorker
import time
from multiprocessing import Pool

def run(tscode):
    buy_factors =[{'xd1':3, 'xd2':20, 'xd3':60, 'class':Buy_safe}]
    sell_factors=[{'xd1':5, 'xd2':20, 'xd3':60, 'class':Sell_safe, 'ratio':0}]
    factors = buy_factors + sell_factors
    stock = K_line(tscode, '20180102', '20201231',get_klines=False)
    worker = TimeWorker(stock.k_lines[:], factors)
    worker.fit()
    profit = worker.draw_trend_profit(ax=None, show=False)
    print('{} profit is {}'.format(tscode, profit))
    return profit
if __name__ == "__main__":
    start_time = time.time()

    k_line_list = K_line_list.test_list()

    aver_profit = 0
    cnt = 0

    # for _, row in k_line_list.iterrows():
    #     tscode = row['ts_code']
    #     stock = K_line(tscode, '20180102', '20201231',get_klines=False)
    #     worker = TimeWorker(stock.k_lines[:], factors)
    #     worker.fit()
    #     profit = worker.draw_trend_profit(ax=None, show=False)
    #     print('{} profit is {}'.format(tscode, profit))
    #     aver_profit += profit
    #     cnt += 1
    
    # aver_profit /= cnt
    # print('final test profit is {}'.format(aver_profit))



    tscode_list = k_line_list.ts_code.tolist()
    # print(tscode_list)
    p = Pool(4)
    res = p.map(run, tscode_list)
    p.close()
    p.join()
    print(res)
    # run(tscode_list[0])

    elapsed = time.time() - start_time
    print('test time is {}'.format(elapsed))