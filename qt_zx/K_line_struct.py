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

class K_line_struct_base(K_line):
    def __init__(self,  code, start_time, end_time):
        super().__init__(code, start_time, end_time)
        

    def stock_days_denoise(self, method='oc'):
        if method == 'oc':
            self._stock_days_denoise_with_open_and_close()
        else:
            self._stock_days_denoise_with_high_and_low()

    def _stock_days_denoise_with_open_and_close(self):
        # 保留open、close作为当天的最高最低值
        df = self.k_lines.loc[:]        
        df['high_b'] = 0
        df['low_b'] = 0
        for i in range(df.shape[0]):       
            if df.loc[i, 'open'] > df.loc[i, 'close']:
                df.loc[i,'high_b'] = df.loc[i,'open']
                df.loc[i,'low_b'] = df.loc[i,'close']
            else:
                df.loc[i,'high_b'] = df.loc[i,'close']
                df.loc[i,'low_b'] = df.loc[i,'open']
        self.k_lines = df

    def _stock_days_denoise_with_high_and_low(self):
        # 保留high、low作为当天的最高最低值
        df = self.k_lines.loc[:]
        rows, _ = df.shape
        df['high_b'] = 0
        df['low_b'] = 0

        for i in range(rows):
            df.loc[i, 'high_b'] = df.loc[i, 'high']
            df.loc[i, 'low_b'] = df.loc[i, 'low']
        self.k_lines = df

    def _stock_contain_remove(self):
        # 把有包含关系的K线做剔除
        df = self.k_lines.loc[:]
        rows, _ = df.shape

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
    
        rows, _ = self.k_lines.shape
    
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
        line.drop(df.index[0], inplace=True)
        return line

    def _line_filter(self, line):
        # filt line, remove some noise 消除趋势中小的震荡
        line_filt = pd.DataFrame(columns=('id', 'price', 'type'))
        line_filt = line_filt.append(line.iloc[0])
        pre_type = line.iloc[0]['type']
        pre_price = line.iloc[0]['price']
        pre_id = line.iloc[0]['id']

        i = 1
        while i < len(line) - 2:
            cur_price = line.iloc[i]['price']
            cur_id = line.iloc[i]['id']
            cur_type = line.iloc[i]['type']

            nex_price = line.iloc[i + 1]['price']
            nex_id = line.iloc[i + 1]['id']
            nex_type = line.iloc[i + 1]['type']

            nex2_price = line.iloc[i + 2]['price']
            nex2_id = line.iloc[i + 2]['id']
            nex2_type = line.iloc[i + 2]['type']

            if pre_type == 1:
                # top
                if nex2_price < cur_price and nex_price < pre_price\
                        and abs((nex_price - cur_price) / (pre_price - nex2_price)) < 0.3:
                    i += 2
                else:
                    line_filt = line_filt.append(line.iloc[i])
                    i += 1
                    pre_price = cur_price
                    pre_type = cur_type
                    pre_id = cur_id
                continue

            elif pre_type == 2:
                #bot
                if nex2_price > cur_price and nex_price > pre_price\
                        and abs((nex_price - cur_price) / (pre_price - nex2_price)) < 0.3:
                    i += 2
                else:
                    line_filt = line_filt.append(line.iloc[i])
                    i += 1
                    pre_price = cur_price
                    pre_type = cur_type
                    pre_id = cur_id
                continue

        return line_filt

    def strategy_neck_line_print(self):
        ax1 = self.ax1

        df_1 = self._stock_contain_remove()
        line = self._line_plot(df_1)
        ax1.plot(line['id'], line['price'], c='tab:blue', alpha=0.6)
        line = self._line_filter(line)
        # print(line_filt)

        ax1.plot(line['id'], line['price'], c='tab:red', alpha=0.6)

        # print(line)
        if line.iloc[0]['type'] == 1:
            main_center_high = line.iloc[0]['price']
            start_date = line.iloc[0]['id']
            main_center_low = line.iloc[1]['price']
            end_date = line.iloc[1]['id']

        elif line.iloc[0]['type'] == 2:
            main_center_high = line.iloc[1]['price']
            start_date = line.iloc[1]['id']
            main_center_low = line.iloc[2]['price']
            end_date = line.iloc[2]['id']

        # print(main_center_high, main_center_low)

        center_list = pd.DataFrame(columns=['start_date', 'end_date', 'center_high', 'center_low'])
        center_list = center_list.append(pd.Series({'start_date': start_date, 'end_date': end_date,
                                                    'center_high': main_center_high, 'center_low': main_center_low}),
                                         ignore_index=True)
        previous_id = line.iloc[2]['id']
        previous_high = main_center_high
        previous_low = main_center_low
        for _, row in line.iloc[:].iterrows():
            #判断下一个线段和上一个center的关系
            if row['type'] == 1:
                second_center_high = row['price']
                if second_center_high < main_center_low:
                    end_date = previous_id - 1
                    ax1.add_patch(mp.Rectangle([start_date, main_center_low], end_date - start_date,
                                               main_center_high - main_center_low,
                                               color='tab:gray', alpha=0.3))
                    start_date = previous_id
                    main_center_high = row['price']
                    center_list = center_list.append(pd.Series({'start_date': start_date, 'end_date': end_date,
                                                                'center_high': main_center_high,
                                                                'center_low': main_center_low}),
                                                     ignore_index=True)
                    main_center_low = previous_low
                else:
                    previous_high = row['price']
                    previous_id = row['id']
            else:
                second_center_low = row['price']
                # compare_signal = 1
                if second_center_low > main_center_high:
                    end_date = row['id'] - 1
                    ax1.add_patch(mp.Rectangle([start_date, main_center_low], end_date - start_date,
                                               main_center_high - main_center_low,
                                               color='tab:gray', alpha=0.3))
                    start_date = previous_id
                    main_center_low = row['price']
                    main_center_high = previous_high
                    center_list = center_list.append(pd.Series({'start_date': start_date, 'end_date': end_date,
                                                                'center_high': main_center_high,
                                                                'center_low': main_center_low}),
                                                     ignore_index=True)
                else:
                    previous_low = row['price']
                    previous_id = row['id']

        end_date = line.iloc[-1]['id']
        ax1.add_patch(mp.Rectangle([start_date, main_center_low], end_date - start_date,
                                   main_center_high - main_center_low,
                                   color='tab:gray', alpha=0.3))
        print(center_list)


if __name__ == "__main__":
    struct = K_line_struct_base('000001.SZ', '20170102', '20200718')

    struct.candle_plot()
    struct.stock_days_denoise()
    struct.k_lines_mean_plot([20, 60])
    struct.strategy_neck_line_print()
    struct.plot_all()