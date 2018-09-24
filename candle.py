import matplotlib as mpl
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mp
import numpy as np
import tushare as ts
from matplotlib.pylab import date2num
import datetime

def date_to_num(dates, timecard):
    num_time = []
    if timecard == 'D':
        for date in dates:
            date_time = datetime.datetime.strptime(date,'%Y-%m-%d')
            num_date = date2num(date_time)
            num_time.append(num_date)
    elif timecard == '30':
        for date in dates:
            date_time = datetime.datetime.strptime(date,'%Y-%m-%d %H:%M')
            num_date = date2num(date_time)
            num_time.append(num_date)
    return num_time


def candle_plot(ax, price, alp):
    #price[0]:date, price[1]:open, price[2]: close, price[3]: high, price[4]:low
    #print(price.shape)

    for p in price:
        if p[1]-p[2] >0:
            co = 'g'
        else:
            co = 'r'
        ax.add_patch(mp.Rectangle([p[0], p[4]], 0.6, p[3]-p[4], color= co, alpha=alp ))
    return ax

def k_contain_detect(pre_p,cur_p,nex_p):
    #  cur high   pre high     cur low      cur high
    if cur_p[3] > pre_p[3] and cur_p[4] > pre_p[4]:
        # next high   cur high     next low    cur low
        if nex_p[3] >= cur_p[3] and nex_p[4] <= cur_p[4]:
            return 1 #up cur < next

        if nex_p[3] <= cur_p[3] and nex_p[4] >= cur_p[4]:
            return 2 #up cur > next
    if cur_p[3] <  pre_p[3] and cur_p[4] < pre_p[4]:
        if nex_p[3] >= cur_p[3] and nex_p[4] <= cur_p[4]:
            return 3 #down cur < next
        if nex_p[3] <= cur_p[3] and nex_p[4] >= cur_p[4]:
            return 4 #down cur > next
    return 0

def data_clean(pin):
    price = pin.copy()
    rows,cols = price.shape
    prev_p = price[0]
    cur_p = price[1]
    c_i = 1

    for i in range(1,rows-2):
        next_p = price[i+1]
        n_i = i+1
        res = k_contain_detect(prev_p, cur_p, next_p)
        if res == 0:
            prev_p = cur_p
            cur_p = next_p
            c_i = n_i

        elif res == 1:
            next_p[4] = cur_p[4]
            cur_p = next_p
            c_i = n_i
            price[n_i, 4] = next_p[4]

        elif res == 2:
            cur_p[4] = next_p[4]
            price[c_i, 4] = cur_p[4]
            # c_i = n_i

        elif res == 3:
            next_p[3] = cur_p[3]
            cur_p = next_p
            c_i = n_i
            price[n_i,3] = next_p[3]

        elif res == 4:
            cur_p[3] = next_p[3]
            price[c_i, 3] = cur_p[3]
            # c_i = n_idata_clean_select
    return price

def data_clean_select(pin):
    price = pin[0:1]
    rows,cols = pin.shape
    print(rows, cols)
    for i in range(2, rows-1):
        # print (price[-1])
        # if i == 159:
        #     i = 159
        if pin[i, 3] >= price[-1,3] and pin[i,4] <= price[-1,4]:
            if pin[i, 3] == price[-1,3] and pin[i,4] == price[-1,4]:
                pass
            else:
                price = np.delete(price, -1, 0)
                price = np.vstack((price,pin[i]))
        elif pin[i, 3] <= price[-1,3] and pin[i,4] >= price[-1,4]:
            pass
        else:
            price = np.vstack((price,pin[i]))
    rows, cols = price.shape
    print(rows, cols)
    price = np.hstack((price, np.arange(rows).reshape(-1,1)))
    return price


def find_strokes(pin):
    price = pin.copy()
    rows, cols = price.shape
    # 0:data_num  1: price, 2: top1/bot2 3:new_index after contain detect
    line = []
    for i in range(1, rows - 1):
        prev_p = price[i-1]
        cur_p = price[i]
        next_p = price[i+1]
        if cur_p[3] > prev_p[3] and cur_p[3] > next_p[3]:
            line.append([cur_p[0], cur_p[3], 1 , cur_p[7]]) #top
        if cur_p[4] < prev_p[4] and cur_p[4] < next_p[4]:
            line.append([cur_p[0], cur_p[4], 2, cur_p[7]]) #bottom
        else:
            pass
    if price[rows - 1, 3] > price[rows - 2, 3]:
        line.append([price[rows - 1, 0], price[rows - 1, 3], 1, price[rows - 1, 7]])
    elif price[rows - 1, 4] < price[rows - 2, 4]:
        line.append([price[rows - 1, 0], price[rows - 1, 4], 1, price[rows - 1, 7]])
    line = np.array(line)
    # print(line)
    rows, cols = line.shape
    print(rows, cols)
    stroke = line[0]

    for i in range(1, rows - 1 ):
        prev_p = line[i-1]
        cur_p = line[i]
        next_p = line[i+1]

        if next_p[1] >= cur_p[1] >= prev_p[1] or next_p[1] <= cur_p[1] <= prev_p[1]:
            pass
        # elif cur_p[2] == prev_p[2] and cur_p[2] == next_p[2]:
        #     pass
        else:
            stroke = np.vstack((stroke,cur_p))
    # stroke = np.vstack((stroke, line[rows - 1, :]))
    stroke = np.vstack((stroke, line[rows-1,:]))
    return stroke

