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
    filepath = stockid+"_database.csv"
    foder = stockid
    if os.path.isdir(foder):
        print('dir exists')
    else:
        print('dir not exists')
        #create folder
    # 檢查檔案是否存在
    if os.path.isfile(filepath):
        print("檔案存在。")
    else:
        print("檔案不存在。")
        return
'''
date = '20180102'
r = requests.get('https://tw.stock.yahoo.com/d/s/major_8299.html')
f = open("major.txt", mode='w', encoding='utf-8')
f.write(r.text)
f.close()
'''
check_db_file_exist("8299")
#f = open("major.txt", mode='r', encoding='utf-8')
#fs = f.read()
#soup = BeautifulSoup(open(fs),'html.parser')
sd = str(datetime.date.today())
asd = sd.split("-")
sdate = asd[0]+asd[1]+asd[2] #get date
sdate = "1100302"
list_header = [] 
data = [] 
soup = BeautifulSoup(open("major_1100302.html",encoding="utf-8"), "html.parser")
#header = soup.find_all("table")[0].find("tr") 
header = soup.find_all("table")[3].find("tr")
for items in header: 
    try: 
        list_header.append(items.get_text()) 
    except: 
        continue
HTML_data = soup.find_all("table")[3].find_all("tr")[1:]
for element in HTML_data: 
    sub_data = [] 
    for sub_element in element: 
        try: 
            sub_data.append(sub_element.get_text()) 
        except: 
            continue
    data.append(sub_data) 
dataFrame = pd.DataFrame(data = data, columns = list_header)
#dataFrame1 = pd.read_csv("database.csv",encoding='utf-8')


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

dataFrame1.to_csv('database.csv', encoding='utf-8',index=0) 