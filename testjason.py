import requests
from io import StringIO
import pandas as pd
import os 
import sys 
from bs4 import BeautifulSoup 
import datetime
import re
import major_data
import create_db
import get_sotck_price


def craete_history(sotckid,filedate):
    #load data form internet
    
    major_file_name = "major_ori_data\\major_"+sotckid+"_"+filedate+".html"
    if os.path.isfile(major_file_name):
        print("檔案存在。")
    else:
        print("檔案不存在。")
        return False

    f = open(major_file_name, mode='r', encoding='utf-8')
    fs = f.read()
    f.close()
    s = re.findall(r"資料日期\S+.+",fs)
    s1 = re.search(r"\d+\s+/\d+ /\d+",s[0])
    s2 = s1.group()
    s2 = re.split(r" /",s2)
    filedate = s2[0]+s2[1]+s2[2] 


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
    #check db and crate db
    create_db.create_data_base(dataFrame,filedate,sotckid)
    #write data
    dataFrame.to_csv("major_csv_data\\"+sotckid+"_"+filedate+'.csv', encoding='utf-8',index=0) 
    #add to dababase
    major_data.collectdata("major_csv_data\\"+sotckid+"_"+filedate+'.csv',filedate,sotckid)


def test_jason_from_histock_file(stockid):

    major_file_name = "histock_original_data\\major_hisstock_"+stockid+".html"

    soup = BeautifulSoup(open(major_file_name,encoding="utf-8"), "html.parser")
    b_tag= soup.find_all("div", class_="row-stock pl10")
    b_tag1= soup.find_all("input",class_="inputDay")
    s = b_tag1[0]
    a = str(s)
    sdate = re.search(r'value=\S+"',a).group().replace('value','').replace('/','').replace('=','').replace('"','')


    f = open(major_file_name, mode='r', encoding='utf-8')
    fs = f.read()
    f.close()
    s = fs.find('"Buy":')
    s1 = fs[s:].find(']')
    newstring=fs[s:s+s1+1]
    newstring =  newstring.replace('"Buy":','')
    newstring = newstring.replace('\n','')
    f1 = open("histock_original_data\\testjason_buy.txt",mode='w',encoding='utf-8')
    f1.write(newstring)
    f1.close()
    df = pd.read_json(newstring)


    s = fs.find('"Sell":')
    s1 = fs[s:].find(']')
    newstring=fs[s:s+s1+1]
    newstring =  newstring.replace('"Sell":','')
    newstring = newstring.replace('\n','')
    f1 = open("histock_original_data\\testjason_sell.txt",mode='w',encoding='utf-8')
    f1.write(newstring)
    f1.close()
    df1 = pd.read_json(newstring)
    df = df.append(df1,ignore_index=True)
    df.to_csv("histock_rebuild_data\\"+stockid+"_major.csv", encoding='utf-8',index=0) #update db

   

def startParser_form_histock(sotckid):
    #load data form internet
    r = requests.get('https://histock.tw/stock/branch.aspx?no=8299')
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
    major_file_name = "histock_original_data\\major_hisstock_"+sotckid+".html"
    f = open(major_file_name, mode='w', encoding='utf-8')
    f.write(r.text)
    f.close()
    

def startParser(sotckid):
    #load data form internet
    print("startParser")
    r = requests.get('https://tw.stock.yahoo.com/d/s/major_8299.html')
    #parser html date
    s = re.findall(r"資料日期\S+.+",r.text)
    s1 = re.search(r"\d+\s+/\d+ /\d+",s[0])
    s2 = s1.group()
    s2 = re.split(r" /",s2)
    filedate = s2[0]+s2[1]+s2[2] 
    #download otc all stock data
    get_sotck_price.downloadOTC(s2[0]+"/"+s2[1]+"/"+s2[2])
    major_file_name = "major_ori_data\\major_"+sotckid+"_"+filedate+".html"
    f = open(major_file_name, mode='w', encoding='utf-8')
    #save original data
    f.write(r.text)
    f.close()
    #load html data
    soup = BeautifulSoup(open(major_file_name,encoding="utf-8"), "html.parser")
    list_header = [] 
    data = [] 
    #soup = BeautifulSoup(open("major.html",encoding="utf-8"), "html.parser")
    #資料放在html的第三組table tag
    header = soup.find_all("table")[3].find("tr")
    for items in header: 
        try: 
            #先parser欄位,把他變成dataFrame的column
            list_header.append(items.get_text()) 
        except: 
            continue
    HTML_data = soup.find_all("table")[3].find_all("tr")[1:]
    for element in HTML_data: 
        sub_data = [] 
        for sub_element in element: 
            try: 
                #再parser資料,把他變成dataFrame的data
                sub_data.append(sub_element.get_text()) 
            except: 
                continue
        data.append(sub_data) 
    #create dataFrame,指定dataframe的data and columns
    dataFrame = pd.DataFrame(data = data, columns = list_header)
    #check db and crate db
    create_db.create_data_base(dataFrame,filedate,sotckid)
    #write data
    dataFrame.to_csv("major_csv_data\\"+sotckid+"_"+filedate+'.csv', encoding='utf-8',index=0) 
    #add to dababase
    major_data.collectdata("major_csv_data\\"+sotckid+"_"+filedate+'.csv',filedate,sotckid)

    
if __name__ == '__main__':
    #startParser_forhistock('8299')    
    test_jason_from_histock_file('8299')
    
