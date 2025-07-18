import requests
import os
import random
import time
from io import StringIO
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
# 设置多个User-Agent
user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1'
]


def crawl_stock_data(stock_code, start_date, end_date):

    if not os.path.exists(stock_code):
        os.makedirs(stock_code)

    current_date = start_date
    while current_date <= end_date:
        # 计算下个月的第一天
        next_month = current_date.replace(day=28) + timedelta(days=4)
        next_month = next_month.replace(day=1)

        # 构建请求URL
        url = f'https://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&date={current_date.strftime("%Y%m%d")}&stockNo={stock_code}'
        # 随机选择一个User-Agent
        headers = {
            'User-Agent': random.choice(user_agents)
        }

        # 初始化重试计数器
        retries = 0

        while retries < 2:
            time.sleep(random.uniform(5, 10))  # 延迟5到10秒
            try:
                # 发送请求
                response = requests.get(url, headers=headers)
                response.raise_for_status()  # 如果响应状态码不是200，抛出异常
            except requests.exceptions.RequestException as e:
                print(f'Failed to retrieve data for {current_date.strftime("%Y-%m")}. Retrying...')
                retries += 1
                time.sleep(5)  # 等待5秒后重试

                headers = {
                    'User-Agent': random.choice(user_agents)
                }

                if retries == 2:
                    print(f'Failed to retrieve data for {current_date.strftime("%Y-%m")} after 2 retries. Skipping to next month.')
                    break
            else:
                # 解析JSON数据
                data = response.json()

                # 提取数据
                df = pd.DataFrame(data['data'], columns=data['fields'])

                # 保存数据到本地文件
                file_name = f'{stock_code}_{current_date.strftime("%Y%m")}.csv'
                file_path = os.path.join(stock_code, file_name)
                df.to_csv(file_path, index=False)

                print(f'Saved data for {current_date.strftime("%Y-%m")} to {file_path}')
                break  # 成功获取数据，跳出重试循环
        # 更新日期到下个月
        current_date = next_month

#取的某天上市股價
def get_stk_twse_info(datestr):
    # 下載股價
    str = 'https://www.twse.com.tw/exchangeReport/MI_INDEX?response=csv&date=' + datestr + '&type=ALL'
    r = requests.post('https://www.twse.com.tw/exchangeReport/MI_INDEX?response=csv&date=' + datestr + '&type=ALL')
    # 整理資料，變成表格
    df = pd.read_csv(StringIO(r.text.replace("=", "")), 
                header=["證券代號" in l for l in r.text.split("\n")].index(True)-1)
                
    df.drop(columns=df.columns[df.columns.str.contains('Unnamed')], inplace=True)
    df.dropna(how='all', inplace=True)
    df.dropna(subset=['證券名稱'], how='all', inplace=True)
    df.rename(columns={'證券代號': '代號'}, inplace=True)
    df.rename(columns={'收盤價': '收盤'}, inplace=True)
    return df


#取的某天OTC股價
def get_stk_otc_info(datestr):
    print(datestr)
    url = f"https://www.tpex.org.tw/www/zh-tw/afterTrading/otc?date={datestr}&type=AL&id=&response=csv"
    response = requests.post(url)
    filestr = datestr.replace('/','_')
    with open(f"otc_data_{filestr}.csv", 'w', encoding='utf-8') as f:
        f.write(response.text)
    lines = response.text.splitlines()
    data =''
    # 假設我們想要找到長度小於20的行，並且連續讀取N行
    N = 5  # 這裡假設N為5，你可以根據需要更改
    count = 0
    find = 0
    for line in lines:
        if len(line) > 20:
            find =1
            count += 1
            #print(line)
            data += line + '\n'
        elif find == 1:
            break
    df = pd.read_csv(StringIO(data))
    df.columns = df.columns.str.replace(' ', '')
    return df
# 假設今天是2025/01/01，你可以根據實際情況更改
def aaa():
    today = datetime(2025, 1, 1)
    # 計算昨天的日期
    yesterday = today - timedelta(days=1)
    # 格式化日期為所需的字符串格式
    formatted_date = yesterday.strftime('%Y/%m/%d')
    return formatted_date
today = datetime.today()
print('load stk function')
