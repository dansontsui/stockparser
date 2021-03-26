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
import Build_fubon_data_to_my_db
import get_sotck_price

def parser_major_data_to_csv_data(folder_twday,htmldata,findBrokName,mainid,subid,sdate):
    soup = BeautifulSoup(htmldata, "html.parser")
    #header = soup.find_all("table")[3].find("tr")[1:]
    #header = soup.find_all("td",{"class":"t2"})
    #header = soup.find_all("table",{"class":"t0"}).find('tr')
    #if str(soup).find('無資料') >=0 :
        #return None
    columns1 =[]
    table = soup.find_all('table', {'class': 't01'})
    if len(table) <=1:
        return None
    #for tableindex in range(0,2):
    aa = table[1].find_all('tr')
    #sartrecordcoulumnName = 0
    #for tt in aa[0]:
    data = []
    dataarr = []
    aa1 = aa[0].find_all('td')
    if len(aa1) == 0 :
        return None
    for c1 in aa1:
        columns1.append(c1.text)
    aa1 = aa[1].find_all('td')
    if len(aa1) == 0 :
        return None
    for c1 in aa1:
        data.append(c1.text)
    data[0] = data[0].replace('/','-')
    dataarr.append(data)
    

    dataFrame = pd.DataFrame(data = dataarr, columns = columns1)
    dataFrame.to_csv("histock_rebuild_data/"+folder_twday+"/"+findBrokName+'_'+mainid+'_'+subid+'_'+sdate+"_rebuid.csv",encoding='utf-8',index=0)
    return dataFrame
    #print(dataFrame.head())

def save_oridata_form_fubon(folder_twday,findBrokName,mainid,subid,sdate):
    #load data form internet

    major_file_name = 'histock_original_data/'+folder_twday+"/"+findBrokName+'_'+mainid+'_'+subid+'_major_fubon_1_'+sdate+'.html'

    #if os.path.isfile(major_file_name):
    #    return True,major_file_name

    headers = {
        'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36',
        'Cookie':'gr_user_id=1f9ea7ea-462a-4a6f-9d55-156631fc6d45; bid=vPYpmmD30-k; ll="118282"; ue="codin; __utmz=30149280.1499577720.27.14.utmcsr=douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/doulist/240962/; __utmv=30149280.3049; _vwo_uuid_v2=F04099A9dd; viewed="27607246_26356432"; ap=1; ps=y; push_noty_num=0; push_doumail_num=0; dbcl2="30496987:gZxPfTZW4y0"; ck=13ey; _pk_ref.100001.8cb4=%5B%22%22%2C%22%22%2C1515153574%2C%22https%3A%2F%2Fbook.douban.com%2Fmine%22%5D; __utma=30149280.833870293.1473539740.1514800523.1515153574.50; __utmc=30149280; _pk_id.100001.8cb4=255d8377ad92c57e.1473520329.20.1515153606.1514628010.'
    }
    url = 'http://fubon-ebrokerdj.fbs.com.tw/z/zc/zco/zco0/zco0.djhtm?A=8299&BHID='+mainid+'&b='+subid+'&C=1&D='+sdate+'&E='+sdate+'&ver=V3'
    #url = 'https://fubon-ebrokerdj.fbs.com.tw/z/zg/zgb/zgb0.djhtm?a='+mainid+'&b='+subid+'&c=E&e='+sdate+'&f='+sdate
    r = requests.get(url,headers = headers)
    #parser html date
    '''
    s = re.findall(r"資料日期\S+.+",r.text)
    s1 = re.search(r"\d+\s+/\d+ /\d+",s[0])
    s2 = s1.group()
    s2 = re.split(r" /",s2)
    filedate = s2[0]+s2[1]+s2[2] 
    #download otc all stock data
    get_sotck_price.downloadOTC(s2[0]+"/"+s2[1]+"/"+s2[2])
    '''
    
    #f = open(major_file_name, mode='w', encoding='utf-8')
    #f.write(r.text)
    #f.close()
    return False,r.text

def load_broker_id_from_csv():
    #pd.read_csv处理空格和tab分割符问题
    df=pd.read_csv('broker_id.csv',encoding='utf-8',sep='\\s+')
    return df

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


df = pd.DataFrame
df = load_broker_id_from_csv()
downloadDate= dt.date.today()
year  = downloadDate.year
month = downloadDate.month
day   = downloadDate.day
twday = '{}-{:1}-{:1}'.format(year,month,day)
folder_twday= '{}{:02}{:02}'.format(year,month,day)
#folder_twday = "2021-03-14"
row = df.shape[0]
col = df.shape[1]
a = str(df.代號[0])

#craete folder

try:
    os.makedirs('stock_original_data')
except OSError:
    print ("Creation of the directory")

try:
    os.makedirs('stock_rebuld_data')
except OSError:
    print ("Creation of the directory")

pattern = re.compile("[A-Za-z]+")

# if found match (entire string matches pattern)
#a = str(df.代號[r])
stockid = '6142'
#stockid = '8299'
#for dc in range(19,-1,-1):

#startdate = dt.datetime(2021,3,25)
#enddate = dt.datetime(2021, 3,25)

startdate = dt.datetime.today()
enddate = dt.datetime.today()

totaldays = (enddate - startdate).days + 1

