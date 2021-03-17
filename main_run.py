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

#http://fubon-ebrokerdj.fbs.com.tw/z/zc/zco/zco0/zco0.djhtm?a=8299&BHID=9800&b=9800
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

    major_file_name = "major_ori_data\\major_hisstock_"+stockid+".html"
    f = open(major_file_name, mode='r', encoding='utf-8')
    fs = f.read()
    f.close()
    #res = requests.get(url) # your link here
    soup = bs4.BeautifulSoup(fs)
    my_list = [i.string.lstrip('q("talkPage.init", ').rstrip(')') for i in soup.select('script') if i.string and i.string.startswith('q')]

    # my_list should now be filled with all the json text that is from a <script> tag followed by a 'q'
    # note that I lstrip and rstrip on the script based no your sample (assuming there's a closing bracket), but if the convention is different you'll need to update that accordingly.

    #...#
    my_jsons = []
    for json_string in my_list:
        my_jsons.append(json.loads(json_string))

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
    major_file_name = "major_ori_data\\major_hisstock_"+sotckid+".html"
    f = open(major_file_name, mode='w', encoding='utf-8')
    f.write(r.text)
    f.close()
    

def startParser(sotckid):
    #load data form internet
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
    startParser('8299')
    