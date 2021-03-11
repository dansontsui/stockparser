import requests
import json
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup 
import csv
import re
import datetime as dt

def parser_major_data_to_csv_data(filename,sdate):
    soup = BeautifulSoup(open(filename,encoding="utf-8"), "html.parser")
    #header = soup.find_all("table")[3].find("tr")[1:]
    #header = soup.find_all("td",{"class":"t2"})
    #header = soup.find_all("table",{"class":"t0"}).find('tr')

    columns1 =[]
    '''
    for a in soup.find_all('td', {'class': 't4t1'}):
        s = a.find('script')
        if s == None:
            s1=(a.text.replace('\n',''))
            columns.append(s1)
        else:
            stocks=(str(s.contents).replace('\n','').replace('\\n','').replace('\\tGenLink2stk','')
            .replace('<!--(','').replace(');//-->','').replace('\'','').replace('"','').replace('[','').replace(']',''))
            s1 = stocks.replace(',')
            columns.append(s1)
    '''
    #columns = [th.text.replace('\n', '') for th in soup.find_all('td', {'class': 't4t1'})]



    a = soup.find_all('td', {'class': 't4t1'})
    b = soup.find_all('td', {'class': 't3n1'})
    #soup = BeautifulSoup(data)
    #script = soup.find_all('script')
    #for jj in script:
    #    print(jj.text)

    table = soup.find_all('table', {'class': 't0'})
    #for tableindex in range(0,2):
    aa = table[0].find_all('tr')
    sartrecordcoulumnName = 0
    for tt in aa:
        aa1 = tt.find_all('td')
        print(aa1[0].text)
        if aa1[0].text == '買超':
            sartrecordcoulumnName = 1
            continue
        if sartrecordcoulumnName:
            for i in range(0,4):
                print(aa1[i].text)
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
                    print(s1)
                    data.append(s1)
                else:
                    #data.append(c.text)
                    stocks1=str(c.contents[1])
                    stocks1 = re.search(r'\(\S+\)',stocks1).group()
                    stocks1 = stocks1.replace('(','').replace('\'','').replace(')','').replace(',','')
                    print(stocks1)
                    data.append(stocks1)
                if len(data) == 4:
                    dataarr.append(data.copy())
                    data.clear()

    dataFrame = pd.DataFrame(data = dataarr, columns = columns1)
    dataFrame.to_csv("histock_rebuild_data\\"+sdate+"_rebuid.csv",encoding='utf-8',index=0)
    print(dataFrame.head())

def save_oridata_form_fubon(sotckid,sdate):
    #load data form internet
    r = requests.get('https://fubon-ebrokerdj.fbs.com.tw/z/zg/zgb/zgb0.djhtm?a=9800&b=9813&c=E&e='+sdate+'&f='+sdate)
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
    major_file_name = 'histock_original_data\major_fubon_'+sdate+'.html'
    f = open(major_file_name, mode='w', encoding='utf-8')
    f.write(r.text)
    f.close()
    return major_file_name

downloadDate= dt.date.today()
year  = downloadDate.year
month = downloadDate.month
day   = downloadDate.day-1
twday = '{}-{:1}-{:1}'.format(year,month,day)


#https://fubon-ebrokerdj.fbs.com.tw/z/zg/zgb/zgb0.djhtm?a=9800&b=9813&c=E&e=2021-3-9&f=2021-3-9
filename = save_oridata_form_fubon('8299',twday)
parser_major_data_to_csv_data(filename,twday)
#https://fubon-ebrokerdj.fbs.com.tw/z/zg/zgb/zgb0.djhtm?a=9800&b=0039003800310042
