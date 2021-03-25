#!/usr/bin/env python3

# -*- coding: utf-8 -*-

#import csv
#import numpy as np
#import datetime as dt
import pandas as pd
#from datetime import timedelta
#import httplib2
#from urllib.parse import urlencode
#import requests
#from io import StringIO
import re
#import os

def twdate(date):
    year  = date.year-1911
    month = date.month
    day   = date.day
    twday = '{}/{:02}/{:02}'.format(year,month,day)
    return twday
    
def downloadTWSE(date):
    url="http://www.twse.com.tw/ch/trading/exchange/MI_INDEX/MI_INDEX.php"
    values = {'download`' : 'csv', 'qdate' : twdate(date), 'selectType' : 'ALLBUT0999' }
    agent = 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0'
    #httplib2.debuglevel = 1
    conn = httplib2.Http('.cache')
    headers = {'Content-type': 'application/x-www-form-urlencoded',
               'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
               'User-Agent': agent}

    resp, content = conn.request(url, 'POST', urlencode(values), headers)

    respStr = str(content.decode('utf-8'))

    srcTWSE = list(csv.reader(respStr.split('\n'), delimiter=','))
    #search stock list
    firstIndex=0
    lastIndex=0
    for i in range(len(srcTWSE)):
        row = srcTWSE[i]
        if (len(row)>15):  #16 columns
            row[0]=row[0].strip(' =\"')
            row[1]=row[1].strip(' =\"')
            if (row[0]=='0050'):  #1st stock ID

                firstIndex=i

            elif (row[0]=='9958'): #lastest stock ID

                lastIndex=i+1

                break

    #print('TWSE index=',firstIndex,lastIndex)

    listTWSE = srcTWSE[firstIndex:lastIndex]

    #print(listTWSE[0])

    resultTWSE = [row[:2]+row[5:9]+row[2:3] for row in listTWSE]

    #print(resultTWSE[0])

    return resultTWSE



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

def get_otc_history_from_file(sdate,stockid):
     filename = 'stock_rebuld_data/'+sdate+"_otcstock.csv"
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

aa = [['A',1,2,3],['B',4,5,6],['C',7,8,9]]
bb = [['D',999,999,999],['E',777,777,777]]
'''
df = pd.read_csv('db/6142_database_1_test.csv',encoding='utf-8')
#df = pd.DataFrame(data = aa)
#df1 = pd.DataFrame(data = bb)

ss0 = df.iloc[0:49,6:10]
ss1 = df.iloc[1:50,6:10]
ss1 = ss1.reset_index(drop=True)
print (ss1)
ss3 = ss1-ss0
print(ss3)
df =df.drop(0)
df = df.reset_index(drop=True)
df.loc[0:49,6:10] = ss3



'''
df = pd.read_csv('db/6142_database_1.csv',encoding='utf-8')
#df1 = pd.read_csv('db/6142_database_1.csv',encoding='utf-8')
df.reset_index(drop=True)
print(df.head())
s = df[1:10]

rows=df.shape[0]
cols=df.shape[1]

#ss0 = df.iloc[0:49,6:10]
#ss1 = df.iloc[1:50,6:10]
#ss1 = ss1.reset_index(drop=True)

ss1 = df.iloc[0:rows,6:cols-1]
ss2 = df.iloc[1:rows+1,6:cols-1]
ss2 = ss2.reset_index(drop=True)
print (ss1)
ss3 = ss2-ss1
print(ss3)
df =df.drop(0)
df = df.reset_index(drop=True)
df.loc[0:rows,6:cols-1] = ss3

df.to_csv('dis.csv',encoding='utf-8',index=0)




    