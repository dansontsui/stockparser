import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import numpy as np
from datetime import datetime
import time
import gc
from datetime import date, timedelta


import warnings
warnings.filterwarnings("ignore")
import finlab.crawler as cr


import sqlite3
conn = sqlite3.connect('./sqllite3/brokder.db')
cursor = conn.cursor()


import logging

logger = logging.getLogger('Log.Parser1')
logger.setLevel(logging.DEBUG)
#formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s',datefmt='%m-%d %H:%M:%S')
formatter = logging.Formatter('%(asctime)s - %(message)s',datefmt='%m-%d %H:%M:%S')
fh1 = logging.FileHandler(filename="collect_broker_data_todb_1.py.log", mode='a')
console = logging.StreamHandler()
console.setFormatter(formatter)
console.setLevel(logging.INFO)
fh1.setLevel(logging.DEBUG)
fh1.setFormatter(formatter)
logger.addHandler(console)
logger.addHandler(fh1)


def checkdb(main,sub):
    sql=f"select  * from broker_buy where mainBroker='{main}' and subbroker='{sub}' order by date"
    try:
        s_df = pd.read_sql(sql, conn)
        return s_df
        #conn.commit()
    except Exception as e:
        print(e)



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

def fixdatastring_from_web(dfa):
    for idx in dfa.index:
        str1 = dfa['券商名稱'][idx]
        ss = str1.replace('<!-- \tGenLink2stk','').replace("('","").replace("'","").replace("); //-->","").replace("AS","")
        d = ss.split(',')
        if len(d) == 2:
            dfa['stockid'][idx]=str(d[0])
            dfa['券商名稱'][idx]=d[1]
        else:
            dfa['券商名稱'][idx]=d[0]


    dfa = dfa[dfa['券商名稱'].isnull() == False]
    dfa = dfa[dfa['券商名稱']!='無此券商分點交易資料' ]

    dfa.reset_index(inplace= True,drop=True)
    dfa['買進張數'] = dfa['買進張數'].astype(int)
    dfa['差額'] = dfa['差額'].astype(int)
    dfa['賣出張數'] = dfa['賣出張數'].astype(int)

    return dfa

def MakeBroidData():

    sql = f"select * from broker_data_main"
    #df = pd.read_csv('broker_id1.csv',encoding='big5')
    df = pd.read_sql(sql,conn)
    '''
    df=pd.read_csv('broker_id.csv',encoding='utf-8',sep='\\s+')
    df['subBroderId'] = ''
    df['MainBroder'] = 'N'

    for bdidx in df.index:
        s1 = df['證券商名稱'][bdidx].split('-')
        if len(s1) == 2:
            df['證券商名稱'][bdidx]=s1[0]
            df['subBroderId'][bdidx]=s1[1]
        else:
            df['MainBroder'][bdidx] = 'Y'
            df['subBroderId'][bdidx]=s1[0]
    '''
    return df


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)

def loadBrokerPikle(Mborkerid):
    try:
        fullsell = pd.read_pickle(f'.\\broker1\\broker_sell_{Mborkerid}.pkl')
    except Exception as e:
        fullsell = None

    try:
        fullbuy = pd.read_pickle(f'.\\broker1\\broker_buy_{Mborkerid}.pkl')
    except Exception as e:
        fullbuy = None


    return fullbuy,fullsell

import os






def saveBrokerPikle(fullbuy,fullsell,Mborkerid):
    try:
        if os.path.isfile(f'.\\broker1\\broker_sell_{Mborkerid}.pkl'):
            fs = pd.read_pickle(f'.\\broker1\\broker_sell_{Mborkerid}.pkl')
            fb = pd.read_pickle(f'.\\broker1\\broker_buy_{Mborkerid}.pkl')
            fb = fb.append(fullbuy)
            fs = fs.append(fullsell)
            fb=fb.sort_index()
            fs=fs.sort_index()
            fb.to_pickle(f'.\\broker1\\broker_buy_{Mborkerid}.pkl')
            fs.to_pickle(f'.\\broker1\\broker_sell_{Mborkerid}.pkl')
        else:
            fullbuy.to_pickle(f'.\\broker1\\broker_buy_{Mborkerid}.pkl')
            fullsell.to_pickle(f'.\\broker1\\broker_sell_{Mborkerid}.pkl')


    except Exception as e:
        fullbuy = None
        fullsell = None
    return fullbuy,fullsell


def loadBrokerCsv(Mborkerid):
    try:
        fullsell = fs = pd.read_csv(f'.\\broker1\\broker_sell_{Mborkerid}.csv',encoding='big5', warn_bad_lines=True, error_bad_lines=False,dtype=str)
    except Exception as e:
        fullsell = None

    try:
        fullbuy = pd.read_csv(f'.\\broker1\\broker_buy_{Mborkerid}.csv',encoding='big5', warn_bad_lines=True, error_bad_lines=False,dtype=str)
    except Exception as e:
        fullbuy = None


    return fullbuy,fullsell