def clean_strokes(pin):
    #pin : 0:data_num  1: price, 2: top1/bot2
    rows, cols = pin.shape
    i = 0
    while i < rows:
        if pin[i+1, 0] - pin[i, 0] >= 4 and pin[i+1, 3] - pin[i, 3] >= 3:
            break
        else:
            i += 1
    strokes = pin[i,:]
    # strokes = np.vstack((strokes, pin[i+1]))
    i += 1
    while i < rows-2:
        test = pin[i,0]
        if pin[i+1,0] - pin[i, 0] >= 4 and pin[i+1, 3] - pin[i, 3] >= 3 \
                and pin[i, 3] - strokes[-1, 3] > 2 and pin[i, 0] - strokes[-1, 0] > 3:
            strokes = np.vstack((strokes, pin[i]))
            i += 1
        else:
            if pin[i, 2] == 2:

                while pin[i+2,1] < pin[i, 1]:# or pin[i+1, 2] < high and pin[i+2, 2] > low:
                    if pin[i+1, 3] - pin[i, 3] > 2 and pin[i+1, 0] - pin[i, 0] > 3 \
                            and pin[i, 3] - strokes[-1, 3] > 2 and pin[i, 0] - strokes[-1, 0] > 3 :
                        break
                    i += 2
                    if i + 2 >= rows:
                        break
                if i+3 < rows-1 and pin[i+3, 1] < pin[i+1, 1] and pin[i+1,1] < pin[i-1,1]:
                    if pin[i+1, 3] - pin[i, 3] > 2 and pin[i+1, 0] - pin[i, 0] > 3:
                        strokes = np.vstack((strokes, pin[i]))
                        i += 1
                    else:
                        pin = np.delete(pin, [i + 2, i + 3], 0)
                        rows, cols = pin.shape

                else:
                    strokes = np.vstack((strokes, pin[i]))
                    i += 1

            else:
                while pin[i+2, 1] > pin[i, 1]:
                    if pin[i+1, 3] - pin[i, 3] > 2 and pin[i+1, 0] - pin[i, 0] > 3 \
                            and pin[i, 3] - strokes[-1, 3] > 2 and pin[i, 0] - strokes[-1, 0] > 3:
                        break
                    i += 2
                    if i + 2 >= rows :
                        break
                if i+3 < rows-1 and pin[i+3, 1] > pin[i+1, 1] and pin[i+1,1] > pin[i-1,1]:
                    if pin[i+1, 3] - pin[i, 3] > 2 and pin[i+1, 0] - pin[i, 0] > 3:
                        strokes = np.vstack((strokes, pin[i]))
                        i += 1
                    else:
                        pin = np.delete(pin, [i+2, i+3], 0)
                        rows, cols = pin.shape
                else:
                    strokes = np.vstack((strokes, pin[i]))
                    i += 1
    return strokes #, count

def count_uncleaned_strokes(pin):
    rows, cols = pin.shape
    pout = pin[0,:]
    i = 0
    while i < rows - 2:
        if pin[i + 1, 0] - pin[i, 0] <= 3:
            if pin[i, 2] == 1:
                if pin[i + 2, 1] > pin[i, 1]:
                    pout[-1] = pin[i+2]
                    i += 2
                else:
                    pout = np.vstack((pout, pin[i]))
                    if i + 3 > rows - 1:
                        break
                    pout = np.vstack((pout, pin[i + 3]))
                    i += 3
            else:
                if pin[i + 2, 1] < pin[i, 1]:
                    pout[-1] = pin[i+2]
                    i += 2
                else:
                    pout = np.vstack((pout, pin[i]))
                    if i + 3 > rows - 1:
                        break
                    pout = np.vstack((pout, pin[i + 3]))
                    i += 3
        else:
            pout = np.vstack((pout, pin[i + 1]))
            i += 1
    return pout


def EMA_12(pin):
    pass

def find_center(pin):
    pass



ktype_in = 'D'
wdyx = ts.get_k_data('000001', ktype=ktype_in,start='2017-01-01') #600690
mat = wdyx.as_matrix()



num_time = date_to_num(mat[:,0], timecard=ktype_in)
mat[:,0] = num_time
rows,cols = mat.shape
n = np.arange(0,rows,1)
mat[:,0] = n
#print(mat)
mat_clean = data_clean(mat)

fig, ax = plt.subplots(figsize=(15,8))

ax = candle_plot(ax, mat_clean, 1)
# print(mat_clean[380:386])
price_clean = data_clean_select(mat_clean)
# print(price_clean)

line = find_strokes(price_clean)
# print(line)
strokes = clean_strokes(line)
# strokes = count_uncleaned_strokes(strokes)
print(strokes)
# pd.DataFrame(mat).to_csv("mat.csv")
# pd.DataFrame(mat_clean).to_csv("mat2.csv")
# pd.DataFrame(line).to_csv("line.csv")

plt.plot(line[:,0]+0.5, line[:,1], c='y',alpha=0.8)
plt.plot(strokes[:,0]+0.5, strokes[:,1])


plt.ylim((np.min(mat[:, 1:4])-1, np.max(mat[:,1:4])+1))
plt.xlim((mat_clean[0,0]-1,mat_clean[-1,0]+1))
plt.show()