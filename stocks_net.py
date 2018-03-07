# -*- coding: utf-8 -*-
"""
Created on Sat Oct 14 12:43:05 2017

@author: liuchun
"""
#!usr/bin/env python
#-*- coding: utf-8 -*-
import time
import datetime
import tushare as ts
import urllib.request
import urllib.parse
import requests

''' 参考网页:http://blog.csdn.net/ustbhacker/article/details/8365756 '''
''' http://tushare.org/trading.html#id2 '''

class tickTencent:
    ''' market:[sz|sh], code: tick code'''
    def __init__(self,market, code):
        self.code = market+code

    def httpPost(self):
        req = urllib.request.Request(url=self.url,data=None)
        try:
            res_data = urllib.request.urlopen(req)
            return res_data.read().decode('gbk')
        
        except Exception as e:
            print(e)
            pass

        return 'None'

    '''
    获取最新行情：
        0: 未知,1: 名字,2: 代码,3: 当前价格,4: 昨收,5: 今开,6: 成交量（手）,7: 外盘,8: 内盘,9: 买一  
        10: 买一量（手）,11-18: 买二 买五,19: 卖一,20: 卖一量,21-28: 卖二 卖五,29: 最近逐笔成交,30: 时间  
        31: 涨跌,32: 涨跌%,33: 最高,34: 最低,35: 价格/成交量（手）/成交额,36: 成交量（手）,37: 成交额（万）  
        38: 换手率,39: 市盈率,40: ,41: 最高,42: 最低,43: 振幅,44: 流通市值,45: 总市值,46: 市净率,47: 涨停价
        48: 跌停价 
    '''
    def getCurrentData(self):
        self.url = "http://qt.gtimg.cn/q="+self.code
        return self.httpPost()
    
    '''
    获取资金流向：
         0: 代码 ,1: 主力流入, 2: 主力流出 ,3: 主力净流入,4: 主力净流入/资金流入流出总和,5: 散户流入,6: 散户流出  
         7: 散户净流入,8: 散户净流入/资金流入流出总和,9: 资金流入流出总和1+2+5+6,10: 未知 ,11: 未知,12: 名字  
         13: 日期 
    '''
    def getCapitalData(self):
        self.url = "http://qt.gtimg.cn/q=ff_"+self.code
        return self.httpPost()
    
    '''
    获取盘口信息：
        0: 买盘大单 ，1: 买盘小单 ，2: 卖盘大单 ，3: 卖盘小单  
    '''
    def getHandicapData(self):
        self.url = "http://qt.gtimg.cn/q=s_pk"+self.code
        return self.httpPost()
    
    '''
    获取简要信息：
        0: 未知,1: 名字,2: 代码 ,3: 当前价格 ,4: 涨跌 ,5: 涨跌% ,6: 成交量（手）,7: 成交额（万） ,8: ,9: 总市值 
    '''
    def getInfoData(self):
        self.url = "http://qt.gtimg.cn/q=s_"+self.code
        return self.httpPost()

class tick163:
    def __init__(self,code, start,end):
        self.ip = 'http://quotes.money.163.com/service/chddata.html'
        self.fields = 'TCLOSE;HIGH;LOW;TOPEN;LCLOSE;CHG;PCHG;TURNOVER;VOTURNOVER;VATURNOVER;TCAP;MCAP'
        self.code = code
        self.end = end
        self.start = start

    def httpPost(self):
        req = urllib.request.Request(url=self.url,data=None)
        try:
            res_data = urllib.request.urlopen(req)
            return res_data.read().decode('gbk')
        
        except Exception as e:
            print(e)
            pass

        return 'None'

    def getData(self):
        self.url = self.ip+"?code="+self.code+"&start="+self.start+"&end="+self.end+"&fields="+self.fields
        return self.httpPost()

class sinaTick():
    def __init__(self,code):
        if code[0:3] == '600' or code[0:3] == '603':
            self.url = 'http://image.sinajs.cn/newchart/daily/n/sh'+code+'.gif'
        else:
            self.url = 'http://image.sinajs.cn/newchart/daily/n/sz'+code+'.gif'
    def getK(self):
        req = requests.get(self.url)
        return req.content

class tickInterface():
    def __init__(self):
        self.name = "TickPrase"
    
    '''返回dataFrame格式'''
    def getStockBasics(self):
        return ts.get_stock_basics()
    
    '''返回dataFrame格式'''
    def getHistData(self,code, start=None,end=None):
        if( start == None and end == None):
            self.data = ts.get_hist_data(code)
        else:
            self.data = ts.get_hist_data(code,start,end)
        return self.data

    '''返回dataFrame格式'''
    def getHdata(self,code,start,end):
        return ts.get_h_data(code, start, end)

    '''返回dataFrame格式'''
    def getKdata(self,code):
        return ts.get_k_data(code)
    
    '''返回dataFrame格式'''
    def getTodayData(self):
        return ts.get_today_all()

    def get_tick_info(self,code,date):
        return ts.get_tick_data(code,date)

    def get_tick_big_volume(self,code,day):
        return ts.get_sina_dd(code, date=day)

    '''上证'''
    def isShangHai(self,code):
        if code[0:3] == '600' or code[0:3] == '603':
            return True
        return False

    '''深证'''
    def isShenZheng(self,code):
        if code[0:3] == '000' or code[0:3] == '002' or code[0:3] == '300':
            return True
        return False

    '''创业板'''
    def isCarveOutBoard(self,code):
        if code[0:3] == '300':
            return True
        return False

    '''中小板'''
    def isSmeBoard(self,code):
        if code[0:3] == '002':
            return True
        return False

    '''ST股票判断'''
    def isStCode(self,name):
        if name.find('ST') == -1:
            return False
        return True

    '''次新股判断'''
    def isSubNewStock(self,timeToMarket):
        timeToMarket=str(timeToMarket)     
        marketStr = str(timeToMarket[0:4])+str('-')+str(timeToMarket[4:6])+str('-')+str(timeToMarket[6:8])
        marketTime = time.mktime(time.strptime(marketStr,'%Y-%m-%d'))
        judgeTime = time.mktime(time.strptime((datetime.date.today() - datetime.timedelta(days=365)).strftime('%Y-%m-%d'),'%Y-%m-%d'))

        if judgeTime > marketTime:
            return False
        return True

    def getAmountInfo(self,code,cday):
        amountIn = 0
        amountOut = 0
        volumeIn = 0
        volumeOut = 0

        codedate = datetime.date.today() - datetime.timedelta(days=cday)
        codeinfo = self.get_tick_info(code,codedate.strftime('%Y-%m-%d'))
        for index in range(0,len(codeinfo)):
            if codeinfo.ix[index].type == '卖盘':
                amountOut = amountOut + codeinfo.ix[index].amount
                '''大于50万一笔认为是大单'''
                if codeinfo.ix[index].amount > 500000:
                    volumeOut = volumeOut + 1
            if codeinfo.ix[index].type == '买盘':
                amountIn = amountIn + codeinfo.ix[index].amount
                if codeinfo.ix[index].amount > 500000:
                    volumeIn = volumeIn + 1

        return volumeIn,volumeOut,amountIn,amountOut
