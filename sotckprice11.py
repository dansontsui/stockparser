#!/usr/bin/env python3

# -*- coding: utf-8 -*-

import csv
import numpy as np
import datetime as dt
import pandas as pd
from datetime import timedelta
import httplib2
from urllib.parse import urlencode

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



def downloadOTC(date):

    url='http://www.tpex.org.tw/web/stock/aftertrading/otc_quotes_no1430/stk_wn1430_print.php?l=zh-tw&d='+twdate(date)+'&se=EW'


    table = pd.read_html(url)[0]

    rowCount = table.values.shape[0]-1;

    srcOTC = table.values[:rowCount].tolist()



    #search stock list

    firstIndex=0

    lastIndex=0

    for i in range(len(srcOTC)):

        row = srcOTC[i]

        if (row[0]=='1258'):  #1st stock ID

            firstIndex=i

        elif (row[0]=='9962'):  #lastest stock ID

            lastIndex=i+1

            break

    #print('OTC index=',firstIndex,lastIndex)

    listOTC = srcOTC[firstIndex:lastIndex]

    resultOTC = [row[:2]+row[4:7]+row[2:3]+row[7:8] for row in listOTC]

    #print(resultOTC[0])

    return resultOTC



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

downloadDate= dt.date.today() - timedelta(days=2)
# download TWSE
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



#download OTC

listOTC=downloadOTC(downloadDate)

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