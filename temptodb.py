import sqlite3
conn = sqlite3.connect('./sqllite3/brokder.db')
cursor = conn.cursor()
import pandas as pd


def checkdb(df):
    cnt = 0
    for idx in df.index:
        sql=f"select  * from broker_buy where mainBroker='{df['mainBroker'][idx]}'  LIMIT 1"
        try:
            cursor.execute(sql)
            data = cursor.fetchall()
            if len(data) == 0 :
                return 0
            else:
                return 1
            #conn.commit()
        except Exception as e:
            print(e)
            print(f"exception : '{df['stockid'][idx]}','{df['mainBroker'][idx]}','{df['subBroker'][idx]}','{df['date'][idx]}'")
        cnt = cnt+1
    conn.commit()
#insertdb(df)

def insertdb(df):
    cnt = 0
    for idx in df.index:
        sql=f"insert into broker_buy (brokerName,buy_tick,sell_tick,diff,stockid,mainBroker,subBroker,date) " \
        f"values('{df['券商名稱'][idx]}',{df['買進張數'][idx]},{df['賣出張數'][idx]},{df['差額'][idx]},'{df['stockid'][idx].replace('.0','').replace('nan','')}','{df['mainBroker'][idx]}','{df['subBroker'][idx]}','{df['date'][idx]}')"
        print(f"{cnt}/{len(df)}")
        try:
            conn.execute(sql)
            #conn.commit()
        except Exception as e:
            print(e)
            print(f"exception : '{df['stockid'][idx]}','{df['mainBroker'][idx]}','{df['subBroker'][idx]}','{df['date'][idx]}'")
        cnt = cnt+1
    conn.commit()
#insertdb(df)

import os
dir_path = r'./broker1/'

# list to store files
res = []

# Iterate directory
for path in os.listdir(dir_path):
    # check if current path is a file
    if os.path.isfile(os.path.join(dir_path, path)):
        if path.find('.csv') >=0:
            #res.append(path)
            df = pd.read_csv(f'./broker1/{path}',encoding='big5', warn_bad_lines=True, error_bad_lines=False,dtype=str)
            df['stockid'] = df['stockid'].astype(str)
            df = df.fillna('-')
            if checkdb(df):
                continue
            insertdb(df)
    #break
        