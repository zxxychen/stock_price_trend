import matplotlib as mpl
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mp
import numpy as np
import tushare as ts
from matplotlib.pylab import date2num
import datetime

def pro_init():
    pro = ts.pro_api('d5741f23ebd206c762d2e593573499d5a479b8955ae9b5152c646ba2')
    return pro

def stock_days_denoise(df):
    #
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
    return df

def candle_plot(ax, df):
    # print candles, the candle is open/close prices
    # df.to_csv('df.csv')
    for index, row in df.iterrows():
        if row['open'] - row['close'] < 0:
            co = 'r'
        else:
            co = 'g'
        # print(row['high_b']- row['low_b'])
        ax.add_patch(mp.Rectangle([index, row['low_b']], 0.6, row['high_b'] - row['low_b'], color=co, alpha=0.6))
    return ax

def stock_contain_remove(df):
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

def line_plot(df):
    # after contain remove, draw the lines
    # in line: type: 1:top, 2:bot
    line = pd.DataFrame(columns=('id', 'price', 'type'))
    # deal with first line
    line = line.append(pd.DataFrame({'id':[0], 'price':[df.loc[0, 'open']], 'type':[1]}))

    rows, cols = df.shape

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

def get_daily_lists(pro, code, start_d, end_d):
    df = pro.daily(ts_code=code, start_date=start_d, end_date=end_d)
    df = df.sort_index(ascending=False)
    df.index = range(len(df))
    return df

pro = pro_init()
df = get_daily_lists(pro, '000001.SZ', '20180701', '20190718')
# df.to_csv('df.csv')
df = stock_days_denoise(df)
# print(df)
df = stock_contain_remove(df)
line = line_plot(df)
# print(line)
fig, ax = plt.subplots(figsize=(5,3))
ax = candle_plot(ax, df)
plt.plot(line['id'] + 0.5, line['price'])
plt.show()