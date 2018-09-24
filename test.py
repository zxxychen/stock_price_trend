#!coding:utf-8#
#from K_line_contain import *
import tushare as ts
import matplotlib.pyplot as plt
import os
import pandas as pd
import datetime as dt

left2 = pd.DataFrame([[1,2],[3,4],[5,6]],index=['a','c','e'],columns=['A','B'])
right2 = pd.DataFrame([[7,8],[9,10],[11,12]],index=['c','e','f'],columns=['A','B'])
print(left2)
print(right2)
print(right2.index)
for i in right2.index:
    if i in left2.index:

        print('yes')
    else:
        print('no')
#print(result)