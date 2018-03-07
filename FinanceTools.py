# -*- coding: utf-8 -*-
"""
Created on Sat Oct 14 12:43:05 2017

@author: liuchun
"""
#!usr/bin/env python
#-*- coding: utf-8 -*-
import talib
from talib import MA_Type
import pandas as pd
import numpy as np
from functools import reduce 

class financeData():
    def __init__(self):
        self.name='FinanceData'
    
    ''' 通过收盘价获取移动平均线，返回数组'''
    def getMa(self, close,timeperiod=5):
        return talib.SMA(close, timeperiod)
    
    '''计算布林线，三指数移动平均，返回upper, middle, lower'''
    def getBoll(self,close):
        upper, middle, lower = talib.BBANDS(close,matype=MA_Type.T3)
        return upper, middle,lower
    
    '''计算收盘价的动量，时间为5,返回数组'''
    def getMom(self,close):
        return talib.MOM(close, timeperiod=5)
    
    def getMacd(self,close):
        macdDIFF, macdDEA, macd = talib.MACDEXT(close, fastperiod=12, fastmatype=1, slowperiod=26, slowmatype=1, signalperiod=9, signalmatype=1)
        macd = macd * 2
        return macdDIFF, macdDEA, macd

    def getOneRsi(self,close,timeperiod):
        diff = list(map(lambda x, y : x - y, close[1:], close[:-1]))
        diffGt0 = list(map(lambda x : 0 if x < 0 else x, diff))
        diffABS = list(map(lambda x : abs(x), diff))
        diff = np.array(diff)
        diffGt0 = np.array(diffGt0)
        diffABS = np.array(diffABS)
        diff = np.append(diff[0], diff)
        diffGt0 = np.append(diffGt0[0], diffGt0)
        diffABS = np.append(diffABS[0], diffABS)
        rsi = list(map(lambda x : self.sma_cn(diffGt0[:x], timeperiod) / self.sma_cn(diffABS[:x], timeperiod) * 100,range(1, len(diffGt0) + 1) ))
        return np.array(rsi)
        
    def getRsi(self,close):
        rsi16 = self.getOneRsi(close, 16)
        rsi12 = self.getOneRsi(close, 12)
        rsi24 = self.getOneRsi(close, 24)
        
        return rsi16,rsi12,rsi24

    def sma_cn(self, close, timeperiod) :
        close = np.nan_to_num(close)
        return reduce(lambda x, y: ((timeperiod - 1) * x + y) / timeperiod, close)
    
    def getKdj(self,high,low, close):
        fastk_period = 9
        slowk_period = 3
        fastd_period = 3
        kValue, dValue = talib.STOCHF(high, low, close, fastk_period, fastd_period=1, fastd_matype=0)

        kValue = np.array(list(map(lambda x : self.sma_cn(kValue[:x], slowk_period), range(1, len(kValue) + 1))))
        dValue = np.array(list(map(lambda x : self.sma_cn(kValue[:x], fastd_period), range(1, len(kValue) + 1))))
    
        jValue = 3 * kValue - 2 * dValue
    
        func = lambda arr : np.array([0 if x < 0 else (100 if x > 100 else x) for x in arr])
    
        kValue = func(kValue)
        dValue = func(dValue)
        jValue = func(jValue)
        return kValue, dValue, jValue
    
    def getCci(self,high,low,close):
        return talib.CCI(high, low, close, timeperiod=14)
    
    def getObv(self,close,volume):
        return talib.OBV(close, volume)
