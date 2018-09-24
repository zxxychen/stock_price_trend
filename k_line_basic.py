#!coding:utf-8#
#from K_line_contain import *
import tushare as ts
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import datetime as dt


def check_k_file(s_code, k_type):
	# s_code and k_type is str type
	file_path = './' + k_type + '/' + s_code + '.csv'
	if os.path.exists(file_path):
		return 1 # file exist
	else:
		return 0

def save_k_file(k_data, s_code, ktype):
	# s_code and k_type is str type
	file_name =  './' + ktype
	if not os.path.exists(file_name):
		os.mkdir(file_name)
	file_path = './' + ktype + '/' + s_code + '.csv'
	try:
		k_data.to_csv(file_path)
	except:
		print(' this file may be open, close ', s_code, ' file first:' )

def read_k_file(s_code, k_type):
	file_path = './' + k_type + '/' + s_code + '.csv'
	data_out = pd.read_csv(file_path, index_col='date')
	return data_out

def update_k_file(k_data,s_code, k_type):
	print('update', s_code,' k line info from NET')
	prev_date = k_data.index[-1]
	#print(prev_date)
	now_date = dt.datetime.now().strftime('%Y-%m-%d')
	#print(prev_date)
	new_k_data = ts.get_k_data(s_code, ktype=k_type, start=prev_date, end=now_date)
	new_k_data.set_index(['date'], inplace=True)
	new_k_data.drop('code', axis=1,inplace=True)

	new_k_data['left_sum'] = 1
	new_k_data['right_sum'] = 1
	for index in new_k_data.index:
		if index in k_data.index:
			pass
		else:
			k_data = k_data.append(new_k_data.loc[index])
	return k_data



def contain_detect(data_p, data_c):
	#print(data_p.name)
	#print(data_c)
	if data_c['low'] >= data_p['low'] and data_c['high'] <= data_p['high']:
		return 2 #remove current data
	elif data_c['low'] <= data_p['low'] and data_c['high'] >= data_p['high']:
		return 1 #remove previous data
	else:
		return 0 #none


def data_clean(din):
	print('start clean data : contain relationship')
	res_sum = 1
	while res_sum != 0:
		res_sum = 0
		prev_s = din.iloc[0]
		cur_s = din.iloc[1]
		for next_date in din.index[2:]:
			#print(next_date)

			res = contain_detect(cur_s, din.loc[next_date])
			if res == -1:
				return -1
			res_sum += res

			if res == 2:
				#print(next_date)
				if cur_s['high'] > prev_s['high'] and cur_s['low'] > prev_s['low']:
					din.loc[cur_s.name, 'low'] = din.loc[next_date,'low']
				elif cur_s['high'] < prev_s['high'] and cur_s['low'] < prev_s['low']:
					din.loc[cur_s.name, 'high'] = din.loc[next_date, 'high']
				else:
					pass

				din.loc[cur_s.name, 'right_sum'] += (din.loc[next_date,'left_sum'] + din.loc[next_date,'right_sum'] -1)
				din.drop(next_date, inplace=True)

			elif res == 1:
				if cur_s['high'] > prev_s['high'] and cur_s['low'] > prev_s['low']:
					din.loc[next_date, 'low'] = din.loc[cur_s.name, 'low']
				elif cur_s['high'] < prev_s['high'] and cur_s['low'] < prev_s['low']:
					din.loc[next_date, 'high'] = din.loc[cur_s.name, 'high']
				else:
					pass
				#print(prev_s['date'])
				din.loc[next_date,'left_sum'] += (din.loc[cur_s.name, 'right_sum'] + din.loc[cur_s.name, 'left_sum'] - 1)
				din.drop(cur_s.name, inplace=True)
				cur_s = din.loc[next_date]

			else:
				prev_s = cur_s
				cur_s = din.loc[next_date]
	return din

def top_detect(data_p,data_c,data_n):
	if data_c['high'] > data_p['high'] and data_c['high'] > data_n['high']:
		return 1 #top
	elif data_c['low'] < data_p['low'] and data_c['low'] < data_n['low']:
		return 2 #bottom
	else:
		return 0 #none

def k_line_to_stroke(din):
	din_top = din.copy( ['high', 'low', 'left_sum', 'right_sum'])
	din_top['top'] = 0
	prev_s = din_top.iloc[0]
	cur_s = din_top.iloc[1]
	dout = pd.DataFrame(columns=['tip'])

	for next_s in din_top.index[2:]:
		res = top_detect(prev_s, cur_s, din_top.loc[next_s])
		if res == 2 :
			din_top.loc[cur_s.name, 'top'] = 2
			#print(cur_s.name, din_top.loc[cur_s.name, 'low'])
			dout = dout.append(pd.DataFrame({'tip': din_top.loc[cur_s.name, 'low']},index=[cur_s.name]))
		elif res == 1:
			din_top.loc[cur_s.name, 'top'] = 1
			#print( cur_s.name, din_top.loc[cur_s.name, 'high'])
			dout = dout.append(pd.DataFrame({'tip': din_top.loc[cur_s.name, 'high']},index=[cur_s.name]))
		else:
			pass
		prev_s = cur_s
		cur_s = din_top.loc[next_s]
	return dout

def k_line_to_stroke2(din):
	din['is_tip'] = 0
	din['tip'] = None
	prev_s = din.iloc[0]
	cur_s = din.iloc[1]
	for next_s in din.index[2:]:
		res = top_detect(prev_s, cur_s, din.loc[next_s])
		if res == 1:
			din.loc[cur_s.name, 'is_tip'] = 1
			din.loc[cur_s.name, 'tip'] = cur_s['high']
		elif res == 2:
			din.loc[cur_s.name, 'is_tip'] = 2
			din.loc[cur_s.name, 'tip'] = cur_s['low']
		else:
			pass
		prev_s = cur_s
		cur_s = din.loc[next_s]

	return din

if __name__ == '__main__':
	stock_code = '600000'
	k_type = 'D'
	if check_k_file(stock_code, k_type):
		print('read ', stock_code,'csv file from local')
		data = read_k_file(stock_code, k_type)
		#print(data.head())
	else:
		print('load,', stock_code, ' k line information from NET')
		data = ts.get_k_data(stock_code, ktype=k_type, start='2018-01-01', end='2018-08-01')
		data.set_index(['date'], inplace=True)
		data.drop('code',axis=1,inplace=True)

		data['left_sum'] = 1
		data['right_sum'] = 1
	data.to_csv('o.csv')

	data = update_k_file(data, stock_code, k_type)
	data.to_csv("n.csv")
	o_data = data_clean(data)

	save_k_file(o_data, stock_code, k_type)

	stroke_data = k_line_to_stroke2(o_data)
	stroke_data.to_csv('top.csv')
	stroke_data['tip'].plot(figsize=(15,5) )

	#o_data['high'].plot(figsize=(15,5) )
	#o_data['low'].plot(figsize=(15,5) )

	fig = plt.show()