for daynumber in range(totaldays):
    datestring = (startdate + dt.timedelta(days = daynumber)).date()
    
        #print datestring.strftime("%Y%m%d") 
    to0 = time.time()
    year = datestring.year
    month = datestring.month
    day   = datestring.day
    twday = '{}-{:1}-{:1}'.format(year,month,day)
    dbDate = '{}-{:02}-{:02}'.format(year,month,day)
    folder_twday= '{}{:02}{:02}'.format(year,month,day)
    otcday= '{}/{:02}/{:02}'.format(year-1911,month,day)
    otc_rebuild_name = otcday.replace('/','')
    otc_filename = 'stock_rebuld_data/'+folder_twday+"_twsestock.csv"
    if Build_fubon_data_to_my_db.check_db_file_exist(otc_filename) == False: 
        fn = get_sotck_price.downloadTWSE(folder_twday)
        if fn == '':
            continue
        sclose,srage,sopen,shigh,slow = get_sotck_price.get_twse_history_from_file(otc_filename,stockid)
    else:
        sclose,srage,sopen,shigh,slow = get_sotck_price.get_twse_history_from_file(otc_filename,stockid)
    Build_fubon_data_to_my_db.gsclose = sclose
    Build_fubon_data_to_my_db.gsrage = srage
    Build_fubon_data_to_my_db.gsopen = sopen
    Build_fubon_data_to_my_db.gshigh = shigh
    Build_fubon_data_to_my_db.gslow = slow
    #1100318
    #folder_twday = "20210311"

    

    try:
        os.makedirs('histock_original_data/'+folder_twday)
    except OSError:
        print ("Creation of the directory %s failed" % folder_twday)
    else:
        print ("Successfully created the directory %s " % folder_twday)

    try:
        os.makedirs("histock_rebuild_data/"+folder_twday)
    except OSError:
        print ("Creation of the directory %s failed" % folder_twday)
    else:
        print ("Successfully created the directory %s " % folder_twday)

    mainBrok = ''
    subBrok = ''
    mainBrokName = ''
    findBrokName = ''

    dbname = 'db/'+stockid+'_database_1.csv'
    DataFrameDb = None
   
    if Build_fubon_data_to_my_db.check_db_file_exist(dbname) == True: #file exist
        DataFrameDb = pd.read_csv(dbname,encoding='utf-8')
    
    for r in range(0,row):#每一家證券公司
        print(folder_twday + ">> " + str(r) + "/" + str(row))
        if df.代號[r][3]=='0' and (df.代號[r][2]>='0' and df.代號[r][2]<='9'):
            mainBrok = df.代號[r]
            subBrok = df.代號[r]
            findBrokName = mainBrokName = df.證券商名稱[r]
            log.log('...main-id:'+mainBrok+'-'+subBrok)
        #elif df.證券商名稱[r].find(mainBrokName) >=0:
        elif mainBrok.find(df.代號[r][:2]) >=0:
            s = df.證券商名稱[r]
            subBrok = df.代號[r]
            findBrokName = df.證券商名稱[r]
            brokage_id_utf8 = subBrok.encode("UTF-8")
            if pattern.fullmatch(df.代號[r][3]) is not None:
                subBrok = '00'+str(hex(brokage_id_utf8[0]))+'00'+str(hex(brokage_id_utf8[1]))+'00'+str(hex(brokage_id_utf8[2]))+'00'+str(hex(brokage_id_utf8[3]))
                subBrok =subBrok.replace('0x','')
                log.log(subBrok)
            else:
                log.log('.....sub-id:'+subBrok)
        else:
            log.log('assert no found '+df.代號[r]+' '+df.證券商名稱[r])
        try:            
            if subBrok == '0031003000340044':
                subBrok = '0031003000340044'
            log.log('.....name  :'+findBrokName)            
            #stockid = '8299'
            checkfile = "histock_rebuild_data/"+folder_twday+"/"+findBrokName+'_'+mainBrok+'_'+subBrok+'_'+twday+"_rebuid.csv"
            if mainBrok == '9800' and folder_twday=='20210303':
                mainBrok = '9800'
            res = True
            if Build_fubon_data_to_my_db.check_db_file_exist(checkfile) == False:
                res,htmldata = save_oridata_form_fubon(folder_twday,findBrokName,mainBrok,subBrok,twday)
                df1 = parser_major_data_to_csv_data(folder_twday,htmldata,findBrokName,mainBrok,subBrok,twday)
            else:
                df1 = pd.read_csv(checkfile,encoding='utf-8')
            
            res,htmldata = save_oridata_form_fubon(folder_twday,findBrokName,mainBrok,subBrok,twday)
            df1 = parser_major_data_to_csv_data(folder_twday,htmldata,findBrokName,mainBrok,subBrok,twday)
            if df1 is None:
                continue
            if DataFrameDb is None:
                DataFrameDb = Build_fubon_data_to_my_db.fubon_create_database(df1,findBrokName,dbname,twday,otc_rebuild_name,stockid)

            Build_fubon_data_to_my_db.trans_data_to_db(DataFrameDb,df1,findBrokName,stockid,twday,otc_rebuild_name)

            if res == False:
                log.log('downloaded from internet ' + mainBrok+ '-' +subBrok)
                #stime.sleep(1)
        except:
            DataFrameDb.to_csv(dbname,encoding='utf-8',index=0)
            log.log("exception"+','+folder_twday+','+checkfile+','+mainBrok +","+subBrok+","+twday)
    to1 = time.time() - to0
    log.log('test time'+str(to1))
    DataFrameDb.to_csv(dbname,encoding='utf-8',index=0)


    '''brokage_id_utf8 = a.encode("UTF-8")
    if pattern.fullmatch(df.代號[r][3]) is not None:
        print("Found match: " + df.代號[r])
    else:
        # if not found match
        print("No match")'''


#https://fubon-ebrokerdj.fbs.com.tw/z/zg/zgb/zgb0.djhtm?a=9800&b=0039003800310042
