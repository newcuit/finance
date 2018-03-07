import matplotlib.pyplot as plt
import numpy as np
import tushare as ts
from FinanceTools import financeData
from stocks_net import tickTencent
from stocks_net import tick163

ta = financeData()
#http://image.sinajs.cn/newchart/daily/n/sz300398.gif
df = ts.get_hist_data('300398',start='2017-01-01',end='2017-10-19')
#df = ts.get_h_data('300398', start='2017-01-01', end='2017-10-20')
print(df.ma5.values)

df = ts.get_k_data('300398')
print(ta.getMa(df.close.values))

#print(df.close.values)
#print(len(df['close'].values))

#tt = tickTencent('sz','300398')
#print(tt.getCurrentData())


dif,dea,macd = ta.getMacd(df['close'].values[::-1])
dif,dea,macd = ta.getMacd(df['close'].values)

print(macd)
fig = plt.figure(figsize=[18,5])
plt.plot(df.index,dif,label='dif')
plt.plot(df.index,dea,label='dea')
plt.plot(df.index,macd,label='macd')
plt.legend(loc='best')
plt.show()


'''
upper, middle, lower = ta.getBoll(df['close'].values[::-1])
print(upper)
print('middle')
print(middle)
print('lower')
print(lower)
fig = plt.figure(figsize=[18,5])
plt.plot(upper,label='upper')
plt.plot(middle,label='middle')
plt.plot(lower,label='lower')
plt.legend(loc='best')
plt.show()
'''


'''
k,d,j= ta.getKdj(df['high'].values[::-1], df['low'].values[::-1], df['close'].values[::-1])
print(k)
fig = plt.figure(figsize=[18,5])
plt.plot(k,label='k')
plt.plot(d,label='d')
plt.plot(j,label='j')
plt.legend(loc='best')
plt.show()
'''


'''
rsi16, rsi12,rsi24 = ta.getRsi(df['close'].values[::-1])
print('rsi16')
print(rsi16)
print('rsi12')
print(rsi12)
print('rsi24')
print(rsi24)
fig = plt.figure(figsize=[18,5])
plt.plot(rsi16,label='rsi16')
plt.plot(rsi12,label='rsi12')
plt.plot(rsi24,label='rsi24')
plt.legend(loc='best')
plt.show()
'''
