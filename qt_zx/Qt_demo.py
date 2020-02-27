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

from Time_work import TimeWorker
from Buy_break_chan import Buy_chan, Sell_chan
from ProcessBase import Qt_order

stock = K_line('000001.SZ', '20170102', '20190718')
stock.candle_plot()
# stock.print_k_lines(10)
buy_factors =[{'xd':10, 'class':Buy_chan},
                {'xd':20, 'class':Buy_chan}]
sell_factors=[{'xd':10, 'class': Sell_chan}]
factors = buy_factors + sell_factors
print(factors)
worker = TimeWorker(stock.k_lines, factors)
worker.fit()
worker.draw_trend_profig()
