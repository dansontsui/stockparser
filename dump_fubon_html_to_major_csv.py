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

def parser_major_data_to_csv_data(folder_twday,filename,findBrokName,mainid,subid,sdate):
    soup = BeautifulSoup(open(filename,encoding="utf-8"), "html.parser")
    #header = soup.find_all("table")[3].find("tr")[1:]
    #header = soup.find_all("td",{"class":"t2"})
    #header = soup.find_all("table",{"class":"t0"}).find('tr')

    columns1 =[]
    table = soup.find_all('table', {'class': 't0'})
    #for tableindex in range(0,2):
    aa = table[0].find_all('tr')
    sartrecordcoulumnName = 0
    for tt in aa:
        aa1 = tt.find_all('td')
        #print(aa1[0].text)
        if aa1[0].text == '買超':
            sartrecordcoulumnName = 1
            continue
        if sartrecordcoulumnName:
            for i in range(0,4):
                #print(aa1[i].text)
                columns1.append(aa1[i].text)
            sartrecordcoulumnName = 0

    data = []
    dataarr = []
    for tdx in range(0,2):
        b = table[tdx].find_all('tr')
        for b in table[tdx].find_all('tr'):
            for c in b.find_all('td'):
                if c.text in columns1 or (c.text=='買超' or c.text=='賣超'):
                    continue
                s = c.find('script')
                if s == None :
                    s1=(c.text.replace('\n',''))
                    #print(s1)
                    data.append(s1)
                else:
                    stocks1=str(c.contents[1])
                    stocks1 = re.search(r'\(\S+\)',stocks1).group()
                    stocks1 = stocks1.replace('(','').replace('\'','').replace(')','').replace(',','')
                    #print(stocks1)
                    data.append(stocks1)
                if len(data) == 4:
                    dataarr.append(data.copy())
                    data.clear()

    dataFrame = pd.DataFrame(data = dataarr, columns = columns1)
    dataFrame.to_csv("histock_rebuild_data/"+folder_twday+"/"+findBrokName+'_'+mainid+'_'+subid+'_'+sdate+"_rebuid.csv",encoding='utf-8',index=0)
    print(dataFrame.head())

def save_oridata_form_fubon(folder_twday,findBrokName,mainid,subid,sdate):
    #load data form internet
    headers = {
        'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36',
        'Cookie':'gr_user_id=1f9ea7ea-462a-4a6f-9d55-156631fc6d45; bid=vPYpmmD30-k; ll="118282"; ue="codin; __utmz=30149280.1499577720.27.14.utmcsr=douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/doulist/240962/; __utmv=30149280.3049; _vwo_uuid_v2=F04099A9dd; viewed="27607246_26356432"; ap=1; ps=y; push_noty_num=0; push_doumail_num=0; dbcl2="30496987:gZxPfTZW4y0"; ck=13ey; _pk_ref.100001.8cb4=%5B%22%22%2C%22%22%2C1515153574%2C%22https%3A%2F%2Fbook.douban.com%2Fmine%22%5D; __utma=30149280.833870293.1473539740.1514800523.1515153574.50; __utmc=30149280; _pk_id.100001.8cb4=255d8377ad92c57e.1473520329.20.1515153606.1514628010.'
    }

    url = 'https://fubon-ebrokerdj.fbs.com.tw/z/zg/zgb/zgb0.djhtm?a='+mainid+'&b='+subid+'&c=E&e='+sdate+'&f='+sdate
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
    major_file_name = 'histock_original_data/'+folder_twday+"/"+findBrokName+'_'+mainid+'_'+subid+'_major_fubon_'+sdate+'.html'
    f = open(major_file_name, mode='w', encoding='utf-8')
    f.write(r.text)
    f.close()
    return major_file_name

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



pattern = re.compile("[A-Za-z]+")

# if found match (entire string matches pattern)
#a = str(df.代號[r])
for dc in range(4,0,-1):
    to0 = time.time()

    day   = downloadDate.day-dc
    twday = '{}-{:1}-{:1}'.format(year,month,day)
    folder_twday= '{}{:02}{:02}'.format(year,month,day)
    #folder_twday = "2021-03-14"

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
    for r in range(0,row):
        if df.代號[r][3]=='0':
            mainBrok = df.代號[r]
            subBrok = df.代號[r]
            findBrokName = mainBrokName = df.證券商名稱[r]
            log.log('...main-id:'+mainBrok+'-'+subBrok)
        elif df.證券商名稱[r].find(mainBrokName) >=0:
            subBrok = df.代號[r]
            findBrokName = df.證券商名稱[r]
            brokage_id_utf8 = subBrok.encode("UTF-8")
            if pattern.fullmatch(df.代號[r][3]) is not None:
                subBrok = '00'+str(hex(brokage_id_utf8[0]))+'00'+str(hex(brokage_id_utf8[1]))+'00'+str(hex(brokage_id_utf8[2]))+'00'+str(hex(brokage_id_utf8[3]))
                subBrok =subBrok.replace('0x','')
                log.log(subBrok)
            else:
                log.log('.....sub-id:'+subBrok)
        try:            
            log.log('.....name  :'+findBrokName)            
            time.sleep(1)
            filename = save_oridata_form_fubon(folder_twday,findBrokName,mainBrok,subBrok,twday)
            parser_major_data_to_csv_data(folder_twday,filename,findBrokName,mainBrok,subBrok,twday)
        except:
            log.log("exception"+','+folder_twday+','+filename+','+mainBrok +","+subBrok+","+twday)
    to1 = time.time() - to0
    #print("get time = " + str(to1))
    log.log('get time'+str(to1))
    log.log(str(to1))
    Build_fubon_data_to_my_db.run_parser(folder_twday)



    '''brokage_id_utf8 = a.encode("UTF-8")
    if pattern.fullmatch(df.代號[r][3]) is not None:
        print("Found match: " + df.代號[r])
    else:
        # if not found match
        print("No match")'''


#https://fubon-ebrokerdj.fbs.com.tw/z/zg/zgb/zgb0.djhtm?a=9800&b=0039003800310042
