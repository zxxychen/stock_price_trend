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
    def __init__(self, code, start_time, end_time, get_klines=True):
        """
        初始化，
        code: 股票代码，以 .SZ .SH 结尾
        start_time: 起始时间
        end_time: 结束时间
        """
        self.code = code
        # self.period = period
        self.start_time = start_time
        self.end_time = end_time
        if get_klines:
            self._get_daily_lists()
        self.fig = plt.figure(figsize=(15, 7))
        gs = GridSpec(3, 3)
        self.ax1 = self.fig.add_subplot(gs[0:-1, :])
        self.ax1.grid(True)
        self.ax2 = self.fig.add_subplot(gs[2, :])
        print('K_line {} download end'.format(self.code))

    def _get_daily_lists(self):
        # 获取日线数据
        # df = self.pro.daily(ts_code=self.code, start_date=self.start_time, end_date=self.end_time)
        ts.set_token('d5741f23ebd206c762d2e593573499d5a479b8955ae9b5152c646ba2')
        df = ts.pro_bar(ts_code=self.code, adj='qfq', start_date=self.start_time, end_date=self.end_time,
                        ma=[5, 20, 60])
        df = df.sort_index(ascending=False)
        df.index = range(len(df))
        df['key'] = np.arange(len(df))
        df.to_csv('./gen/'+self.code+'.csv', columns=df.columns, index=True)
        self.k_lines = df

    def load_temp_csv(self):
        self.k_lines = pd.read_csv('./gen/temp.csv', index_col=0)

    def print_k_lines(self, ndays=None):
        # print some parameters of the instance
        print('code is ', self.code)
        print('start data ', self.start_time)
        print('end data ', self.end_time)
        if ndays==None:
            ndays = 5
        print(self.k_lines.head(ndays))
        print(self.k_lines.tail(ndays))

    

    def k_lines_mean_plot(self, malist):
        # add moving average line to candle image
        (days, _) = self.k_lines.shape
        ax1 = self.ax1
        if malist is not None:
            for ma in malist:
                print(ma, type(ma))
                ax1.plot(np.arange(0, days).astype(float)+0.5, self.k_lines['close'].rolling(ma).mean(), alpha=0.8)
        else:
            ax1.plot(np.arange(4, days).astype(float)+0.5, self.k_lines.loc[4:, 'ma5'], color='b', alpha=0.8)
            ax1.plot(np.arange(9, days).astype(float)+0.5, self.k_lines.loc[9:, 'ma20'], color='y', alpha=0.8)
            ax1.plot(np.arange(29, days).astype(float)+0.5, self.k_lines.loc[29:, 'ma60'], color='c', alpha=0.8)
        self.ax1 = ax1

    def k_lines_BOLL_plot(self, N):
        # add moving average line to candle image
        (days, _) = self.k_lines.shape
        ax1 = self.ax1
        # 先画出N日均线
        kl_pd = self.k_lines
        kl_pd.loc[:, 'N1mean'] = self.k_lines['close'].rolling(N).mean()
        ax1.plot(np.arange(0, days).astype(float)+0.5, kl_pd.N1mean, alpha=0.8, color='K')
        # 求标准差
        kl_pd.loc[:, 'std1'] = kl_pd.close - kl_pd.N1mean
        kl_pd.loc[:, 'std1'] = kl_pd['std1'].rolling(N).std()
        kl_pd.loc[:, 'up'] = kl_pd.N1mean + 2 * kl_pd.loc[:,'std1']
        kl_pd.loc[:, 'dn'] = kl_pd.N1mean - 2 * kl_pd.loc[:, 'std1']
        ax1.fill_between(kl_pd.key.astype(float) + 0.5,\
             kl_pd.dn.shift(10), kl_pd.up.shift(1), \
                 color='red', alpha=0.2)
        
        self.ax1 = ax1

    def candle_plot(self, ax2_type='val'):
        fig = self.fig
        ax1 = self.ax1
        ax2 = self.ax2
        
        for index, row in self.k_lines.iterrows():
            if row['open'] - row['close'] < 0:
                co = 'r'
                day_high = row.close
                day_low = row.open
            else:
                co = 'g'
                day_high = row.open
                day_low = row.close
            # print(row['high_b']- row['low_b'])
            ax1.add_patch(mp.Rectangle([index, day_low], 0.8, day_high - day_low, color=co, alpha=0.6))
            ax1.add_patch(mp.Rectangle([index+0.35, row['low']], 0.1, row['high'] - row['low'], color=co, alpha=0.4))
        # print(self.k_lines.shape)
        # print(self.k_lines['low_b'].min())
        (days, _) = self.k_lines.shape
        # print(days)
        ax1.set_xlim(-1, days + 1)
        ax1.set_ylim(self.k_lines['low'].min() - 1, self.k_lines['high'].max() + 1)
        ax1.set_xlabel('days Kline')

        ax2.bar(self.k_lines.index, self.k_lines['vol'])
        ax2.set_xlim(-1, days + 1)
        ax2.set_ylim(0, self.k_lines['vol'].max() + 1000)
        ax2.set_xlabel('VOL')
        return 

    def plot_all(self, save=False):
        # 画图，显示所有调用过的图像
        if save == True:
            print(self.code + '.png')
            self.fig.savefig(self.code + '.png')
        plt.show(self.fig)

    

if __name__ == "__main__":
    test = K_line('000001.SZ', '20180102', '20201231',get_klines=True)
    test.k_lines_mean_plot([20,5, 60])
    test.candle_plot()
    # test.plot_all()

    test2 = K_line('600105.SH', '20180102', '20201231',get_klines=True)
    test2.k_lines_mean_plot([20,5, 60])
    test2.candle_plot()
    test2.plot_all()


