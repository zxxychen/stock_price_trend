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
        self.pro = 0
        self.k_lines = 0
        self.fig = 0
        self.ax1 = 0
        self.ax2 = 0

    def pro_init(self):
        self.pro = ts.pro_api('d5741f23ebd206c762d2e593573499d5a479b8955ae9b5152c646ba2')

    def get_daily_lists(self):
        # 获取日线数据
        df = self.pro.daily(ts_code=self.code, start_date=self.start_time, end_date=self.end_time)
        df = df.sort_index(ascending=False)
        df.index = range(len(df))
        self.k_lines = df

    def print_k_lines(self, ndays):
        # print some parameters of the instance
        print('code is ', self.code)
        print('start data ', self.start_time)
        print('end data ', self.end_time)

        print(self.k_lines.head(ndays))
        print(self.k_lines.tail(ndays))

    def stock_days_denoise_with_open_and_close(self):
        #
        df = self.k_lines.loc[:]
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
        self.k_lines = df

    def stock_days_denoise_with_high_and_low(self):
        #
        df = self.k_lines.loc[:]
        rows, cols = df.shape
        df['high_b'] = 0
        df['low_b'] = 0

        for i in range(rows):
            df.loc[i, 'high_b'] = df.loc[i, 'high']
            df.loc[i, 'low_b'] = df.loc[i, 'low']
        self.k_lines = df

    def k_lines_mean(self):
        # calculate moving average line
        (days, _) = self.k_lines.shape
        df = self.k_lines
        df['mean_5'] = 0
        df['mean_10'] = 0
        df['mean_30'] = 0
        for i in range(4, days):
            df.loc[i, 'mean_5'] = np.mean(df.loc[i-4:i, 'close'])

        for i in range(9, days):
            df.loc[i, 'mean_10'] = np.mean(df.loc[i-9:i, 'close'])

        for i in range(29, days):
            df.loc[i, 'mean_30'] = np.mean(df.loc[i-29:i, 'close'])

        self.k_lines = df

    def k_lines_mean_plot(self):
        # add moving average line to candle image
        (days, _) = self.k_lines.shape
        ax1 = self.ax1
        ax1.plot(range(4, days), self.k_lines.loc[4:, 'mean_5'], color='b')
        ax1.plot(range(9, days), self.k_lines.loc[9:, 'mean_10'], color='y')
        ax1.plot(range(29, days), self.k_lines.loc[29:, 'mean_30'], color='black')
        self.ax1 = ax1

    def candle_plot(self):
        # plot, the candle is open/close prices
        # plot vol
        # df.to_csv('df.csv')
        # fig, ax = plt.subplots(figsize=(5,3))
        fig = plt.figure(figsize=(16, 8))
        # fig = plt.figure(constrained_layout=True)
        gs = GridSpec(3, 3)
        ax1 = fig.add_subplot(gs[0:-1, :])
        for index, row in self.k_lines.iterrows():
            if row['open'] - row['close'] < 0:
                co = 'r'
            else:
                co = 'g'
            # print(row['high_b']- row['low_b'])
            ax1.add_patch(mp.Rectangle([index, row['low_b']], 0.6, row['high_b'] - row['low_b'], color=co, alpha=0.6))
        print(self.k_lines.shape)
        print(self.k_lines['low_b'].min())
        (days, _) = self.k_lines.shape
        print(days)
        ax1.set_xlim(-1, days + 1)
        ax1.set_ylim(self.k_lines['low_b'].min(), self.k_lines['high_b'].max())
        ax1.set_xlabel('days Kline')

        # ax2 = plt.subplot(2,1,2)
        ax2 = fig.add_subplot(gs[2, :])
        ax2.bar(self.k_lines.index, self.k_lines['vol'])
        ax2.set_xlim(-1, days + 1)
        ax2.set_ylim(0, self.k_lines['vol'].max() + 1000)
        ax2.set_xlabel('VOL')
        # plt.show()
        self.fig = fig
        self.ax1 = ax1
        self.ax2 = ax2
        return fig, ax1, ax2

    def k_lines_plot_all(self):
        # 画图，显示所有调用过的图像
        fig = self.fig
        ax1 = self.ax1
        ax2 = self.ax2
        print(self.code + '.png')
        # fig.savefig(self.code + '.png')
        plt.show(fig)

    def _stock_contain_remove(self):
        df = self.k_lines.loc[:]
        rows, cols = df.shape

        # first: clean contain relationships
        for i in range(rows):
            # state = 1: rise 2:fall
            if i == 0:
                if df.loc[i+1, 'high_b'] > df.loc[i, 'high_b'] and df.loc[i+1, 'low_b'] > df.loc[i, 'low_b']:
                    state = 1
                elif df.loc[i+1, 'high_b'] < df.loc[i, 'high_b'] and df.loc[i+1, 'low_b'] < df.loc[i, 'low_b']:
                    state = 2
                else:
                    state = 1

            else:
                if df.loc[i, 'high_b'] > df.loc[i-1, 'high_b'] and df.loc[i, 'low_b'] > df.loc[i-1, 'low_b']:
                    #price rise
                    pass
                elif df.loc[i, 'high_b'] < df.loc[i-1, 'high_b'] and df.loc[i, 'low_b'] < df.loc[i-1, 'low_b']:
                    #price fall
                    pass
                elif df.loc[i, 'high_b'] < df.loc[i-1, 'high_b'] and df.loc[i, 'low_b'] > df.loc[i-1, 'low_b']:
                    #contain: i-1 contain i
                    if state == 1:
                        df.loc[i-1, 'low_b'] = df.loc[i, 'low_b']
                    else:
                        df.loc[i-1, 'high_b'] = df.loc[i, 'high_b']
                elif df.loc[i, 'high_b'] > df.loc[i-1, 'high_b'] and df.loc[i, 'low_b'] < df.loc[i-1, 'low_b']:
                    # contain: i contain i-1
                    if state == 1:
                        df.loc[i, 'low_b'] = df.loc[i-1, 'low_b']
                    else:
                        df.loc[i, 'high_b'] = df.loc[i-1, 'high_b']
                else:
                    pass
        return df

    def _line_plot(self, df):
        # after contain remove, draw the lines
        # in line: type: 1:top, 2:bot
        line = pd.DataFrame(columns=('id', 'price', 'type'))
        # deal with first line
        line = line.append(pd.DataFrame({'id':[0], 'price':[df.loc[0, 'open']], 'type':[1]}))
    
        rows, cols = self.k_lines.shape
    
        for i in range(rows):
            if i == 0 or i == rows-1:
                pass
            else:
                if df.loc[i, 'high_b'] >= df.loc[i-1, 'high_b'] and df.loc[i, 'high_b'] >= df.loc[i+1, 'high_b']:
                    line = line.append(pd.DataFrame({'id':[i], 'price':[df.loc[i, 'high_b']], 'type':[1]}), ignore_index=True)
                elif df.loc[i, 'low_b'] <= df.loc[i-1, 'low_b'] and df.loc[i, 'low_b'] <= df.loc[i+1, 'low_b']:
                    line = line.append(pd.DataFrame({'id':[i], 'price':[df.loc[i, 'low_b']], 'type':[2]}), ignore_index=True)
                else:
                    pass
    
        # deal with last line
        line = line.append(pd.DataFrame({'id':[rows-1], 'price':[df.loc[rows -1, 'close']], 'type':[2]}), ignore_index=True)
        # line.to_csv('line.csv')
        cnt = 100
        while cnt != 0:
            cnt = 0
            for i in range(len(line)):
                if i == 0 or i == len(line) - 1:
                    pass
                else:
                    if line.loc[i, 'type'] == 1:
                        if line.loc[i + 1, 'type'] == 1:
                            if line.loc[i+1, 'price'] >= line.loc[i, 'price']:
                                line.loc[i, 'type'] = 0
                                cnt += 1
                            else:
                                line.loc[i+1, 'type'] = 0
                                cnt += 1
                    elif line.loc[i, 'type'] == 2:
                        if line.loc[i + 1, 'type'] == 2:
                            if line.loc[i+1, 'price'] <= line.loc[i, 'price']:
                                line.loc[i, 'type'] = 0
                                cnt += 1
                            else:
                                line.loc[i+1, 'type'] = 0
                                cnt += 1
            line = line[~line['type'].isin([0])]
            line.index = range(len(line))
    
        # line.to_csv('line2.csv')
    
        return line


    def strategy_neck_line_print(self):
        df = self.k_lines
        fig = self.fig
        ax1 = self.ax1
        main_center_high = 0
        main_center_low = 0

        df_1 = self._stock_contain_remove()
        line = self._line_plot(df_1)
        print(line)


    def strategy_average_system_test(self):
        # 均线策略 测试
        df = self.k_lines
        trade_info = pd.DataFrame(columns=['buy_date', 'buy', 'sold_date', 'sold'])
        # 准备入场信号
        ready_state = 0
        # 准备买信号
        pre_buy_state = 0
        # 上一购买状态信号
        previous_buy_state = 0
        trade_count = 0

        for index, row in df.iterrows():
            if index == 29:
                # 初始状态设置
                pass
            if index >= 30:
                # 开始计算30日均线
                # 所有操作需要在30日均线上方
                if row['mean_10'] > row['mean_30']:
                    # State 1
                    ready_state = 1
                else:
                    # State 0
                    ready_state = 0

                # 买需要5日均线在10日均线上方
                if ready_state == 1:
                    if row['mean_5'] < row['mean_10']:
                        # State 2
                        pre_buy_state = 0
                    else:
                        # State 3
                        pre_buy_state = 1
                else:
                    pre_buy_state = 0

                # 买操作需要 5日均线 上穿 10日均线
                if previous_buy_state == 0:
                    if pre_buy_state == 1:
                        trade_info.loc[trade_count, 'buy'] = row['close']
                        trade_info.loc[trade_count, 'buy_date'] = index
                    else:
                        pass
                else:
                    if pre_buy_state == 1:
                        pass
                    else:
                        trade_info.loc[trade_count, 'sold'] = row['close']
                        trade_info.loc[trade_count, 'sold_date'] = index
                        trade_count += 1
                previous_buy_state = pre_buy_state

        print('total trade count is', trade_count)
        print(trade_info)
        if np.isnan(trade_info.loc[trade_info.shape[0]-1, 'buy']):
            trade_info = trade_info.drop(trade_info.shape[0])
        else:
            if np.isnan(trade_info.loc[trade_info.shape[0]-1, 'sold']):
                trade_info.loc[trade_count, 'sold'] = df.iloc[-1]['close']

        # trade_info 统计 1手 增长
        cap_increase = 0
        ax = self.ax1
        for index, row in trade_info.iterrows():
            cap_increase += row['sold'] - row['buy']
            ax.axvspan(row['buy_date'], row['sold_date'], facecolor='tab:gray', alpha=0.3)
        cap_total = trade_info.loc[0, 'buy'] + cap_increase
        print('initial  price = ', trade_info.loc[0, 'buy'], 'final cap = ', cap_total, 'increase = ', cap_increase)

        start_price = df.iloc[29]['close']
        end_price = df.iloc[-1]['close']
        percentage = (end_price - start_price) / start_price * 100
        print('initial  price = ', df.loc[29, 'close'], 'final cap = ', df.iloc[-1]['close'], 'increase = ',
              df.iloc[-1]['close'] - df.loc[29, 'close'])

        ax.set(title=[self.code, 'initial  price = {:.2f}', trade_info.loc[0, 'buy'], 'final cap = ', cap_total,
                      'increase = ', cap_increase])


if __name__ == "__main__":
    test = K_line('000001.SZ', '20170102', '20190718')
    test.pro_init()
    test.get_daily_lists()
    # test.print_k_lines(10)
    test.stock_days_denoise_with_high_and_low()
    test.k_lines_mean()
    test.print_k_lines(10)
    # test.candle_plot()
    # test.k_lines_mean_plot()
    # test.strategy_average_system_test()
    # test.k_lines_plot_all()
    test.strategy_neck_line_print()
    test.print_k_lines(10)

