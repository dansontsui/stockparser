import requests
from io import StringIO
import pandas as pd
import os 
import sys 
from bs4 import BeautifulSoup 
import datetime
import re
import major_data



def startParser(sotckid):
    #load data form internet
    r = requests.get('https://tw.stock.yahoo.com/d/s/major_8299.html')
    #parser html date
    s = re.findall(r"資料日期\S+.+",r.text)
    s1 = re.search(r"\d+\s+/\d+ /\d+",s[0])
    s2 = s1.group()
    s2 = re.split(r" /",s2)
    filedate = s2[0]+s2[1]+s2[2] 
    major_file_name = "major_"+sotckid+"_"+filedate+".html"
    f = open(major_file_name, mode='w', encoding='utf-8')
    f.write(r.text)
    f.close()
    #f = open(major_file_name, mode='r', encoding='utf-8')
    #fs = f.read()
    #soup = BeautifulSoup(open(fs),'html.parser')
    soup = BeautifulSoup(open(major_file_name,encoding="utf-8"), "html.parser")
    list_header = [] 
    data = [] 
    #soup = BeautifulSoup(open("major.html",encoding="utf-8"), "html.parser")
    #資料放在html的第三組table tag
    header = soup.find_all("table")[3].find("tr")
    for items in header: 
        try: 
            #先parser 欄位 變成dataFrame的column
            list_header.append(items.get_text()) 
        except: 
            continue
    HTML_data = soup.find_all("table")[3].find_all("tr")[1:]
    for element in HTML_data: 
        sub_data = [] 
        for sub_element in element: 
            try: 
                #再parser 資料 變成dataFrame的data
                sub_data.append(sub_element.get_text()) 
            except: 
                continue
        data.append(sub_data) 
    #create dataFrame
    dataFrame = pd.DataFrame(data = data, columns = list_header)
    #write data
    dataFrame.to_csv(sotckid+"_"+filedate+'.csv', encoding='utf-8',index=0) 
    #add to dababase
    major_data.collectdata(sotckid+"_"+filedate+'.csv',filedate,sotckid)
if __name__ == '__main__':
    startParser('8299')
    