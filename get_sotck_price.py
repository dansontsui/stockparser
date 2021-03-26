#!/usr/bin/env python3

# -*- coding: utf-8 -*-

import csv
import numpy as np
import datetime as dt
import pandas as pd
from datetime import timedelta
import httplib2
from urllib.parse import urlencode
import requests
from io import StringIO
import re
import os

def twdate(date):
    year  = date.year-1911
    month = date.month
    day   = date.day
    twday = '{}/{:02}/{:02}'.format(year,month,day)
    return twday

#20200109

def downloadTWSE(datestr):
    # 下載股價
    r = requests.post('https://www.twse.com.tw/exchangeReport/MI_INDEX?response=csv&date=' + datestr + '&type=ALL')
    if len(r.text) == 0:
        return ''
    # 整理資料，變成表格
    df = pd.read_csv(StringIO(r.text.replace("=", "")), 
                header=["證券代號" in l for l in r.text.split("\n")].index(True)-1)
    # 整理一些字串：
    df = df.apply(lambda s: s.astype(str).str.replace(",", "").replace("+", "1").replace("-", "-1"))

    filename = 'stock_rebuld_data/'+datestr+"_twsestock.csv"
    df.to_csv(filename,encoding = 'utf=8')
    return filename
    #print(df.head())

def downloadOTC1(date):

    # 整理資料，變成表格
    f = open("otcstock.csv", mode='r', encoding='utf-8')
    #r = f.read()
    #f.close()
    #sio = StringIO(r)
    line2 = ''
    start = 0
    end = 0
    for line1 in f.readlines():
        if len(line1) <=1:
            continue
        if line1.find('代號') >=0:
            start = 1
        if line1.find('管理股票') >=0:
            end = 1
        if start==1 and end==0:
            line2 += line1
    f.close()            
    f = open("otcstock_reset.csv", mode='w', encoding='utf-8')
    f.write(line2)
    f.close()
    df = pd.read_csv('otcstock_reset.csv')
    return 

def internet_otc_to_csv(IOtext):
    start = 0
    end  = 0
    sdate = ''
    line2 = ''
    for line1 in IOtext.readlines():
        if len(line1) <=1:
            continue
        if line1.find('資料日期')>=0:
            r = re.search(r'\d+\S+',line1)
            d = r.group()
            s = d.split('/')
            sdate = s[0] + s[1] + s[2]
        if line1.find('代號') >=0:
            start = 1
        if line1.find('管理股票') >=0:
            end = 1
        if start==1 and end==0:
            line2 += line1
    filename = 'stock_rebuld_data/'+sdate+"_otcstock.csv"
    f = open(filename, mode='w', encoding='utf-8')
    f.write(line2)
    f.close()
    return filename

def downloadOTCoriginaldate(date):
    sd = twdate(date)
    sd1=sd.split('/')
    sd2 = sd1[0] + sd1[1] + sd1[2]
    
    url = 'https://www.tpex.org.tw/web/stock/aftertrading/daily_close_quotes/stk_quote_result.php?l=zh-tw&o=csv&d='+sd+'&s=0,asc,0'
    #url = 'https://www.tpex.org.tw/web/stock/aftertrading/daily_close_quotes/stk_quote_result.php?l=zh-tw&o=csv&d='+sd+'&s=0,asc,0'
    r = requests.post(url)
# 整理資料，變成表格
    f = open(sd2+"_orginal_data.csv", mode='w', encoding='utf-8')
    sio = StringIO(r.text)
    f.write(sio.read())
    f.close()

def downloadOTC(date):
    #sd = twdate(date)
    sd = date
    print("get otc data [%s]" % sd)
    sd1=sd.split('/')
    sd2 = sd1[0] + sd1[1] + sd1[2]
    url = 'https://www.tpex.org.tw/web/stock/aftertrading/daily_close_quotes/stk_quote_result.php?l=zh-tw&o=csv&d='+sd+'&s=0,asc,0'
    print(url)
    r = requests.post(url)
# 整理資料，變成表格



    f = open('stock_original_data/'+sd2+"_original_data.csv", mode='w', encoding='utf-8')
    sio = StringIO(r.text)
    sioSize = sio.seek(0,2)
    f.write(sio.read())
    f.close()

    if sioSize < 2048:
        return ''
    sio.seek(0)
    #sio = StringIO(r.text)
    fileName = internet_otc_to_csv(sio)
    #df = pd.read_csv(fileName)
    return fileName
def get_twse_df_from_history_from_file(filename,stockid):
      #filename = 'stock_rebuld_data/'+sdate+"_otcstock.csv"
     df = pd.read_csv(filename,encoding='utf-8')
     row  =  df.shape[0]
     return df["證券代號"]
     
def get_twse_history_from_file(filename,stockid):
     #filename = 'stock_rebuld_data/'+sdate+"_otcstock.csv"
     df = pd.read_csv(filename,encoding='utf-8')
     row  =  df.shape[0]
     for r in range(0,row):
         if df["證券代號"][r] == stockid:
             return df["收盤價"][r], df["漲跌價差"][r], df["開盤價"][r],df["最高價"][r],df["最低價"][r]
     return 'ff','ff','ff','ff','ff'
def get_otc_history_from_file(filename,stockid):
     #filename = 'stock_rebuld_data/'+sdate+"_otcstock.csv"
     df = pd.read_csv(filename,encoding='utf-8')
     row  =  df.shape[0]
     for r in range(1,row):
         if df["代號"][r] == stockid:
             return df["收盤 "][r], df["漲跌"][r], df["開盤 "][r],df["最高 "][r],df["最低"][r]
     return 'ff','ff','ff','ff','ff'

def get_otc_history_from_internet():
    for i in range(20,0,-1):
        downloadDate= dt.date.today() - timedelta(days=i)
        downloadOTC(downloadDate)


def showStock(stockID, stockName, Open, High, Low, Close,Volume):

    showLen=8

    #print('\nTWSE count=',len(stockID))

    print('ID:',stockID[:showLen])

    print('Name:',stockName[:showLen])

    print('Open:',Open[:showLen])

    print('High:',High[:showLen])

    print('Low:',Low[:showLen])

    print('Close:',Close[:showLen])

    print('Volume:',Volume[:showLen])

#main

downloadDate= dt.date.today() #- timedelta(days=2)

# download TWSE
'''
listTWSE = downloadTWSE(downloadDate)

#get result
result = np.array(listTWSE)

stockID=result[:,0]

stockName=result[:,1]

Open=result[:,2]

High=result[:,3]

Low=result[:,4]

Close=result[:,5]

Volume=result[:,6]

print('TWSE count=',len(stockID))

#showStock(stockID, stockName, Open, High, Low, Close,Volume)


'''
#download OTC
#listOTC = downloadOTC1(downloadDate)
#for i in range(20,0,-1):
#    downloadDate= dt.date.today() - timedelta(days=i)
#    listOTC=downloadOTC(downloadDate)

'''
#get result

result = np.array(listOTC)

stockID=result[:,0]

stockName=result[:,1]

Open=result[:,2]

High=result[:,3]
Low=result[:,4]
Close=result[:,5]
Volume=result[:,6]
print('OTC count=',len(stockID))
#showStock(stockID, stockName, Open, High, Low, Close,Volume)
#save result
Title =  ['股票代碼', '股票名稱', '開盤價', '最高價','最低價','收盤價','成交股數']
f = open("TwStockList.csv","w")
w = csv.writer(f, lineterminator='\n')
w.writerows([Title])
w.writerows(listTWSE)   #TWSE list
w.writerows(listOTC)    #OTC list
f.close()
'''