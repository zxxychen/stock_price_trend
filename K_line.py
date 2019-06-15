import matplotlib as mpl
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mp
from matplotlib.gridspec import GridSpec
import numpy as np
import tushare as ts
from matplotlib.pylab import date2num
import datetime


class K_line():
    def __init__(self, code, start_time, end_time):
        self.code = code
        # self.period = period
        self.start_time = start_time
        self.end_time = end_time
        

    def pro_init(self):
        self.pro = ts.pro_api('d5741f23ebd206c762d2e593573499d5a479b8955ae9b5152c646ba2')
    
    def get_daily_lists(self):
        df = self.pro.daily(ts_code=self.code, start_date=self.start_time, end_date=self.end_time)
        df = df.sort_index(ascending=False)
        df.index = range(len(df))
        self.klines = df
    
    def print_klines(self, ndays):
        print('code is ', self.code)
        print('stard data ', self.start_time)
        print('end data ', self.end_time)

        print(self.klines.head(ndays))


    def stock_days_denoise_with_open_and_close(self):
        #
        df = self.klines.loc[:]
        rows, cols = df.shape
        df['high_b'] = 0
        df['low_b'] = 0

        for i in range(rows):
            if df.loc[i, 'open'] > df.loc[i, 'close']:
                df.loc[i, 'high_b'] = df.loc[i, 'open']
                df.loc[i, 'low_b'] = df.loc[i, 'close']
            else:
                df.loc[i, 'high_b'] = df.loc[i, 'close']
                df.loc[i, 'low_b'] = df.loc[i, 'open']
        self.klines = df

    def stock_days_denoise_with_high_and_low(self):
        #
        df = self.klines.loc[:]
        rows, cols = df.shape
        df['high_b'] = 0
        df['low_b'] = 0

        for i in range(rows):
            df.loc[i, 'high_b'] = df.loc[i, 'high']
            df.loc[i, 'low_b'] = df.loc[i, 'low']
        self.klines = df
    
    def candle_plot(self):
        # print candles, the candle is open/close prices
        # df.to_csv('df.csv')
        # fig, ax = plt.subplots(figsize=(5,3))
        fig = plt.figure(figsize=(20,8))
        # fig = plt.figure(constrained_layout=True)
        gs = GridSpec(3, 3)
        ax1 = fig.add_subplot(gs[0:-1, :])
        for index, row in self.klines.iterrows():
            if row['open'] - row['close'] < 0:
                co = 'r'
            else:
                co = 'g'
            # print(row['high_b']- row['low_b'])
            ax1.add_patch(mp.Rectangle([index, row['low_b']], 0.6, row['high_b'] - row['low_b'], color=co, alpha=0.6))
        print(self.klines.shape)
        print(self.klines['low_b'].min())
        (days, _) = self.klines.shape
        print(days)
        ax1.set_xlim(-1,days + 1)
        ax1.set_ylim(self.klines['low_b'].min(), self.klines['high_b'].max())
        ax1.set_xlabel('days Kline')

        # ax2 = plt.subplot(2,1,2)
        ax2 = fig.add_subplot(gs[2,:])
        ax2.bar(self.klines.index, self.klines['vol'])
        ax2.set_xlim(-1,days + 1)
        ax2.set_ylim(0, self.klines['vol'].max() + 1000)
        ax2.set_xlabel('VOL')
        plt.show()



if __name__ == "__main__":
    
    test = K_line('000001.SZ', '20170102', '20190718')
    test.pro_init()
    test.get_daily_lists()
    test.print_klines(10)
    test.stock_days_denoise_with_high_and_low()
    test.print_klines(10)
    test.candle_plot()
