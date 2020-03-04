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
from global_paras import *
from abc import ABCMeta, abstractmethod
from qt_base import K_line
from ProcessBase import Qt_buy_base, Qt_sell_base


class struct_cls:
    def __init__(self, name='range', id_start=0, id_end=0, price_max=0, price_min=0, price_line_lists=list()):
        self.name = name # 'trend' or 'range'
        self.id_start = id_start
        self.id_end = id_end
        self.price_max = price_max
        self.price_min = price_min
        self.price_line_lists = price_line_lists
    def __str__(self):
        out = 'name:{}, start:{}, end:{}, max:{}, min:{}'.format(self.name, self.id_start, self.id_end,\
                                                    self.price_max, self.price_min)
        return out


class Buy_yao(Qt_buy_base):
    def __init__(self, kl_pd, **kwargs):
        print('----init---{}'.format(self.__class__.__name__))
        super().__init__(kl_pd)
        self._init_self(**kwargs)
        self.pre_key = 0 
        self.now_state = DN # 0:go down  1:go up

        self.line_base = pd.DataFrame(columns=['id', 'price','vertex'])
        self.line_simple = pd.DataFrame(columns=['id', 'price','vertex'])
        self.struct_parts = pd.DataFrame(columns=['id', 'price','vertex'])
        self.struct_list = list()

        self.line_base_ref = 0 #化简line_base时的参考id，当前化简到某一天了。从第三天开始
        self.line_simple_ref = 2 #化简line_simple时的参考id，当前化简到某一天了。从第三天开始

    def _init_self(self, **kwargs):
        self.xd =  kwargs['xd1']
        if 'pre_time' in kwargs:
            self.pre_time = kwargs['pre_time']
        else:
            self.pre_time = 60
        self.ax = kwargs['ax']


    def _line_for_basic(self, today):
        #所有 line_base 是当天之前完成的折线线段，顶点之后的线段（如：BOT之后一直上升，则不画出线段，直到下一个TOP出现才完成当前线段）
        day_ind = today.key
        kl_pd = copy.deepcopy(self.kl_pd)

        if kl_pd.open[day_ind] > kl_pd.close[day_ind]:
            kl_pd.loc[day_ind, 'hi'] = kl_pd.open[day_ind]
            kl_pd.loc[day_ind, 'lo'] = kl_pd.close[day_ind]
        else:
            kl_pd.loc[day_ind, 'hi'] = kl_pd.close[day_ind]
            kl_pd.loc[day_ind, 'lo'] = kl_pd.open[day_ind]

        #第一天  定义初始值
        if day_ind == 0:
            if kl_pd.open[day_ind] > kl_pd.close[day_ind]: #下跌
                self.pre_price = kl_pd.hi[day_ind]
                self.pre_key = day_ind
                self.now_state = DN
                self.line_base = self.line_base.append({'id':day_ind, 'price':kl_pd.hi[day_ind], 'vertex': TOP}, ignore_index=True)

            else: #上涨
                self.pre_price = kl_pd.lo[day_ind]
                self.pre_key = day_ind
                self.now_state = UP
                self.line_base = self.line_base.append({'id':day_ind, 'price':kl_pd.lo[day_ind], 'vertex': BOT}, ignore_index=True)

        else:
            
            # 寻找顶点 
            if self.now_state == UP:
                if kl_pd.hi[self.pre_key] < kl_pd.hi[day_ind] and kl_pd.lo[self.pre_key] < kl_pd.lo[day_ind]: #继续涨
                    self.pre_key = day_ind
                elif kl_pd.hi[self.pre_key] < kl_pd.hi[day_ind] and kl_pd.lo[self.pre_key] >= kl_pd.lo[day_ind]: #继续涨
                    self.pre_key = day_ind
                elif kl_pd.hi[self.pre_key] > kl_pd.hi[day_ind] and kl_pd.lo[self.pre_key] > kl_pd.lo[day_ind]:#转跌
                    self.line_base = self.line_base.append({'id':self.pre_key, 'price':kl_pd.hi[self.pre_key], 'vertex': TOP}, ignore_index=True)
                    self.now_state = DN
                    self.pre_key = day_ind
                else:
                    pass
                                    
            else:
                if kl_pd.hi[self.pre_key] > kl_pd.hi[day_ind] and kl_pd.lo[self.pre_key] > kl_pd.lo[day_ind]: #继续跌
                    self.pre_key = day_ind
                elif kl_pd.hi[self.pre_key] < kl_pd.hi[day_ind] and kl_pd.lo[self.pre_key] >= kl_pd.lo[day_ind]: #继续跌
                    self.pre_key = day_ind
                elif kl_pd.hi[self.pre_key] < kl_pd.hi[day_ind] and kl_pd.lo[self.pre_key] < kl_pd.lo[day_ind]:#转涨
                    self.line_base = self.line_base.append({'id':self.pre_key, 'price':kl_pd.lo[self.pre_key], 'vertex': BOT}, ignore_index=True)
                    self.now_state = UP
                    self.pre_key = day_ind
                else:
                    pass

        if(day_ind == self.kl_pd.iloc[-1].key):
            if self.now_state == UP:
                self.line_base = self.line_base.append({'id':self.pre_key, 'price':kl_pd.hi[self.pre_key], 'vertex': TOP}, ignore_index=True)
            else:
                self.line_base = self.line_base.append({'id':self.pre_key, 'price':kl_pd.lo[self.pre_key], 'vertex': BOT}, ignore_index=True)
            self.ax.plot(self.line_base['id'], self.line_base['price'], c='tab:blue', alpha=0.5)
        self.kl_pd = kl_pd
        return

    def _line_simplify(self, today):
        # 把line_base进行化简，尽量显示大一点的趋势
        day_ind = today.key
        line_base = self.line_base
        if self.line_simple.shape[0] == 0 and self.line_base.shape[0] > 1:
            self.line_simple = self.line_simple.append(line_base.iloc[0:2], ignore_index=True)
            self.line_base_ref = 1
        
        if line_base.shape[0] > 1 and self.line_base_ref < self.line_base.index[-1]:
            line_base_start = self.line_base_ref
            while self.line_base_ref < self.line_base.index[-1]:
                # print('line_simplify:', day_ind, line_base_start, self.line_base.index[-1])
                if line_base.iloc[line_base_start+1].id - line_base.iloc[line_base_start].id >= self.xd and \
                    self.line_simple.iloc[-1].vertex != self.line_base.iloc[line_base_start+1].vertex:
                     # 这里 xd 应该可以自定义
                    self.line_simple = self.line_simple.append(self.line_base.iloc[line_base_start+1])
                    self.line_base_ref += 1
                    line_base_start = self.line_base_ref
                else:
                        #如果下一阶段和前一阶段差不多，则保留，阈值暂定为60%
                    diff_pre = self.line_simple.iloc[-1].price - self.line_simple.iloc[-2].price
                    diff_now = self.line_simple.iloc[-1].price - self.line_base.iloc[line_base_start+1].price
                    if abs(diff_now / diff_pre) >= 0.6:
                        self.line_simple = self.line_simple.append(self.line_base.iloc[line_base_start+1])
                        self.line_base_ref += 1
                        line_base_start = self.line_base_ref
 
                    else:
                        # #思路三
                        # #接着再往下看一段, 寻找突破峰值的下一个点
                        temp_base_id = line_base_start+2
                        # print('---line_simplify:', day_ind, line_base_start, self.line_base.index[-1])
                        while self.line_base.index[-1] > temp_base_id:
                            if self.line_base.iloc[line_base_start].vertex == TOP:
                                if self.line_base.iloc[temp_base_id].vertex == TOP and \
                                    self.line_base.iloc[temp_base_id].price > self.line_base.iloc[line_base_start].price:
                                    # 突破 top
                                    self.line_simple.iloc[-1].id = self.line_base.iloc[temp_base_id].id
                                    self.line_simple.iloc[-1].price = self.line_base.iloc[temp_base_id].price
                                    self.line_base_ref = temp_base_id
                                    break

                                if self.line_base.iloc[temp_base_id].vertex == BOT and \
                                    self.line_base.iloc[temp_base_id].price < self.line_base.iloc[line_base_start+1].price:
                                    # 下一个bot突破
                                    self.line_simple = self.line_simple.append(self.line_base.iloc[temp_base_id])
                                    self.line_base_ref = temp_base_id
                                    break

                            if self.line_base.iloc[line_base_start].vertex == BOT:
                                if self.line_base.iloc[temp_base_id].vertex == BOT and \
                                    self.line_base.iloc[temp_base_id].price < self.line_base.iloc[line_base_start].price:
                                    # 突破 bot
                                    self.line_simple.iloc[-1].id = self.line_base.iloc[temp_base_id].id
                                    self.line_simple.iloc[-1].price = self.line_base.iloc[temp_base_id].price
                                    self.line_base_ref = temp_base_id
                                    break
                                    
                                if self.line_base.iloc[temp_base_id].vertex == TOP and \
                                    self.line_base.iloc[temp_base_id].price > self.line_base.iloc[line_base_start+1].price:
                                    # 下一个top突破
                                    self.line_simple = self.line_simple.append(self.line_base.iloc[temp_base_id])
                                    self.line_base_ref = temp_base_id
                                    break
                            temp_base_id += 1
                        break
        # 画出化简后的折线
        if(day_ind == self.kl_pd.iloc[-1].key):
            self.ax.plot(self.line_simple['id'], self.line_simple['price'], color='m', alpha=0.7)
    
    def current_struct_analysis_daily(self, today, lines):
        # 把line_simple 分析成不同的区间
        # lines 可以是self.line_simple, 可以是self.line_base
        day_ind = today.key
        new_line_id = lines.shape[0] - 1
        current_line_id = self.line_simple_ref
        
        # 初始化， 寻找最初的struct， 区间阈值 1.3 只用于最初判断
        if new_line_id > 2 and self.struct_parts.shape[0] == 0 and len(self.struct_list) == 0:
            while self.struct_parts.shape[0] == 0 and current_line_id <= new_line_id:
                diff_now = abs(lines.iloc[current_line_id].price - lines.iloc[current_line_id-1].price)
                diff_pre = abs(lines.iloc[current_line_id - 1].price - lines.iloc[current_line_id - 2].price)
                if diff_now / diff_pre > 0.7 and diff_now / diff_pre < 1.3: 
                    self.struct_parts = self.struct_parts.append(lines.iloc[current_line_id-2:current_line_id+1])
                    self.struct_parts_max = np.max(self.struct_parts.price)
                    self.struct_parts_min = np.min(self.struct_parts.price)
                    self.line_simple_ref += 1
                    current_line_id = self.line_simple_ref
                    break
                self.line_simple_ref += 1
                current_line_id = self.line_simple_ref
        if self.struct_parts.shape[0] > 0 or len(self.struct_list) > 0:
            #逐项判断line的区间
            while current_line_id < new_line_id:
                if self.struct_parts.shape[0] > 1:
                    # 判断此时struct是否有数据
                    print('{} currnt line id :{}, shape:{}'.format('strucs', current_line_id, self.struct_parts.shape[0]))
                    if lines.iloc[current_line_id].price > self.struct_parts_min and \
                        lines.iloc[current_line_id].price < self.struct_parts_max:
                        # 仍在震荡范围内
                        self.struct_parts = self.struct_parts.append(lines.iloc[current_line_id])
                        self.struct_parts_max = np.max(self.struct_parts.price)
                        self.struct_parts_min = np.min(self.struct_parts.price)
                        current_line_id +=1
                    else:
                        #超出震荡范围, 但是在2倍以内
                        diff_now = abs(lines.iloc[current_line_id].price - lines.iloc[current_line_id-1].price)
                        diff_pre = abs(self.struct_parts_max - self.struct_parts_min)
                        if diff_now / diff_pre < 2 : 
                            #需要判断是否为趋势，还是继续震荡
                            #如果下一段曲线回归，则为震荡                            
                            if current_line_id < new_line_id-1:
                                #有下一段折线
                                current_line_id += 1
                                diff_now = abs(lines.iloc[current_line_id].price - lines.iloc[current_line_id-1].price)
                                if (lines.iloc[current_line_id].price < self.struct_parts_min and lines.iloc[current_line_id].vertex == TOP) \
                                    or (lines.iloc[current_line_id].price > self.struct_parts_min and lines.iloc[current_line_id].vertex == BOT):
                                    # 出现新区间, 先保存旧区间
                                    a = struct_cls(RANGE, self.struct_parts.iloc[0].id, self.struct_parts.iloc[-1].id, \
                                                    self.struct_parts_max, self.struct_parts_min, self.struct_parts)
                                    self.struct_list.append(a)

                                    self.struct_parts.drop(self.struct_parts.index,inplace=True)
                                    # 定义趋势
                                    current_line_id -=1
                                    self.struct_parts = self.struct_parts.append(lines.iloc[current_line_id-1:current_line_id+1])
                                    self.struct_parts_max = np.max(self.struct_parts.price)
                                    self.struct_parts_min = np.min(self.struct_parts.price)
                                    b = struct_cls(TREND, self.struct_parts.iloc[0].id, self.struct_parts.iloc[-1].id,\
                                                    self.struct_parts_max, self.struct_parts_min, self.struct_parts)
                                    self.struct_list.append(b)

                                    self.struct_parts.drop(self.struct_parts.index,inplace=True)
                                    # 定义新区间
                                    current_line_id +=1
                                    self.struct_parts = self.struct_parts.append(lines.iloc[current_line_id-1:current_line_id+1])
                                    self.struct_parts_max = np.max(self.struct_parts.price)
                                    self.struct_parts_min = np.min(self.struct_parts.price)

                                else:
                                    #是前一区间的延续
                                    self.struct_parts = self.struct_parts.append(lines.iloc[current_line_id-1:current_line_id+1])
                                    self.struct_parts_max = np.max(self.struct_parts.price)
                                    self.struct_parts_min = np.min(self.struct_parts.price)
                                self.line_simple_ref += current_line_id + 1
                                current_line_id = self.line_simple_ref
                            else: #没有下一段折线，暂时退出
                                current_line_id += 1
                        else:
                            #超过2倍认为是趋势, 先保存前一段range
                            a = struct_cls(RANGE, self.struct_parts.iloc[0].id, self.struct_parts.iloc[-1].id, \
                                                    self.struct_parts_max, self.struct_parts_min, self.struct_parts)
                            self.struct_list.append(a)

                            #超过2倍认为是趋势， 保存趋势
                            self.struct_parts.drop(self.struct_parts.index,inplace=True)
                            self.struct_parts = self.struct_parts.append(lines.iloc[current_line_id-1:current_line_id+1])
                            self.struct_parts_max = np.max(self.struct_parts.price)
                            self.struct_parts_min = np.min(self.struct_parts.price)
                            b = struct_cls(TREND, self.struct_parts.iloc[0].id, self.struct_parts.iloc[-1].id,\
                                            self.struct_parts_max, self.struct_parts_min, self.struct_parts)
                            self.struct_list.append(b)
                            self.struct_parts.drop(self.struct_parts.index,inplace=True)
                            self.line_simple_ref += current_line_id + 1
                            current_line_id = self.line_simple_ref
                            
                else:
                    #如果没有数据, 需要寻找新的struct
                    # 此时，有可能是刚结束趋势
                    self.struct_parts = self.struct_parts.append(lines.iloc[current_line_id-1:current_line_id+1])
                    self.struct_parts_max = np.max(self.struct_parts.price)
                    self.struct_parts_min = np.min(self.struct_parts.price)
                    self.line_simple_ref += current_line_id + 1
                    current_line_id = self.line_simple_ref


        if(day_ind == self.kl_pd.iloc[-1].key):
            #打印出最终结果
            for  a in self.struct_list:
                print(a)

    def current_struct_analysis_daily2(self, today, lines):
        # 把line_simple 分析成不同的区间
        # lines 可以是self.line_simple, 可以是self.line_base
        day_ind = today.key
        new_line_id = lines.shape[0] - 1
        current_line_id = self.line_simple_ref
        
        # 初始化， 寻找最初的struct， 区间阈值 1.3 只用于最初判断
        if new_line_id > 2 and self.struct_parts.shape[0] == 0 and len(self.struct_list) == 0:
            while self.struct_parts.shape[0] == 0 and current_line_id <= new_line_id:
                diff_now = abs(lines.iloc[current_line_id].price - lines.iloc[current_line_id-1].price)
                diff_pre = abs(lines.iloc[current_line_id - 1].price - lines.iloc[current_line_id - 2].price)
                if diff_now / diff_pre > 0.7 and diff_now / diff_pre < 1.3: 
                    self.struct_parts = self.struct_parts.append(lines.iloc[current_line_id-2:current_line_id+1])
                    self.struct_parts_max = np.max(self.struct_parts.price)
                    self.struct_parts_min = np.min(self.struct_parts.price)
                    self.line_simple_ref += 1
                    current_line_id = self.line_simple_ref
                    break
                self.line_simple_ref += 1
                current_line_id = self.line_simple_ref
        if self.struct_parts.shape[0] > 0 or len(self.struct_list) > 0:
            #逐项判断line的区间
            while current_line_id < new_line_id:
                if self.struct_parts.shape[0] > 1:
                    # 判断此时struct是否有数据
                    print('{} currnt line id :{}, shape:{}'.format('strucs', current_line_id, self.struct_parts.shape[0]))
                    if lines.iloc[current_line_id].price > self.struct_parts_min and \
                        lines.iloc[current_line_id].price < self.struct_parts_max:
                        # 仍在震荡范围内
                        self.struct_parts = self.struct_parts.append(lines.iloc[current_line_id])
                        self.struct_parts_max = np.max(self.struct_parts.price)
                        self.struct_parts_min = np.min(self.struct_parts.price)
                        current_line_id +=1
                    else:
                        #超出震荡范围, 但是在2倍以内
                        diff_now = abs(lines.iloc[current_line_id].price - lines.iloc[current_line_id-1].price)
                        diff_pre = abs(self.struct_parts_max - self.struct_parts_min)
                        if diff_now / diff_pre < 2 : 
                            #需要判断是否为趋势，还是继续震荡
                            #如果下一段曲线回归，则为震荡                            
                            if current_line_id < new_line_id-1:
                                #有下一段折线
                                current_line_id += 1
                                diff_now = abs(lines.iloc[current_line_id].price - lines.iloc[current_line_id-1].price)
                                if (lines.iloc[current_line_id].price < self.struct_parts_min and lines.iloc[current_line_id].vertex == TOP) \
                                    or (lines.iloc[current_line_id].price > self.struct_parts_min and lines.iloc[current_line_id].vertex == BOT):
                                    # 出现新区间, 先保存旧区间
                                    a = struct_cls(RANGE, self.struct_parts.iloc[0].id, self.struct_parts.iloc[-1].id, \
                                                    self.struct_parts_max, self.struct_parts_min, self.struct_parts)
                                    self.struct_list.append(a)

                                    self.struct_parts.drop(self.struct_parts.index,inplace=True)
                                    # 定义趋势
                                    current_line_id -=1
                                    self.struct_parts = self.struct_parts.append(lines.iloc[current_line_id-1:current_line_id+1])
                                    self.struct_parts_max = np.max(self.struct_parts.price)
                                    self.struct_parts_min = np.min(self.struct_parts.price)
                                    b = struct_cls(TREND, self.struct_parts.iloc[0].id, self.struct_parts.iloc[-1].id,\
                                                    self.struct_parts_max, self.struct_parts_min, self.struct_parts)
                                    self.struct_list.append(b)

                                    self.struct_parts.drop(self.struct_parts.index,inplace=True)
                                    # 定义新区间
                                    current_line_id +=1
                                    self.struct_parts = self.struct_parts.append(lines.iloc[current_line_id-1:current_line_id+1])
                                    self.struct_parts_max = np.max(self.struct_parts.price)
                                    self.struct_parts_min = np.min(self.struct_parts.price)

                                else:
                                    #是前一区间的延续
                                    self.struct_parts = self.struct_parts.append(lines.iloc[current_line_id-1:current_line_id+1])
                                    self.struct_parts_max = np.max(self.struct_parts.price)
                                    self.struct_parts_min = np.min(self.struct_parts.price)
                                self.line_simple_ref += current_line_id + 1
                                current_line_id = self.line_simple_ref
                            else: #没有下一段折线，暂时退出
                                current_line_id += 1
                        else:
                            #超过2倍认为是趋势, 先保存前一段range
                            a = struct_cls(RANGE, self.struct_parts.iloc[0].id, self.struct_parts.iloc[-1].id, \
                                                    self.struct_parts_max, self.struct_parts_min, self.struct_parts)
                            self.struct_list.append(a)

                            #超过2倍认为是趋势， 保存趋势
                            self.struct_parts.drop(self.struct_parts.index,inplace=True)
                            self.struct_parts = self.struct_parts.append(lines.iloc[current_line_id-1:current_line_id+1])
                            self.struct_parts_max = np.max(self.struct_parts.price)
                            self.struct_parts_min = np.min(self.struct_parts.price)
                            b = struct_cls(TREND, self.struct_parts.iloc[0].id, self.struct_parts.iloc[-1].id,\
                                            self.struct_parts_max, self.struct_parts_min, self.struct_parts)
                            self.struct_list.append(b)
                            self.struct_parts.drop(self.struct_parts.index,inplace=True)
                            self.line_simple_ref += current_line_id + 1
                            current_line_id = self.line_simple_ref
                            
                else:
                    #如果没有数据, 需要寻找新的struct
                    # 此时，有可能是刚结束趋势
                    self.struct_parts = self.struct_parts.append(lines.iloc[current_line_id-1:current_line_id+1])
                    self.struct_parts_max = np.max(self.struct_parts.price)
                    self.struct_parts_min = np.min(self.struct_parts.price)
                    self.line_simple_ref += current_line_id + 1
                    current_line_id = self.line_simple_ref


        if(day_ind == self.kl_pd.iloc[-1].key):
            #打印出最终结果
            for  a in self.struct_list:
                print(a)


    def current_struct_analysis_line_base(self, today, lines):
        # 把line_simple 分析成不同的区间
        # lines 可以是self.line_simple, 可以是self.line_base
        new_line_id = lines.shape[0] - 1
        current_line_id = self.line_simple_ref
        cur_struct = struct_cls()
        pre_struct = struct_cls()
        
        if new_line_id == 2 and pre_struct.id_end == 0 and cur_struct.id_end == 0:
            # 构建初始的struct，用前3个顶点作为初始中枢
            cur_struct.id_start = lines.iloc[1].id
            cur_struct.id_end = lines.iloc[2].id
            if lines.iloc[0].vertex == TOP:
                cur_struct.price_max = lines.iloc[2].price
                cur_struct.price_min = lines.iloc[1].price
            else:
                cur_struct.price_max = lines.iloc[1].price
                cur_struct.price_min = lines.iloc[2].price
            cur_struct.price_line_lists = cur_struct.price_line_lists.append(lines.iloc[1:3])

            self.line_simple_ref = 2
        
        print('line id: ', self.line_simple_ref, 'new id: ', new_line_id)
        current_line_id = self.line_simple_ref
        while current_line_id < new_line_id:
            # 之后每增加一个顶点，进行比较，是否还留在中枢内1
            current_line_id = self.line_simple_ref + 1
            if lines.iloc[current_line_id].vertex == TOP:
                # 如果顶点在中枢内，则保存这个顶点
                if lines.iloc[current_line_id].price <= cur_struct.price_max and \
                    lines.iloc[current_line_id].price >= cur_struct.price_min:
                    cur_struct.price_max = lines.iloc[current_line_id].price
                    cur_struct.id_end =  lines.iloc[current_line_id].id
                    cur_struct.price_line_lists = cur_struct.price_line_lists.append(lines.iloc[current_line_id])
                    self.line_simple_ref = current_line_id

                elif lines.iloc[current_line_id].price < cur_struct.price_min:
                    # 作为顶点，如果向下突破了，则保存前一个中枢结构体
                    pre_struct = cur_struct
                    self.struct_list.append(cur_struct)
                    # 配置新的中枢
                    cur_struct = struct_cls()
                    cur_struct.id_start = lines.iloc[current_line_id-1].id
                    cur_struct.id_end = lines.iloc[current_line_id].id
                    cur_struct.price_max = lines.iloc[current_line_id].price
                    cur_struct.price_min = lines.iloc[current_line_id-1].price
                    cur_struct.price_line_lists = cur_struct.price_line_lists.append(lines.iloc[current_line_id-1:current_line_id+1])
                    self.line_simple_ref = current_line_id
                
                else:
                    pass

            if lines.iloc[current_line_id].vertex == BOT:
                # 如果底点在中枢内，则保存这个顶点
                if lines.iloc[current_line_id].price <= cur_struct.price_max and \
                    lines.iloc[current_line_id].price >= cur_struct.price_min:
                    cur_struct.price_min = lines.iloc[current_line_id].price
                    cur_struct.id_end = lines.iloc[current_line_id].id
                    cur_struct.price_line_lists = cur_struct.price_line_lists.append(lines.iloc[current_line_id])
                    self.line_simple_ref = current_line_id

                elif lines.iloc[current_line_id].price < cur_struct.price_min:
                    # 作为底点，如果向上突破了，则保存前一个中枢结构体
                    pre_struct = cur_struct
                    self.struct_list.append(cur_struct)
                    # 配置新的中枢
                    cur_struct = struct_cls()
                    cur_struct.id_start = lines.iloc[current_line_id-1].id
                    cur_struct.id_end = lines.iloc[current_line_id].id
                    cur_struct.price_max = lines.iloc[current_line_id-1].price
                    cur_struct.price_min = lines.iloc[current_line_id].price
                    cur_struct.price_line_lists = cur_struct.price_line_lists.append(lines.iloc[current_line_id-1:current_line_id+1])
                    self.line_simple_ref = current_line_id
                
                else:
                    pass
                
            current_line_id += 1





    def fit_day(self, today):
        res = list()
        self._line_for_basic(today)
        self._line_simplify(today)
        self.current_struct_analysis_line_base(today, self.line_base)
        self.line_simple.to_csv('line_simple.csv')
        self.line_base.to_csv('line_base.csv')
        self.struct_parts.to_csv('structs.csv')
        return res
        





class Sell_mean(Qt_sell_base):
    def __init__(self, kl_pd, **kwargs):
        print('----init---{}'.format(self.__class__.__name__))
        super().__init__(kl_pd)
        self._init_self(**kwargs)


    def _init_self(self, **kwargs):
        self.xd =  kwargs['xd1']
    
    def fit_day(self, today):
        res = list()
        kl_pd = self.kl_pd
        day_ind = int(today.key)
        if day_ind > self.xd and day_ind < len(kl_pd)-2:
            if(today.close < kl_pd['close'].rolling(self.xd).mean()[day_ind]):
                res.append(self.make_sell_order(day_ind+1))
        return res