def saveBrokerCsv(fullbuy,fullsell,Mborkerid):
    try:
        if os.path.isfile(f'.\\broker1\\broker_sell_{Mborkerid}.csv'):
            fs = pd.read_csv(f'.\\broker1\\broker_sell_{Mborkerid}.csv',encoding='big5', warn_bad_lines=True, error_bad_lines=False)
            fb = pd.read_csv(f'.\\broker1\\broker_buy_{Mborkerid}.csv',encoding='big5', warn_bad_lines=True, error_bad_lines=False)
            fb['date'] = pd.to_datetime(fb['date']).dt.date
            fs['date'] = pd.to_datetime(fs['date']).dt.date
            #fs.set_index('date',inplace=True)
            #fb.set_index('date',inplace=True)
            fb = fb.append(fullbuy)
            fs = fs.append(fullsell)
            fs.reset_index(drop=True)
            fb.reset_index(drop=True)
            fb=fb.sort_index()
            fs=fs.sort_index()
            fb.to_csv(f'.\\broker1\\broker_buy_{Mborkerid}.csv',index=False,encoding='big5',errors='ignore')
            fs.to_csv(f'.\\broker1\\broker_sell_{Mborkerid}.csv',index=False,encoding='big5',errors='ignore')
        else:
            fullbuy.to_csv(f'.\\broker1\\broker_buy_{Mborkerid}.csv',index=False,encoding='big5',errors='ignore')
            fullsell.to_csv(f'.\\broker1\\broker_sell_{Mborkerid}.csv',index=False,encoding='big5',errors='ignore')


    except Exception as e:
        fullbuy = None
        fullsell = None
    return fullbuy,fullsell    


#fullbuy,fullsell= loadBrokerPikle()
'''
s = fullsell['date']
s = s.dropna()
start_date = max(s)
start_date  = start_date + timedelta(days=1)

start_date = date(2022, 3, 1)
end_date = datetime.now().date()
'''


borkerdf=MakeBroidData()

Mborkerdfidx = borkerdf

