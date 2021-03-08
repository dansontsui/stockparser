import requests
#from io import StringIO
import pandas as pd
import os 
import sys 
from bs4 import BeautifulSoup 
import datetime

'''
date = '20180102'
r = requests.get('https://tw.stock.yahoo.com/d/s/major_8299.html')
f = open("major.txt", mode='w', encoding='utf-8')
f.write(r.text)
f.close()
'''


data = {'Name': ['Jai', 'Princi', 'Gaurav', 'Anuj'], 
        'Height': [5.1, 6.2, 5.1, 5.2], 
        'Qualification': ['Msc', 'MA', 'Msc', 'Msc']} 
  
# Convert the dictionary into DataFrame 
df = pd.DataFrame(data) 
  
# Declare a list that is to be converted into a column 
address = ['Delhi', 'Bangalore', 'Chennai', 'Patna'] 
  
# Using 'Address' as the column name 
# and equating it to the list 
df['Address'] = address 
  
# Observe the result 
df 

#f = open("major.txt", mode='r', encoding='utf-8')
#fs = f.read()
#soup = BeautifulSoup(open(fs),'html.parser')
sd = str(datetime.date.today())
asd = sd.split("-")
sdate = asd[0]+asd[1]+asd[2] #get date



def collectdata(filename,sdate,stockid):

    list_header = [] 
    data = [] 
    dataFrame = pd.read_csv(filename,encoding='utf-8')
    
    #dataFrame1 = pd.read_csv("database.csv",encoding='utf-8')
    #dbname = stockid+"_database.csv"
    dbname = "db\\"+stockid+"_database.csv"
    major_frame = pd.read_csv(dbname,encoding='utf-8')
    rowcount = major_frame.shape[0]
    columncount = major_frame.shape[1]
    rowcount1 = dataFrame.shape[0]
    columncount1 = dataFrame.shape[1]

    for c in range(0,rowcount):
        if str(major_frame["日期"][c]) == str(sdate):
            return
    Brokerage = []
    data1=[]
    #檢查是否有新增brokerage ,有的話要加入major_frame 的list
    for l in range(len(dataFrame["買超券商"])):
        #如果該brokerage不存在  新增一個brokerage
        if dataFrame["買超券商"][l] not in major_frame.columns:
            #看目前資料庫有幾個row
            for i in range(0,rowcount):
                 #之前的資料都填0 , PS 之前該brokerage沒有 buy or sell
                data1.append(0)
            major_frame[dataFrame["買超券商"][l]] = data1
        data1.clear()
        if dataFrame["賣超券商"][l] not in major_frame.columns:
            #看目前資料庫有幾個row
            for i in range(0,rowcount):
                #之前的資料都填0 , PS 之前該brokerage沒有 buy or sell
                data1.append(0) 
            major_frame[dataFrame["賣超券商"][l]] = data1
        data1.clear()

    rowcount = major_frame.shape[0]
    columncount = major_frame.shape[1]
    rowcount1 = dataFrame.shape[0]
    columncount1 = dataFrame.shape[1]

    #新增brokerage完成後 要新增row
    newinfo = []
    newinfo.append(sdate)
    #已major db為主要開始搜尋今日的資料是否有符合
    #要讓 newinfo的資料順序 對其 major db的欄位順序
    #如此 新增的row 才會對齊欄位
    for r in range(1,columncount): 
        total =0

        for c in range(0,rowcount1):
            #保留庫存
            total = major_frame[major_frame.columns[r]][rowcount-1]
            if major_frame.columns[r] == "元大證券 ":
                total = major_frame[major_frame.columns[r]][rowcount-1]
            
            if dataFrame["買超券商"][c] == major_frame.columns[r]:
                newd1 = dataFrame["買超"][c] 
                oldd1 = major_frame[dataFrame["買超券商"][c]][rowcount-1]
                total = int(oldd1) + int(newd1)
                break
            elif dataFrame["賣超券商"][c] == major_frame.columns[r]:
                newd1 = dataFrame["賣超"][c] 
                oldd1 = major_frame[dataFrame["賣超券商"][c]][rowcount-1]
                total = int(oldd1) + int(newd1)
                break
        newinfo.append(total)
    
    major_frame.loc[rowcount] = newinfo #add new row
    major_frame.to_csv(dbname, encoding='utf-8',index=0) #update db

#test 
#collectdata('8299_1100303.csv','1100303')    