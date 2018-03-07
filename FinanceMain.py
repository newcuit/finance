# -*- coding: utf-8 -*-
"""
Created on Sat Oct 14 12:43:05 2017

@author: liuchun
"""
#!usr/bin/env python
#-*- coding: utf-8 -*-
import sys
import time
import datetime
import pandas as pd
import os
from stocks_net import tickInterface,sinaTick
from PyQt5 import QtCore, QtGui, uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from FinanceTools import financeData

qtCreatorXmlFile = "Finance.ui"
updateCodeSourceDay=5
 
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorXmlFile)

class chooseBtnThread(QtCore.QThread):
    _signal = QtCore.pyqtSignal(str)
 
    def __init__(self, window):
        super(chooseBtnThread, self).__init__()
        self.window = window
        self.tick = tickInterface()
        self.finaniceTool = financeData()

    def screenAddMessage(self,msg):
        self.window.FinanceShow.addItem(self.window.tr(msg));
        self.window.FinanceShow.scrollToBottom()

    def chooseTicksByCondition(self,codeBaseInfo):
        total = len(codeBaseInfo)

        for i in codeBaseInfo.index:
            code = codeBaseInfo.ix[i]['code']
            #print(code)
            self.window.dialog_show_signal.emit(self.window.tr("正在分析: "+codeBaseInfo.ix[i]['name']+"("+str(i+1)+"/"+str(total)+")..."))

            if self.window.choose_stocks_btn.text() == "开始":
                break
            
            '''申购中的新股时间为0，需要返回'''
            if str(codeBaseInfo.ix[i]['timeToMarket']) == '0':
                continue
            
            self.message = str(code)
            '''所属市场板块判断'''
            if self.window.market.currentIndex() == 1:
                if not self.tick.isShangHai(code):
                    continue
            elif self.window.market.currentIndex() == 2:
                if not self.tick.isShenZheng(code):
                    continue
            elif self.window.market.currentIndex() == 3:
                if not self.tick.isCarveOutBoard(code):
                    continue
            elif self.window.market.currentIndex() == 4:
                if not self.tick.isSmeBoard(code):
                    continue
            self.message += ','+codeBaseInfo.ix[i]['name']
            self.message += ','+codeBaseInfo.ix[i]['industry']

            '''ST股判断'''
            if self.window.st_status.currentIndex() == 1:
                if not self.tick.isStCode(codeBaseInfo.ix[i]['name']):
                    continue
            elif self.window.st_status.currentIndex() == 2:
                if self.tick.isStCode(codeBaseInfo.ix[i]['name']):
                    continue

            '''用净利润增长率判断盈利或亏损'''
            if self.window.price_gain_loss.currentIndex() == 1:
                if float(codeBaseInfo.ix[i]['npr']) > 0:
                    continue
            elif self.window.price_gain_loss.currentIndex() == 2:
                if float(codeBaseInfo.ix[i]['npr']) < 0:
                    continue
          
            '''次新股判断'''
            if self.window.new_stocks.currentIndex() == 1:
                if not self.tick.isSubNewStock(codeBaseInfo.ix[i]['timeToMarket']):
                    continue
            elif self.window.new_stocks.currentIndex() == 2:
                if self.tick.isSubNewStock(codeBaseInfo.ix[i]['timeToMarket']):
                    continue

            '''流通股本判断'''
            outstanding = float(codeBaseInfo.ix[i]['outstanding'])
            if outstanding < float(self.window.flow_stocks_min.text()):
                continue
            if outstanding > float(self.window.flow_stocks_max.text()):
                continue
            
            '''市净率判断'''
            pb = float(codeBaseInfo.ix[i]['pb'])
            if pb < float(self.window.market_to_boot_radio_min.text()):
                continue
            if pb > float(self.window.market_to_boot_radio_max.text()):
                continue

            '''市盈率判断'''
            pe = float(codeBaseInfo.ix[i]['pe'])
            if pe < float(self.window.priceearning_min.text()):
                continue
            if pe > float(self.window.priceearning_max.text()):
                continue

            '''每股净资产判断'''
            bvps = float(codeBaseInfo.ix[i]['bvps'])
            if bvps < float(self.window.perstocks_netasset_min.text()):
                continue
            if bvps > float(self.window.perstocks_netasset_max.text()):
                continue

            '''每股收益判断'''
            esp = float(codeBaseInfo.ix[i]['esp'])
            if esp < float(self.window.perstocks_grain_min.text()):
                continue
            if esp > float(self.window.perstocks_grain_max.text()):
                continue

            '''未分配利润判断'''
            perundp = float(codeBaseInfo.ix[i]['perundp'])
            if perundp < float(self.window.undis_profi_min.text()):
                continue
            if perundp > float(self.window.undis_profi_max.text()):
                continue

            if self.window.choose_stocks_btn.text() == "开始":
                break
            
            '''获取3年数据'''
            try:             
                allYearData = self.tick.getKdata(code)
                k_func = lambda pos1,pos2:(pos2[1]-pos1[1])/(pos2[0]-pos1[0])
                y_func = lambda pos,k,x:k*(x-pos[0])+pos[1]
                if self.window.choose_stocks_btn.text() == "开始":
                    break

                '''换手率判断'''
                outstanding = float(codeBaseInfo.ix[i]['outstanding'])
                volume = float(allYearData['volume'].values[::-1][0])
                turnover = float(volume/outstanding/10000)
            
                if turnover < float(self.window.turnover_rate_min.text()):
                    continue
                if turnover > float(self.window.turnover_rate_max.text()):
                    continue

                '''价格判断'''
                price = float(allYearData['close'].values[::-1][0])
                if price < float(self.window.price_min.text()):
                    continue
                if price > float(self.window.price_max.text()):
                    continue

                '''近5日涨跌幅判断'''
                lstFivePrice = float(allYearData['close'].values[::-1][4])
                currentPrice = float(allYearData['close'].values[::-1][0])
                inc_radio = (currentPrice - lstFivePrice)*100/lstFivePrice
                if inc_radio < float(self.window.inc_radio_min.text()):
                    continue
                if inc_radio > float(self.window.inc_radio_max.text()):
                    continue

                ''' 近5日波动幅度判断 '''
                price_wave_max = float(self.window.price_wave_max.text())
                price_wave_min = float(self.window.price_wave_min.text())
                price_wave = lambda cclose,lclose:(cclose-lclose)*100/lclose
                day_wav_price1 = price_wave(float(allYearData['close'].values[::-1][0]),float(allYearData['close'].values[::-1][1]))
                day_wav_price2 = price_wave(float(allYearData['close'].values[::-1][1]),float(allYearData['close'].values[::-1][2]))
                day_wav_price3 = price_wave(float(allYearData['close'].values[::-1][2]),float(allYearData['close'].values[::-1][3]))
                day_wav_price4 = price_wave(float(allYearData['close'].values[::-1][3]),float(allYearData['close'].values[::-1][4]))
                day_wav_price5 = price_wave(float(allYearData['close'].values[::-1][4]),float(allYearData['close'].values[::-1][5]))

                if  day_wav_price1 > price_wave_max or day_wav_price1 < price_wave_min:
                    continue
                if  day_wav_price2 > price_wave_max or day_wav_price2 < price_wave_min:
                    continue
                if  day_wav_price3 > price_wave_max or day_wav_price3 < price_wave_min:
                    continue
                if  day_wav_price4 > price_wave_max or day_wav_price4 < price_wave_min:
                    continue
                if  day_wav_price5 > price_wave_max or day_wav_price5 < price_wave_min:
                    continue

                dif,dea,macd = self.finaniceTool.getMacd(allYearData['close'].values)
                ''' macd金叉 '''
                if self.window.macd_golden_cross.isChecked():
                    macd_len = len(dif)
                    if dif[macd_len - 2] < dea[macd_len - 2] and dif[macd_len - 1] > dea[macd_len - 1]:
                        pass
                    else:
                        continue

                ''' macd开口向上 ,斜率必须大于0，近两日值必须上升且dif小于dea'''
                if self.window.macd_turn_up.isChecked():
                    macd_len = len(dif)
                    dif_k = k_func((1,dif[macd_len - 3]),(3,dif[macd_len - 1]))
                    if dif_k <= 0:
                        continue
                    if dif[macd_len - 2] >= dea[macd_len - 2] and dif[macd_len - 1] > dea[macd_len - 1]:
                        continue

                k,d,j= self.finaniceTool.getKdj(allYearData['high'].values, allYearData['low'].values, allYearData['close'].values)
                ''' kdj金叉 '''
                if self.window.kdj_golden_cross.isChecked():
                    kdj_len = len(k)
                    if k[kdj_len - 2] < d[kdj_len - 2] and k[kdj_len - 1] > d[kdj_len - 1]:
                        pass 
                    else:
                        continue

                ''' kdj开口向上 ，斜率大于0.5且j>k>d'''
                if self.window.kdj_turn_up.isChecked():
                    kdj_len = len(k)
                    kdj_j_k = k_func((1,j[kdj_len - 3]),(3,j[kdj_len - 1]))
                    if kdj_j_k < 0.5:
                        continue
                    if j[kdj_len - 1] <= k[kdj_len - 1]:
                        continue
                    if k[kdj_len - 1] <= d[kdj_len - 1]:
                        continue

                '''kdj超卖 '''
                if self.window.kdj_oversold.isChecked():
                    kdj_len = len(k)
                    if k[kdj_len - 1] <10 and d[kdj_len - 1] < 20:
                        pass 
                    else:
                        continue

                '''rsi24超卖'''
                if self.window.rsi_oversold.isChecked():
                    rsi16, rsi12,rsi24 = self.finaniceTool.getRsi(allYearData['close'].values)
                    if rsi24[len(rsi24) - 1] < 30:
                        pass
                    else:
                        continue

                '''价格处于低位'''
                if self.window.price_low.isChecked():
                    if price >= min(allYearData.close.values[-100:])*1.2:
                        continue

                '''均线多头排列'''
                if self.window.avg_mul_arrange.isChecked():
                    ma5 = self.finaniceTool.getMa(allYearData['close'].values,5)
                    ma10 = self.finaniceTool.getMa(allYearData['close'].values,10)
                    ma20 = self.finaniceTool.getMa(allYearData['close'].values,20)
                    ma30 = self.finaniceTool.getMa(allYearData['close'].values,30)
                    
                    ma5_len = len(ma5)
                    ma10_len = len(ma10)
                    ma20_len = len(ma20)
                    ma30_len = len(ma30)
                    if ma5[ma5_len -1] < ma10[ma10_len - 1]:
                        continue
                    if ma10[ma10_len -1] < ma20[ma20_len - 1]:
                        continue
                    if ma20[ma20_len -1] < ma30[ma30_len - 1]:
                        continue

                    if ma5[ma5_len -2] < ma10[ma10_len - 2]:
                        continue
                    if ma10[ma10_len -2] < ma20[ma20_len - 2]:
                        continue
                    if ma20[ma20_len -2] < ma30[ma30_len - 2]:
                        continue

                    if ma5[ma5_len -1] < ma5[ma5_len - 2]:
                        continue

                '''macd背离,macd,dif的斜率为正，price斜率为负'''
                if self.window.macd_fall_away.isChecked():
                    macd_len = len(macd)
                    dif_k = k_func((1,dif[macd_len - 3]),(3,dif[macd_len - 1]))
                    macd_k = k_func((1,macd[macd_len - 3]),(3,macd[macd_len - 1]))
                    lstThreePrice = float(allYearData['close'].values[::-1][2])
                    price_k = k_func((1,lstThreePrice),(3,currentPrice))
                    if price_k > -0.1:
                        continue
                    if dif_k <= 0.003:
                        continue
                    if macd_k <= 0.003:
                        continue

                '''量价背离，成交量斜率为正，price斜率为负'''
                volume = allYearData['volume'].values[::-1]
                if self.window.volumue_fall_away.isChecked():
                    lstThreePrice = float(allYearData['close'].values[::-1][2])
                    turnover3 = float(volume[2]/outstanding/10000)
                    turnover1 = float(volume[0]/outstanding/10000)
                    volume_k = k_func((1,turnover3),(3,turnover1))
                    price_k = k_func((1,lstThreePrice),(3,currentPrice))
                    if volume_k < 0.3:
                        continue
                    if price_k > -0.1:
                        continue

                '''成交量逐步放大,斜率大于0.5，且每天有一定涨幅的量'''
                if self.window.volume_trun_big.isChecked():
                    turnover1 = float(volume[0]/outstanding/10000)
                    turnover2 = float(volume[1]/outstanding/10000)
                    turnover3 = float(volume[2]/outstanding/10000)
                    turnover4 = float(volume[3]/outstanding/10000)
                    turnover5 = float(volume[4]/outstanding/10000)
                
                    volume_k = k_func((1,turnover5),(5,turnover1))
                    if volume_k < 0.5:
                        continue
                    if turnover4 < turnover5*7/6:
                        continue
                    if turnover2 < turnover3*7/6:
                        continue

                    if turnover4 >= y_func((1,turnover5),volume_k,2):
                        continue;
                    if turnover2 >= y_func((1,turnover5),volume_k,4):
                        continue;
                
                '''BOLL开口向上，斜率大于0.2，且boll口打开'''
                if self.window.boll_trun_up.isChecked():
                    upper, middle, lower = self.finaniceTool.getBoll(allYearData['close'].values)
                    boll_len = len(middle)
                    boll_up_k = k_func((1,upper[boll_len - 3]),(3,upper[boll_len - 1]))
                    boll_mi_k = k_func((1,middle[boll_len - 3]),(3,middle[boll_len - 1]))

                    if boll_up_k < 0.2:
                        continue
                    if boll_mi_k < 0.2:
                        continue

                    boll_diff5 = upper[boll_len - 5] - lower[boll_len - 5]
                    boll_diff1 = upper[boll_len - 1] - lower[boll_len - 1]
                    if boll_diff1 < boll_diff5*4/3:
                        continue
                if self.window.price_inflow.isChecked() or self.window.big_contract.isChecked():
                    dayi=0
                    days=5
                    volumeCache = 0
                    tick_pass = True;
                    while True:
                        volumeIn,volumeOut,amountIn,amountOut = self.tick.getAmountInfo('300398',dayi)
                        dayi = dayi+1
                        if amountIn == 0 and amountOut == 0:
                            continue
                        '''近5日资金流入'''
                        if self.window.price_inflow.isChecked():
                            if amountIn - amountOut <= 0:
                                tick_pass = False
                                break
                        '''近5日大单增加'''
                        if self.window.big_contract.isChecked():
                            if volumeIn + volumeOut <= volumeCache*8/10:
                                tick_pass = False
                                break
                            volumeCache = volumeIn + volumeOut;
                        
                        days = days-1
                        if days == 0:
                            break
                    if tick_pass == False:
                        continue

                self.message += ",换手率:"+str(round(turnover,3))+'%'
                self.message += ",价格:"+str(round(price,3))+'元'
                self.message += ",近5日涨跌:"+str(round(inc_radio,3))+'%'
            except Exception as e:
                print(e)
                time.sleep(1)
                self.window.dialog_show_signal.emit(self.window.tr(codeBaseInfo.ix[i]['name']+":获取数据异常..."))
                pass
            
            
            self.message += ",流通股本:"+str(round(outstanding,3))+'亿股'
            self.message += ",市净率:"+str(round(pb,3))
            self.message += ",市盈率:"+str(round(pe,3))
            self.message += ",每股净资产:"+str(round(bvps,3))+'元'
            self.message += ",每股收益:"+str(round(esp,3))+'元'
            self.message += ",未分配利润:"+str(round(perundp,3))+'元'
            self.screenAddMessage(self.window.tr(self.message))
        self.window.choose_stocks_btn.setText("开始")

    def getDataFile(self):
        configData = None
        for root, dirs, files in os.walk('data'):
            if len(files) == 0:
                break
            configData = files[0]
            break
        
        if configData == None:
            return "data/"+datetime.date.today().strftime('%Y-%m-%d')+"_stock.data"
        try:
            LastUpdateTime=configData.split('_')[0]
            luTime = time.mktime(time.strptime(LastUpdateTime,'%Y-%m-%d'))
            needUpTime = time.mktime(time.strptime((datetime.date.today() - datetime.timedelta(days=updateCodeSourceDay)).strftime('%Y-%m-%d'),'%Y-%m-%d'))
            if needUpTime <= luTime:
                print("use old data")
                return "data/"+LastUpdateTime+"_stock.data"
        except Exception as e:
            pass
        os.remove("data/"+configData)
        print('need update data')
        return "data/"+datetime.date.today().strftime('%Y-%m-%d')+"_stock.data"
 
    def run(self):
        fileData = self.getDataFile()
        print('use dataFile <%s/%s>'%(os.getcwd(),str(fileData)))
        if not os.path.exists(str(fileData)):
            print(fileData+' not exists, We create it')
            try:
                self.window.dialog_show_signal.emit(self.window.tr("正在获取股票信息..."))
                codeBaseInfo = self.tick.getStockBasics()
            except Exception as e:
                self.window.dialog_show_signal.emit(self.window.tr("获取数据异常，请稍后重试..."))
                print(e)
                self.window.choose_stocks_btn.setText("开始")
                return
            codeBaseInfo.to_csv(fileData)
        codeBaseInfo = pd.read_csv(fileData,encoding='gbk', dtype=str)

        if self.window.run_way.currentIndex() == 0:
            self.chooseTicksByCondition(codeBaseInfo)
        elif self.window.run_way.currentIndex() == 1:
            self.screenShow('股票AI 接口未实现')
        elif self.window.run_way.currentIndex() == 2:
            self.screenShow('选股回测 接口未实现')
        elif self.window.run_way.currentIndex() == 3:
            self.screenShow('智能盯盘 接口未实现')
        elif self.window.run_way.currentIndex() == 4:
            self.screenShow('自动买卖 接口未实现')
        elif self.window.run_way.currentIndex() == 5:
            self.screenShow('指定股票分析 接口未实现')
        self.window.dialog_hide_signal.emit()
      
