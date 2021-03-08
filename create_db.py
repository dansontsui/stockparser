import requests
from io import StringIO
import pandas as pd
import os 
import sys 
from bs4 import BeautifulSoup 
import datetime
import re
#if db not exists

def check_db_file_exist(stockid):
    filepath = "db\\"+stockid+"_database.csv"
    foder = "db"
    if os.path.isdir(foder):
        print('dir exists')
    else:
        print('dir not exists')
        #create folder
    # 檢查檔案是否存在
    if os.path.isfile(filepath):
        print("檔案存在。")
        return True
    else:
        print("檔案不存在。")
        return False
'''
date = '20180102'
r = requests.get('https://tw.stock.yahoo.com/d/s/major_8299.html')
f = open("major.txt", mode='w', encoding='utf-8')
f.write(r.text)
f.close()
'''
def create_data_base(dataFrame,sdate,stockid):
    if check_db_file_exist(stockid) == True:
        return 
    Brokerage = []
    data1=[]
    Brokerage.append('日期')
    data1.append(sdate)
    for l in range(len(dataFrame["買超券商"])):
        if len(Brokerage) == 0:
            Brokerage.append(dataFrame["買超券商"][l])
            data1.append(dataFrame["買超"][l])
        else:
            findbrok = 0
            if dataFrame["買超券商"][l] in Brokerage:
                findbrok = 1
            if findbrok == 0:
                Brokerage.append(dataFrame["買超券商"][l])
                data1.append(dataFrame["買超"][l])
            findbrok = 0
            if dataFrame["賣超券商"][l] in Brokerage:
                findbrok = 1
            if findbrok == 0:
                Brokerage.append(dataFrame["賣超券商"][l])
                data1.append(dataFrame["賣超"][l])            

    data2 = []
    data2.append(data1)
    dataFrame1 = pd.DataFrame(data = data2, columns = Brokerage)
    dataFrame1.to_csv('db\\'+stockid+'_database.csv', encoding='utf-8',index=0) 