import requests
import json
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup 
import csv
import re
import datetime as dt
import time
import log
import logging
import os


def check_db_file_exist(filename):
    filepath = filename
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
def fubon_appen_data_to_database(brokagename,count,dbname,sdate):
    
    #dataFrame = pd.read_csv(rebuild_csv_filename,encoding='utf-8')
    db_dataFrame = pd.read_csv(dbname,encoding='utf-8')
    if brokagename in db_dataFrame.columns:
        return
    else:
        dbrow = db_dataFrame.shape[0]
        dbcol = db_dataFrame.shape[1]
        oriCount = db_dataFrame[brokagename][dbrow]
        
    return
def fubon_create_database(rebuild_csv_filename,brokagename,dbname,sdate):

    s1 = sdate[0:3]+"/"+sdate[3:5]+"/"+sdate[5:7]
    sclose=0
    srage=0
    sopen=0
    shigh=0
    slow=0
    #sclose,srage,sopen,shigh,slow = get_sotck_price.get_otc_history_from_file(sdate,stockid)
    #if sclose == 'ff':
    #    sclose = 'ff'
    Brokerage = []
    data1=[]
    Brokerage.append('日期')
    data1.append(sdate)
    Brokerage.append('收盤')
    data1.append(sclose)
    Brokerage.append('漲跌')
    data1.append(srage)
    Brokerage.append('開盤')
    data1.append(sopen)
    Brokerage.append('最高')
    data1.append(shigh)
    Brokerage.append('最低')
    data1.append(slow)
    dataFrame = pd.read_csv(rebuild_csv_filename,encoding='utf-8')
    Brokerage.append(brokagename)
    data1.append(dataFrame["差額"][0])

    data2 = []
    data2.append(data1)

    dataFrame1 = pd.DataFrame(data = data2, columns = Brokerage)
    dataFrame1.to_csv(dbname, encoding='utf-8',index=0) 

    '''
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
    '''


def trans_data_to_db(foldername,rebuild_csv_filename,sdate):
    filename = foldername+'\\'+rebuild_csv_filename
    borkDataFrame = pd.read_csv(filename,encoding='utf-8')
    brokagename = rebuild_csv_filename.split('_')
    rowcount = borkDataFrame.shape[0]
    columncount = borkDataFrame.shape[1]
    pattern = re.compile("[A-Za-z]+")
    for index,row in borkDataFrame.iterrows():
        s = row['券商名稱'] #stock name
        sid = re.search(r'[A-Za-z0-9]+',s).group()
        sname = re.search(r'[^A-Za-z0-9]+',s).group()
        print(sid +" " + sname)
        dbname = 'db\\'+sid +"_"+sname+"_db.csv"
        if check_db_file_exist(dbname) == False: #file not exist
            fubon_create_database(filename,brokagename[0],dbname,sdate)
        else:
            fubon_appen_data_to_database(brokagename[0],row['差額'],dbname,sdate)


        

        
        
    #temp1 = filename.split('_',filename)
    #dbname = 'db\\'+temp1[0]+'_dababase.csv'




if __name__ == '__main__':
    #03-11 18:21:13 - Log.Parser - INFO 

    logger = logging.getLogger('Log.Parser')
    logger.setLevel(logging.DEBUG)
    #formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s',datefmt='%m-%d %H:%M:%S')
    formatter = logging.Formatter('%(asctime)s - %(message)s',datefmt='%m-%d %H:%M:%S')
    fh1 = logging.FileHandler(filename="test.py.log", mode='a')
    console = logging.StreamHandler()
    console.setFormatter(formatter)
    console.setLevel(logging.INFO)
    fh1.setLevel(logging.DEBUG)
    fh1.setFormatter(formatter)
    logger.addHandler(console)
    logger.addHandler(fh1)
    log.log("start")

    downloadDate= dt.date.today()
    year  = downloadDate.year
    month = downloadDate.month
    day   = downloadDate.day-1
    twday = '{}-{:1}-{:1}'.format(year,month,day)
    folder_twday= '{}{:02}{:02}'.format(year,month,day)

    
    try:
        os.mkdir('db')
    except OSError:
        print ("Creation db of the directory %s failed" % folder_twday)
    else:
        print ("Successfully db created the directory %s " % folder_twday)

    

    pattern = re.compile("[A-Za-z]+")
    path = 'histock_rebuild_data\\'+folder_twday
    for dirpath, dirnames, files in os.walk(os.path.abspath(path)):
        if dirpath.find('_NoTest') != -1:
            continue
        files.sort()
        for _file in files:
            fs = str(_file)
            if fs.find("csv") <0:
                continue
            trans_data_to_db(dirpath,fs,folder_twday)




    

