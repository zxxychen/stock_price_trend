import numpy as np
global BUY
BUY = 1
global HOLD 
HOLD = np.NaN
global SELL 
SELL = 0

## safety:
SAFE0 = 0 # 保守一些的
SAFE1 = 1 # 激进一些的

# for Buy_break_yao
BOT = 0 #bottom
TOP = 1
DN = 0 #down
UP = 1
TREND = 'trend'
RANGE = 'range'