class FinanceMainWindow(QMainWindow, Ui_MainWindow):
    dialog_show_signal = QtCore.pyqtSignal(str)
    dialog_hide_signal = QtCore.pyqtSignal()

    def __init__(self):
        QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.setFixedSize(self.width(), self.height())
        self.setWindowIcon(QtGui.QIcon('pic/stock_wicon.ico'))
        self.initUi()

    def initUi(self):
        self.k_show = QWidget()
        self.k_pic = QLabel(self.k_show)
        self.k_pixmap = QtGui.QPixmap()
        self.dialogMessageBoxShow(self.tr("系统正在初始化"))

        '''股票市场'''
        self.market.insertItem(1,self.tr("全部"))
        self.market.insertItem(2,self.tr("上证"))
        self.market.insertItem(3,self.tr("深证"))
        self.market.insertItem(4,self.tr("创业板"))
        self.market.insertItem(5,self.tr("中小板"))

        '''盈亏'''
        self.price_gain_loss.insertItem(1,self.tr("全部"))
        self.price_gain_loss.insertItem(2,self.tr("亏损"))
        self.price_gain_loss.insertItem(3,self.tr("盈利"))

        '''股票状态'''
        self.st_status.insertItem(1,self.tr("全部"))
        self.st_status.insertItem(2,self.tr("ST股"))
        self.st_status.insertItem(3,self.tr("非ST股"))

        '''股票状态'''
        self.new_stocks.insertItem(1,self.tr("全部"))
        self.new_stocks.insertItem(2,self.tr("次新股"))
        self.new_stocks.insertItem(3,self.tr("非次新股"))

        '''换手率'''
        self.turnover_rate_min.setText(self.tr("5"))
        self.turnover_rate_min.setAlignment(Qt.AlignHCenter|Qt.AlignVCenter )
        self.turnover_rate_max.setText(self.tr("12"))
        self.turnover_rate_max.setAlignment(Qt.AlignCenter )

        self.turnover_rate_min.setValidator(QtGui.QIntValidator(0, 100, self ));
        self.turnover_rate_max.setValidator(QtGui.QIntValidator(0, 100, self ));

        '''股价'''
        self.price_min.setText(self.tr("10"))
        self.price_min.setAlignment(Qt.AlignHCenter|Qt.AlignVCenter )
        self.price_max.setText(self.tr("35"))
        self.price_max.setAlignment(Qt.AlignCenter )

        self.price_min.setValidator(QtGui.QIntValidator(0, 1000, self ));
        self.price_max.setValidator(QtGui.QIntValidator(0, 1000, self ));

        '''流通股本'''
        self.flow_stocks_min.setText(self.tr("0"))
        self.flow_stocks_min.setAlignment(Qt.AlignHCenter|Qt.AlignVCenter )
        self.flow_stocks_max.setText(self.tr("20"))
        self.flow_stocks_max.setAlignment(Qt.AlignCenter )

        self.flow_stocks_min.setValidator(QtGui.QIntValidator(0, 1000, self ));
        self.flow_stocks_max.setValidator(QtGui.QIntValidator(0, 1000, self ));

        '''市盈率'''
        self.priceearning_min.setText(self.tr("0"))
        self.priceearning_min.setAlignment(Qt.AlignHCenter|Qt.AlignVCenter )
        self.priceearning_max.setText(self.tr("200"))
        self.priceearning_max.setAlignment(Qt.AlignCenter )

        self.priceearning_min.setValidator(QtGui.QIntValidator(0, 3000, self ));
        self.priceearning_max.setValidator(QtGui.QIntValidator(0, 3000, self ));

        '''市净率'''
        self.market_to_boot_radio_min.setText(self.tr("0"))
        self.market_to_boot_radio_min.setAlignment(Qt.AlignHCenter|Qt.AlignVCenter )
        self.market_to_boot_radio_max.setText(self.tr("200"))
        self.market_to_boot_radio_max.setAlignment(Qt.AlignCenter )

        self.market_to_boot_radio_min.setValidator(QtGui.QIntValidator(0, 3000, self ));
        self.market_to_boot_radio_max.setValidator(QtGui.QIntValidator(0, 3000, self ));

        '''每股净资产'''
        self.perstocks_netasset_min.setText(self.tr("-2"))
        self.perstocks_netasset_min.setAlignment(Qt.AlignHCenter|Qt.AlignVCenter )
        self.perstocks_netasset_max.setText(self.tr("8"))
        self.perstocks_netasset_max.setAlignment(Qt.AlignCenter )

        rx = QtCore.QRegExp("(-|\\+)?[0-8]\\d");
        self.perstocks_netasset_min.setValidator(QtGui.QRegExpValidator(rx, self.perstocks_netasset_min));
        self.perstocks_netasset_max.setValidator(QtGui.QRegExpValidator(rx, self.perstocks_netasset_max));

        '''每股收益'''
        self.perstocks_grain_min.setText(self.tr("-2"))
        self.perstocks_grain_min.setAlignment(Qt.AlignHCenter|Qt.AlignVCenter )
        self.perstocks_grain_max.setText(self.tr("5"))
        self.perstocks_grain_max.setAlignment(Qt.AlignCenter )

        self.perstocks_grain_min.setValidator(QtGui.QRegExpValidator(rx, self.perstocks_grain_min));
        self.perstocks_grain_max.setValidator(QtGui.QRegExpValidator(rx, self.perstocks_grain_max));

        '''未分配利润'''
        self.undis_profi_min.setText(self.tr("-2"))
        self.undis_profi_min.setAlignment(Qt.AlignHCenter|Qt.AlignVCenter )
        self.undis_profi_max.setText(self.tr("4"))
        self.undis_profi_max.setAlignment(Qt.AlignCenter )

        self.undis_profi_min.setValidator(QtGui.QRegExpValidator(rx, self.undis_profi_min));
        self.undis_profi_max.setValidator(QtGui.QRegExpValidator(rx, self.undis_profi_max));

        '''近5日涨幅'''
        self.inc_radio_min.setText(self.tr("-2"))
        self.inc_radio_min.setAlignment(Qt.AlignHCenter|Qt.AlignVCenter )
        self.inc_radio_max.setText(self.tr("10"))
        self.inc_radio_max.setAlignment(Qt.AlignCenter )

        self.inc_radio_min.setValidator(QtGui.QRegExpValidator(rx, self.undis_profi_min));
        self.inc_radio_max.setValidator(QtGui.QRegExpValidator(rx, self.undis_profi_max));

        '''股价每日波动幅度'''
        self.price_wave_min.setText(self.tr("-3"))
        self.price_wave_min.setAlignment(Qt.AlignHCenter|Qt.AlignVCenter )
        self.price_wave_max.setText(self.tr("4"))
        self.price_wave_max.setAlignment(Qt.AlignCenter )

        self.price_wave_min.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp("(-|\\+)?\\d"), self.undis_profi_min));
        self.price_wave_max.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp("(-|\\+)?\\d"), self.undis_profi_max));

        '''设置工作模式'''
        self.run_way.insertItem(1,self.tr("选股"))
        self.run_way.insertItem(2,self.tr("股票AI"))
        self.run_way.insertItem(3,self.tr("选股回测"))
        self.run_way.insertItem(4,self.tr("智能盯盘"))
        self.run_way.insertItem(5,self.tr("自动买卖"))
        self.run_way.insertItem(6,self.tr("指定股票分析"))
        
        '''选择按钮'''
        self.choose_stocks_btn.clicked.connect(self.choose_btn)

        textEditStyle="border-radius: 10px;  border: 2px groove gray"
        self.turnover_rate_min.setStyleSheet(textEditStyle)
        self.turnover_rate_max.setStyleSheet(textEditStyle)
        self.price_min.setStyleSheet(textEditStyle)
        self.price_max.setStyleSheet(textEditStyle)
        self.flow_stocks_min.setStyleSheet(textEditStyle)
        self.flow_stocks_max.setStyleSheet(textEditStyle)
        self.priceearning_min.setStyleSheet(textEditStyle)
        self.priceearning_max.setStyleSheet(textEditStyle)
        self.perstocks_netasset_min.setStyleSheet(textEditStyle)
        self.perstocks_netasset_max.setStyleSheet(textEditStyle)
        self.perstocks_grain_min.setStyleSheet(textEditStyle)
        self.perstocks_grain_max.setStyleSheet(textEditStyle)
        self.undis_profi_min.setStyleSheet(textEditStyle)
        self.undis_profi_max.setStyleSheet(textEditStyle)
        self.inc_radio_max.setStyleSheet(textEditStyle)
        self.inc_radio_min.setStyleSheet(textEditStyle)
        self.FinanceShow.setStyleSheet(textEditStyle)
        self.market_to_boot_radio_min.setStyleSheet(textEditStyle)
        self.market_to_boot_radio_max.setStyleSheet(textEditStyle)
        self.price_wave_min.setStyleSheet(textEditStyle)
        self.price_wave_max.setStyleSheet(textEditStyle)
        self.choose_stocks_btn.setStyleSheet("QPushButton{background-color:rgb(58,61,64);color: rgb(210,210,210);\
                                           border-radius: 10px;  border: 2px groove rgb(38,41,44);\
                                           border-style: outset;}"
                                          "QPushButton:hover{background-color:rgb(58,61,64); color: black;}"
                                          "QPushButton:pressed{background-color:rgb(54,67,68);\
                                           border-style: inset;}"
                                           );
        self.setStyleSheet("QWidget{background-color:rgb(74,87,88);color:rgb(210,210,210)}"
                   "QLabel{font-size:12px;font-family:Roman times;}")
        
        self.FinanceShow.setStyleSheet("background-color:rgb(230,230,230);"
                                       "color:rgb(11,62,0);"
                                       "border-radius: 10px;  border: 2px groove rgb(100,100,100);"
                                       "gridline-color:red;"
                                       "selection-background-color:lightgray;")

        self.dialog_show_signal.connect(self.dialogMessageBoxShow)
        self.dialog_hide_signal.connect(self.dialogMessageBoxHide)
        
        self.FinanceShow.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.FinanceShow.customContextMenuRequested[QtCore.QPoint].connect(self.listViewMenu)
        self.k_show.setStyleSheet("QWidget{background-color:rgb(94,107,108);color:rgb(0,134,210)}")

        self.dialogMessageBoxHide()
        try:
            os.mkdir('data' )
        except Exception as e:
            pass

    def dialogMessageBoxShow(self, string):
        self.msg_process_show.setText(string)

    def dialogMessageBoxHide(self):
        self.msg_process_show.setText("")

    def uiValidator(self):
        ratemin = self.turnover_rate_min.text()
        ratemax = self.turnover_rate_max.text()
        pricemin = self.price_min.text()
        pricemax = self.price_max.text()
        flowstockmin = self.flow_stocks_min.text()
        flowstockmax = self.flow_stocks_max.text()
        priceearnmin = self.priceearning_min.text()
        priceearnmax = self.priceearning_max.text()
        netassetmin = self.perstocks_netasset_min.text()
        netassetmax = self.perstocks_netasset_max.text()
        grainmin = self.perstocks_grain_min.text()
        grainmax = self.perstocks_grain_max.text()
        undismin = self.undis_profi_min.text()
        undismax = self.undis_profi_max.text()
        inc_radio_max = self.inc_radio_max.text()
        inc_radio_min = self.inc_radio_min.text()
        boot_radio_min = self.market_to_boot_radio_min.text()
        boot_radio_max = self.market_to_boot_radio_max.text()
        price_wave_min = self.price_wave_min.text()
        price_wave_max = self.price_wave_max.text()

        if ratemin == '' or ratemin == '+' or ratemin == '-':
            return False
        if ratemax == '' or ratemax == '+' or ratemax == '-':
            return False
        if pricemin == '' or pricemin == '+' or pricemin == '-':
            return False
        if pricemax == '' or pricemax == '+' or pricemax == '-':
            return False
        if flowstockmin == '' or flowstockmin == '+' or flowstockmin == '-':
            return False
        if flowstockmax == '' or flowstockmax == '+' or flowstockmax == '-':
            return False
        if priceearnmin == '' or priceearnmin == '+' or priceearnmin == '-':
            return False
        if priceearnmax == '' or priceearnmax == '+' or priceearnmax == '-':
            return False
        if netassetmin == '' or netassetmin == '+' or netassetmin == '-':
            return False
        if netassetmax == '' or netassetmax == '+' or netassetmax == '-':
            return False
        if grainmin == '' or grainmin == '+' or grainmin == '-':
            return False
        if grainmax == '' or grainmax == '+' or grainmax == '-':
            return False
        if undismax == '' or undismax == '+' or undismax == '-':
            return False
        if undismin == '' or undismin == '+' or undismin == '-':
            return False
        if inc_radio_min == '' or undismax == '+' or undismax == '-':
            return False
        if inc_radio_max == '' or undismin == '+' or undismin == '-':
            return False
        if boot_radio_min == '' or boot_radio_min == '+' or boot_radio_min == '-':
            return False
        if boot_radio_max == '' or boot_radio_max == '+' or boot_radio_max == '-':
            return False
        if price_wave_min  == '' or price_wave_min == '+' or price_wave_min == '-':
            return False
        if price_wave_max  == '' or price_wave_max == '+' or price_wave_max == '-':
            return False

        return True

    def choose_btn(self):
        if self.choose_stocks_btn.text() == "终止":
            self.choose_stocks_btn.setText("开始")
            return
        else:
            self.choose_stocks_btn.setText("终止")

        if not self.uiValidator():
            reply = QMessageBox.information(self,"警告","参数无效", QMessageBox.Yes) 
            return

        self.FinanceShow.clear()
        self.thread = chooseBtnThread(self)
        self.thread.start()

    def listViewMenu(self,point):
        popMenu = QMenu()
        popMenu.setStyleSheet("background-color:rgb(200,200,200);color:rgb(0,0,0)")
        k_pic = QAction('日K线图', self)
        k_pic.triggered.connect(self.kmenu_action_handler) 
        popMenu.addAction(k_pic)
        popMenu.exec_(QtGui.QCursor.pos())

    def kmenu_action_handler(self):
        codeinfo = self.FinanceShow.currentItem().text()
        codeList = codeinfo.split(',')
        print('选中：'+codeList[0])

        picSource=sinaTick(codeList[0])
        self.k_pixmap.loadFromData(picSource.getK())
        self.k_pic.setPixmap(self.k_pixmap)  
        self.k_show.setFixedSize(self.k_pixmap.width()+5, self.k_pixmap.height()+5);  
        self.k_show.setWindowTitle(codeList[0]+': 日K线图')
        self.k_show.setWindowFlags(Qt.WindowStaysOnTopHint);
        self.k_show.show()

    def __del__(self):
        self.dialog.hide()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FinanceMainWindow()
    window.show()
    sys.exit(app.exec_())
