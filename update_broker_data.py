import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import finlab.crawler as cr

headers = cr.generate_random_header()

session = requests.Session()
retry = Retry(connect=3, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)

#Mborkerid = '9800'
#subborkerid = '9800'
#datestr = '2022-08-12'
#r = requests.get(url,headers = headers)
print(" read data start")
#url = "https://www.twse.com.tw/brokerService/brokerServiceAudit?showType=list&stkNo=1020"
#url = "https://www.learncodewithmike.com/2021/05/pandas-and-sqlite.html"
url = "https://www.twse.com.tw/zh/brokerService/brokerServiceAudit"
r = session.get(url,headers = headers,verify=False)
try:
    df = pd.read_html(r.text)
except Exception as e:
    print(str(e))

import sqlite3
conn = sqlite3.connect('./sqllite3/brokder.db')
cursor = conn.cursor()

df[0].to_sql('broker_data_main', conn, if_exists='replace', index=False)    
df1=df[0]
for idx in df1.index:
    url = f"https://www.twse.com.tw/brokerService/brokerServiceAudit?showType=list&stkNo={df1['證券商代號'][idx]}"
#url = "https://www.learncodewithmike.com/2021/05/pandas-and-sqlite.html"
#url = "https://www.twse.com.tw/zh/brokerService/brokerServiceAudit"
    r = session.get(url,headers = headers,verify=False)
    try:
        cursor.execute(f"delete from broker_data_detail where mainid='{df1['證券商代號'][idx]}'")
        df = pd.read_html(r.text)
        df = df[3]
        df['mainid'] = df1['證券商代號'][idx]
        df.to_sql('broker_data_detail', conn, if_exists='append', index=False)
    except Exception as e:
        print(str(e))
