# -*- coding:utf-8 -*-
import matplotlib as mpl
import tushare as ts
import matplotlib.pyplot as plt
from matplotlib import finance as mpf
# 导入两个涉及的库
from matplotlib.pylab import date2num
import datetime
import pandas as pd


wdyx = ts.get_k_data('600000', ktype='D',start='2018-01-01')
wdyx.info()

def date_to_num(dates):
    num_time = []
    for date in dates:
        date_time = datetime.datetime.strptime(date,'%Y-%m-%d')
        num_date = date2num(date_time)
        num_time.append(num_date)
    return num_time
# dataframe转换为二维数组
mat_wdyx = wdyx.as_matrix()
print(mat_wdyx[:3])
num_time = date_to_num(mat_wdyx[:,0])
mat_wdyx[:,0] = num_time
#         日期,   开盘,     收盘,    最高,      最低,   成交量,    代码
print(mat_wdyx[:3])

fig, ax = plt.subplots(figsize=(15,8))
#fig.subplots_adjust(bottom=0.5)
#mpf.candlestick_ochl(ax, mat_wdyx, width=0.6, colorup='g', colordown='r', alpha=0.1)
plt.grid(True)
# 设置日期刻度旋转的角度
plt.xticks(rotation=30)
plt.title('600000')
plt.xlabel('Date')
plt.ylabel('Price')
#plt.ylim((10,20))
for price in mat_wdyx:
    ax.axvline(x=price[0], ymax=price[3], ymin=price[4], linewidth=5,color='r', alpha=1)

# # x轴的刻度为日期
#ax.xaxis_date ()


# data =  pd.read_csv('top.csv')
# data.dropna(axis=0, inplace=True)
# print(data.head())
# mat_data = data.as_matrix()
# data_time = date_to_num(mat_data[:,0])
# mat_data[:, 0] = data_time
# #print('halhahha', mat_data[:5])
# ax.plot(mat_data[:,0], mat_data[:, 9])

#plt.show()
###candlestick_ochl()函数的参数
# ax 绘图Axes的实例
# mat_wdyx 价格历史数据
# width    图像中红绿矩形的宽度,代表天数
# colorup  收盘价格大于开盘价格时的颜色
# colordown   低于开盘价格时矩形的颜色
# alpha      矩形的颜色的透明度

# fig, (ax1, ax2) = plt.subplots(2, sharex=True, figsize=(15,8))
# mpf.candlestick_ochl(ax1, mat_wdyx, width=0.6, colorup = 'g', colordown = 'r')
# ax1.set_title('600000')
# ax1.set_ylabel('Price')
# ax1.grid(True)
# ax1.xaxis_date()
# #plt.bar(mat_wdyx[:,0]-0.25, mat_wdyx[:,5], width= 0.5)
# ax2.bar(mat_wdyx[:,0]-0.25, mat_wdyx[:,5], width= 0.5)
# ax2.set_ylabel('Volume')
# ax2.grid(True)
plt.show()



