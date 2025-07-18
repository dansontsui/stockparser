import yfinance as yf
import json
import pandas as pd
import logging
import subprocess
#console_handler = logging.StreamHandler()
#logging.getLogger().addHandler(console_handler)
# 添加FileHandler来将日志写入文件
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
file_handler = logging.FileHandler('D:\\danson_tsui\\Documents\\mystock\\app.log')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logging.getLogger().addHandler(file_handler)

import requests
from pytz import timezone
def get00751bdivdata():
    dd = pd.read_html('https://www.moneydj.com/ETF/X/Basic/Basic0005.xdjhtm?etfid=00751B.TW')
    df = dd[1]
    df.rename(columns={'除息日': 'Date','配息總額':'Dividends'}, inplace=True)
    df['Date'] = pd.to_datetime(df['Date'], format='%Y/%m/%d',errors='coerce')
    return df.head(1)

def get00937bdivdata():
    url = 'https://www.capitalfund.com.tw/etf/product/detail/378/interest'
    response = requests.get(url)
    if response.status_code == 200:
        html_content = response.text
    else:
        print('Failed to retrieve the webpage. Status code:', response.status_code)
    from bs4 import BeautifulSoup
    import pandas as pd
    # 使用BeautifulSoup解析HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    # 找到表格的所有行
    rows = soup.find_all('div', class_='tr')
    data = []
    for row in rows:
        # 找到每行的所有列
        cols = row.find_all('div', class_='td')
        cols = [col.text for col in cols]
        for i in range(0,len(cols)):
            cols[i] = cols[i].replace('配息基準日','').replace('除息交易日','').replace('配息發放日','').replace('每單位分配金額(元)','').replace('除息日前一日之淨值','').replace('年化配息率	','').replace('配息頻率','')
        data.append(cols)
    # 將資料轉換為data frame
    df = pd.DataFrame(data, columns=['配息基準日', 'Date', '配息發放日', 'Dividends', '除息日前一日之淨值', '年化配息率', '配息頻率'])
    #print(df)
    df.dropna(axis=0,inplace=True)
    df['Date'] = pd.to_datetime(df['Date'], format='%Y/%m/%d',errors='coerce')
    #df = df.reset_index()
    return df.head(1)




def get_last_dividend(stock_code):

    #stock_code = f"00{s.index[0]}.TWO"
    #stock_code = "00878.TW"
    #print(stock_code)
    # 使用YFinance獲取數據
    sa = []
    dividends = yf.Ticker(stock_code).dividends
    logging.info(stock_code)
    logging.info(dividends)
    if len(dividends) == 0:
        return dividends
    # 打印獲取的數據

    df = pd.Series(dividends)
    df = df.reset_index()
    df['Date'] = pd.to_datetime(df['Date'].dt.strftime('%Y/%m/%d'))
    return df.tail(1)
    #return dividends.tail(1)

def cal_profit(df_dvihis,myLastDate,divdate,result,div,resid):
    if myLastDate < divdate:
        print('id',resid)
        print('id_count',result['count'][resid])
        print('div',div)
        print('intrest',float(div) * result['count'][resid]*1000)
        new_data = {'id': resid, 'update_date': divdate, 'div':div,'count':result['count'][resid],'Interest':float(div) * result['count'][resid]*1000}
        df_dvihis.loc[len(df_dvihis)] = new_data
        return 1
    return 0
def check_update_date_exist(div_dates,update_date):
    for d in div_dates:
        if d == update_date:
            return 1
    return 0

df = pd.read_csv('D:\\danson_tsui\\Documents\\mystock\\db.csv',index_col=None)   
df = df.reset_index(drop=True)
df['date'] = pd.to_datetime(df['date'])
df_dvihis = pd.read_csv('D:\\danson_tsui\\Documents\\mystock\\myhis1.csv',index_col='idx')
#df_dvihis = df_dvihis.reset_index(drop=True)
df_dvihis['update_date'] = pd.to_datetime(df_dvihis['update_date'])
v = df.index
s = v.value_counts()
result = df.groupby('id').agg({'count': 'sum', 'price': 'mean'})

openfile = 0
for id in result.index:
    stock_code = f"00{id}.TWO"
    resid = id
    logging.info(f"-------------{stock_code}-------------")
    #lastdiv = get_last_dividend (stock_code)
    lastdiv = get00751bdivdata()
    if id == '937B':
        lastdiv=get00937bdivdata()
    lastdiv = lastdiv.reset_index(drop='True')

    if len(lastdiv) == 0:
        logging.info('no data need update')
        break
    if lastdiv['Date'][0].year < 2023:
        logging.warning('warning data')
    # 使用條件選擇選取指定欄位內容為id的資料
    filtered_data = df[df['id'] == id]
    # 根據日期欄位排序資料，選擇最後一筆資料
    latest_data = filtered_data.sort_values('date').tail(1)
    myLastDate = latest_data['date'][latest_data.index[0]]
    #檢查該筆除權日期是否已經存在 如果存在就不用計算
    exist = check_update_date_exist(df_dvihis['update_date'],lastdiv['Date'][0])
    res = 0
    if exist == 0:
        #計算利息
        res = cal_profit(df_dvihis,myLastDate,lastdiv['Date'][0],result,lastdiv['Dividends'][lastdiv.index[0]],resid)
    if res :
        openfile = 1
        logging.info('update')
    else:
        logging.info('no data need update')

df_dvihis.to_csv('D:\\danson_tsui\\Documents\\mystock\\myhis1.csv')
if openfile:
    subprocess.run(['start', 'D:\\danson_tsui\\Documents\\mystock\\myhis1.csv'], shell=True)  # 打开文件