totalcnt = len(borkerdf)
startcnt = 0
#find
#Mborkerdfidx = Mborkerdfidx[Mborkerdfidx['代號'] == '9800']
logger.info(f"STRAT-{ datetime.now().date()}")
for Mborkeridx in Mborkerdfidx.index:
    fullbuy = None
    fullsell = None
    gc.collect()
    Mborkerid = Mborkerdfidx['證券商代號'][Mborkeridx]


    #subBrokerid = borkerdf[borkerdf['證券商名稱'] ==  Mborkerdfidx['證券商名稱'][Mborkeridx]]
    sql = f"select * from broker_data_detail where mainid = '{Mborkerid}'"
    subBrokerid = pd.read_sql(sql,conn)

    list = [Mborkerid, Mborkerid, "", "","",""]
    subBrokerid.loc[len(subBrokerid)] = list

    #fullbuy,fullsell= loadBrokerPikle(Mborkerid)
    #fullbuy,fullsell= loadBrokerCsv(Mborkerid)
    
    for subbrokerIdidx in subBrokerid.index:
        #if subBrokerid['subBroderId'][subbrokerIdidx] == subBrokerid['證券商名稱'][subbrokerIdidx]:
        #    subborkerid = Mborkerid
        #else:
        Mborkerid =subBrokerid['mainid'][subbrokerIdidx]
        subborkerid = subBrokerid['證券商代號'][subbrokerIdidx]
        log = f"get {Mborkerid} - {subborkerid} "            
        
        if subborkerid == '查無資料':
            #print(borkerdf['代號'] + 'is N')
            logger.warning(f"{Mborkerid}-{subborkerid}")
            continue            
        #fst = os.path.isfile(f'.\\broker1\\broker_sell_{Mborkerid}.csv')
        #fbt = os.path.isfile(f'.\\broker1\\broker_buy_{Mborkerid}.csv')
        #if (isinstance(fullbuy,pd.DataFrame) == False and fbt==True) or (isinstance(fullsell,pd.DataFrame) == False and fst==True) :
        #    print('make Error N')
        #    borkerdf['valid'][subbrokerIdidx] = 'N'
        #    borkerdf.to_csv('broker_id.csv',index=False,encoding='big5',errors='ignore')
        #    continue
        logger.info(log)
        df = checkdb(Mborkerid,subborkerid)

        if len(df) > 0:
            #df = pd.DataFrame(data)
            s = pd.to_datetime(df['date']).dt.date
            start_date = max(s)
            start_date  = start_date + timedelta(days=1)
        else:
            start_date = date(2022, 3, 1)

        end_date = datetime.now().date()
        #end_date =date(2022, 3, 5)
        #log = f"get {Mborkerid} - {subborkerid} "
        startcnt +=1
        fullbuy_t = None
        fullsell_t = None
        gc.collect()
        #print(log)
        session = requests.Session()
        retry = Retry(connect=3, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)        
        for single_date in daterange(start_date, end_date):

            time.sleep(0.3)
            datestr = single_date.strftime("%Y-%m-%d")
            #end='\r'
            log = f">>> {datestr} - {str(startcnt)}/{str(totalcnt)} - {Mborkerid}-{subborkerid}"
            print(log,end='\r')
            #datestr = "2023-2-1"

            
            #Mborkerid = '9800'
            #subborkerid = '9800'
            #datestr = '2022-08-12'
            #r = requests.get(url,headers = headers)
            
            headers = cr.generate_random_header()
            #print(log+" read data start")
            url = f'https://fubon-ebrokerdj.fbs.com.tw/z/zg/zgb/zgb0.djhtm?a={Mborkerid}&b={subborkerid}&c=E&e={datestr}&f={datestr}'
            r = session.get(url,headers = headers,verify= False)
            try:
                df = pd.read_html(r.text)
            except Exception as e:
                logger.warning(str(e))
                continue
            #print(log+" read data")
            dfbuy = pd.DataFrame(df[3])
            dfbuy.drop(index=0,axis=0,inplace=True)
            dfbuy.rename(columns={0:dfbuy[0][1],1:dfbuy[1][1],2:dfbuy[2][1],3:dfbuy[3][1]},inplace=True)
            dfbuy.drop(index=1,axis=0,inplace=True)
            dfbuy.reset_index(drop=True,inplace=True)
            dfbuy['stockid']=''
            dfbuy['mainBroker'] = Mborkerid
            dfbuy['subBroker'] = subborkerid
            dfbuy['date'] = datestr #datetime.strptime(datestr,'%Y-%m-%d').date()

            dfsell = pd.DataFrame(df[4])
            dfsell.drop(index=0,axis=0,inplace=True)
            dfsell.rename(columns={0:dfsell[0][1],1:dfsell[1][1],2:dfsell[2][1],3:dfsell[3][1]},inplace=True)
            dfsell.drop(index=1,axis=0,inplace=True)
            dfsell.reset_index(drop=True,inplace=True)
            dfsell['stockid']=''
            dfsell['mainBroker'] = Mborkerid
            dfsell['subBroker'] = subborkerid
            dfsell['date'] = datestr #datetime.strptime(datestr,'%Y-%m-%d').date()

            dfsell = fixdatastring_from_web(dfsell)
            dfbuy = fixdatastring_from_web(dfbuy)
            #print(log+" end")
            #dfbuy = dfbuy.set_index('date')
            #dfsell = dfsell.set_index('date')



            if isinstance(fullbuy_t,pd.DataFrame) == False:
                fullbuy_t = pd.DataFrame(columns=dfbuy.columns,index=dfbuy.index)
                fullbuy_t=fullbuy_t.dropna()
                fullsell_t = pd.DataFrame(columns=dfbuy.columns,index=dfbuy.index)
                fullsell_t=fullsell_t.dropna()
            if len(dfbuy) > 0:
                fullbuy_t = fullbuy_t.append(dfbuy)
            else:
                test=1
            if len(dfsell) > 0:
                fullsell_t = fullsell_t.append(dfsell)
            
        
        if isinstance(fullbuy_t,pd.DataFrame) == False:
            continue
        fullbuy_t = fullbuy_t.reset_index(drop=True)
        fullsell_t = fullsell_t.reset_index(drop=True)
        
        if len(fullbuy_t) > 0 or len(fullsell_t) > 0:
            #borkerdf['valid'][subbrokerIdidx] = 'Y'
            #borkerdf.to_csv('broker_id1.csv',index=False,encoding='big5',errors='ignore')
            #saveBrokerPikle(fullbuy_t,fullsell_t,Mborkerid)
            #saveBrokerCsv(fullbuy_t,fullsell_t,Mborkerid)
            fullbuy_t.rename(columns = {'券商名稱':'brokerName','買進張數':'buy_tick','賣出張數':'sell_tick','差額':'diff'}, inplace = True)
            fullsell_t.rename(columns = {'券商名稱':'brokerName','買進張數':'buy_tick','賣出張數':'sell_tick','差額':'diff'}, inplace = True)
            try:
                fullbuy_t.to_sql('broker_buy', conn, if_exists='append', index=False) 
                fullsell_t.to_sql('broker_buy', conn, if_exists='append', index=False) 
                conn.commit()
            except:
                continue
            #insertdb(fullbuy_t)
            #insertdb(fullsell_t)
        else:
            #print('make N')
            logger.debug(f"{Mborkerid}-{subborkerid} - make N")
            #borkerdf['valid'][subbrokerIdidx] = 'N'
            #borkerdf.to_csv('broker_id1.csv',index=False,encoding='big5',errors='ignore')
        #fullbuy,fullsell= loadBrokerPikle(Mborkerid)
        #if isinstance(fullbuy,pd.DataFrame) == False:
        #    print('error')
        #if isinstance(fullsell,pd.DataFrame) == False:
        #    print('error')            
        #fullbuy.to_pickle(f'.\\broker1\\broker_buy_{Mborkerid}.pkl')
        #fullsell.to_pickle(f'.\\broker1\\broker_sell_{Mborkerid}.pkl')