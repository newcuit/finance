import talib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import tushare as ts
from talib import MA_Type

df = ts.get_hist_data('300398',start='20160830',end='20171019')
print(df.close)


mydif,mydea,mybar = talib.MACD(df['close'].values, fastperiod=12, slowperiod=26, signalperiod=9)

print(mydif,mydea,mybar)
dataArray=None
for i in df.index.values:
    rowArray = np.array(i.replace('-',''))
    if str(dataArray) == 'None':
        dataArray = rowArray
    else:
        dataArray = np.row_stack((dataArray,rowArray))

print(dataArray)
fig = plt.figure(figsize=[18,5])
plt.plot(mydif,label='dif')
plt.plot(mydea,label='dea')
plt.plot(mybar,label='bar')
plt.legend(loc='best')
plt.show()

upper, middle, lower = talib.BBANDS(df['close'].values,matype=MA_Type.T3)
print(upper, middle, lower)
fig = plt.figure(figsize=[18,5])
plt.plot(upper,label='upper')
plt.plot(middle,label='middle')
plt.plot(lower,label='lower')
plt.legend(loc='best')
plt.show()

k,d = talib.STOCH(df['high'].values, df['low'].values, df['close'].values,fastk_period=5, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
j = 3*k - 2*d
fig = plt.figure(figsize=[18,5])
plt.plot(k,label='k')
plt.plot(d,label='d')
plt.plot(j,label='j')
plt.legend(loc='best')
plt.show()

rsi16 = talib.RSI(df['close'].values, timeperiod=16)
rsi12 = talib.RSI(df['close'].values, timeperiod=12)
rsi24 = talib.RSI(df['close'].values, timeperiod=24)
fig = plt.figure(figsize=[18,5])
plt.plot(rsi16,label='rsi16')
plt.plot(rsi12,label='rsi12')
plt.plot(rsi24,label='rsi24')
plt.legend(loc='best')
plt.show()
