import numpy as np
from finlab.data import Data
import gc
from sklearn.linear_model import LinearRegression
import numpy as np
import datetime
#import matplotlib.pyplot as plot
import warnings
import pandas as pd

import sqlite3
conn = sqlite3.connect('./sqllite3/brokder.db')
cursor = conn.cursor()

warnings.filterwarnings("ignore")

def merge_sell_buy_data(mid,subid,sotckid,startdate):
    cnt = 0
    sql = f"select * from broker_buy where mainBroker='{mid}' and subbroker='{subid}' and stockid='{sotckid}'"
    fs = pd.read_sql(sql,conn)
    fs['date'] = pd.to_datetime(fs['date']).dt.date
    fs.set_index('date',inplace=True)
    return fs

def get_correlation_value(brokerdata,stockid,startdate,cumsum=False):
    data = Data()
    s89 = data.get("收盤價")
    close = pd.DataFrame(s89)
    close = close[stockid]
    close = pd.DataFrame(close)
    close = close[close.index > pd.to_datetime(startdate)]
    brokerdata.drop_duplicates(keep='last',inplace=True)
    #dff = brokerdata #pd.DataFrame(brokerdata)
    if (cumsum) == True:
        s= brokerdata['diff'].cumsum()
    else:
        s=brokerdata['diff']
    close['bkdata'] = s

    close['bkdata'] = close['bkdata'].ffill()
    close.fillna(0,inplace=True)
    arr1 = close[stockid]
    arr2 = close['bkdata']

    correlation = np.corrcoef(arr1, arr2)[0, 1]
    #print("Correlation:", correlation)
    cnt = len(close)
    #close = None
    s89 = None
    gc.collect()
    return correlation,close,cnt
#------------------------------------------------------------------------
#transation case 1
#if 條件1 == 1 and hold == 0 then do b or s
#不考慮pred and close是否維持同樣方向    
#------------------------------------------------------------------------
def case1_trans(close):
    trans = 0
    price = 0
    close['hold'] = np.nan
    close['trans'] = 0
    close['hold_price'] =0
    close['bs'] = np.nan
    for idx  in close.index:
        #bs = buy or sell direction , compare writh predit and current price 
        if close['pred'][idx] >  close[stockid][idx]:
            close['bs'][idx] = 1
        else:
            close['bs'][idx] = -1
        #trans signal is 1 and no any transation
        if close['p_shift_diff'][idx] == 1 and trans == 0:
            #do transation , hold is 1
            if close['pred'][idx]  ==  close[stockid][idx]:
                continue
            trans = 1
            close['hold'][idx] = 1
            close['trans'][idx] = 1
            price = close[stockid][idx]
        #trans signal is 1 and had transation, set close signal (hold is -1)
        elif close['p_shift_diff'][idx] == 1 and trans == 1:
            trans = 0
            close['hold'][idx] = 0
            close['trans'][idx] = -1
            price = 0

    #為了要模擬交易
    #因為訊號觸發之後要隔天才能交易所以把交易訊號shift 1天
    close['hold'] = close['hold'].shift(1)
    close['bs'] = close['bs'].shift(1)
    close['trans'] = close['trans'].shift(1)
    c = close[close['hold'].isna() == False]
    #然後補上該天的close p
    close['hold_price'] = c[stockid]
    return close

#--------------------------------------------------------------------
#transation case 2
#if 條件1 == 1 and hold == 0 then do b or s#
#考慮pred and close是否維持同樣方向 如果是同方向 而且價格還沒到 就持續持有
#---------------------------------------------------------------------
def case2_trans(close):
    trans = 0
    trans_bs = 0
    price = 0
    #close = close.reset_index(drop=True,inplace=True)
    #close['hold2'].fillna(0,inplace=True)
    close['hold2'] = 0.0
    close['trans2'] = 0
    close['hold_price2'] =0
    close['bs'] = 0
    #close.reset_index(drop=True,inplace=True)
    sindx = close.index
    #for idx  in close.index:
    #sindx = close.index
    for id  in range(0,len(sindx)):
        idx = sindx[id]        
        #bs = buy or sell direction , compare writh predit and current price 
        if close['pred'][idx] >  close[stockid][idx]:
            close['bs'][idx] = 1
        else:
            close['bs'][idx] = -1
        #trans signal is 1 and no any transation
        if close['p_shift_diff'][idx] == 1 and trans == 0:
            #do transation , hold is 1
            if close['pred'][idx]  ==  close[stockid][idx]:
                continue
            trans = 1
            trans_bs = close['bs'][idx]
            if (id+1) >= len(sindx):
                continue
            idxn = sindx[id+1]    
            close['hold2'][idxn] = 1
            close['trans2'][idxn] = 1
            price = close[stockid][idxn]
            close['hold_price2'][idxn]=price
        #if trans ==1 (buy Strategy) and current price is more then preditc price then close
        elif trans == 1 and (trans_bs==1 and close[stockid][idx] >= close['pred'][idx]):
            if close['trans2'][idx] != 0:
                continue
            trans = 0
            close['hold2'][idx] = 0
            close['trans2'][idx] = -1
            price = close[stockid][idx]
            close['hold_price2'][idx]=price
        #if trans ==-1 (sell Strategy) and current price is lenn then preditc price then close            
        elif trans == 1 and (trans_bs==-1 and close[stockid][idx] <= close['pred'][idx]):
            if close['trans2'][idx] != 0:
                continue
            trans = 0
            close['hold2'][idx] = 0
            close['trans2'][idx] = -1
            price = close[stockid][idx]
            close['hold_price2'][idx]=price
        #if have trans signa and 相反 direction
        elif close['p_shift_diff'][idx] == 1 and trans == 1:
            if close['bs'][idx] != trans_bs:
                #force close hold
                close['hold2'][idx] = 0
                idxn = sindx[id+1]    
                close['trans2'][idxn] = -1
                price = close[stockid][idxn]
                close['hold_price2'][idxn]=price
                trans = 0
    #為了要模擬交易
    #因為訊號觸發之後要隔天才能交易所以把交易訊號shift 1天
    close['bs'] = close['bs'].shift(1)
    return close    

#profit cacluat
def caclprofit(newcolname,transcol,holdprice,close):
    profit = 0
    eprice = 0
    sprice = 0
    trans = 0
    bs=0
    try:
        for idx  in close.index:
            if close[transcol][idx] ==1: #trans signal
                #signal trigger and no any transation
                if trans != 0:
                    raise Exception(f"if signal is 1, trans must 0, idx={idx}")
                bs =  close['bs'][idx]
                sprice = close[holdprice][idx]
                if bs == -1: #buy or sell
                    trans = -1 #記錄手上是buy or sell
                else:
                    trans = 1
            elif close[transcol][idx] ==-1: #trans signal
                eprice = close[holdprice][idx]
                if trans == -1 : #手上是buy or sell 決定profit的計算
                    close[newcolname][idx] = sprice-eprice
                    profit += sprice-eprice
                else:
                    close[newcolname][idx] = eprice-sprice
                    profit += eprice-sprice
                trans = 0
        #print("profit:" + str(profit))
        return close,profit
        
        
    except Exception as e:
        print(str(e))

def loadBrokerPikle(Mborkerid):
    sql = f"select * from broker_buy where mainbroker = '{Mborkerid}'"
    df = pd.read_sql(sql,conn)
    return df

data = Data()
s89 = data.get("收盤價")
alldata = pd.DataFrame(s89)
#p = alldata['8299'][alldata['8299'].index.max()]
import time
def process_sql(df,sql,read=True):
    for i in range(0,2):
        try:
            if read:
                df1 = pd.read_sql(sql,conn)
                return df1
            else:
                df.to_sql('pdit_data', conn,if_exists='append', index=False)
                break
        except Exception as e:
            time.sleep(10)
            continue


import os
#data = Data()
#s89 = data.get("收盤價")
#Dalldata = pd.DataFrame(s89)
#stkidlist = alldata.columns
#alldata = None
s89 = None
data = None
gc.collect()
profitResults = []
i=0
col = ['stockid','mainid','subid','broker_trans_count','correc','case1profit','trans1_cnt','case2profit','trans2_cnt','currentPrice','update_date']
dfpdit = pd.DataFrame(columns=col)
date = datetime.datetime.now().date()
#date = datetime.date(2023,2,16)
t1 = datetime.datetime.now()

#borkerdf= pd.read_csv('broker_id.csv',encoding='big5')

sql = f"select * from broker_data_main"
#df = pd.read_csv('broker_id1.csv',encoding='big5')
Mborkerdfidx = process_sql(None,sql,True)
#pd.read_sql(sql,conn)

#Mborkerdfidx = borkerdf[borkerdf['MainBroder'] == 'Y']
totalcnt = len(Mborkerdfidx)
startcnt = 0

#if os.path.isfile('./predict/pdit.pkl'):
#    dfpdit = pd.read_pickle('./predict/pdit.pkl')

for Mborkeridx in Mborkerdfidx.index:
    
    fullbuy = None
    fullsell = None
    gc.collect()
    #Mborkeridx = 139
    Mborkerid = Mborkerdfidx['證券商代號'][Mborkeridx]
    sql = f"select * from broker_data_detail where mainid = '{Mborkerid}'"
    subBrokerid = process_sql(None,sql,True)
    #pd.read_sql(sql,conn)
    list = [Mborkerid, Mborkerid, "", "","",""]
    subBrokerid.loc[len(subBrokerid)] = list
    #subBrokerid = borkerdf[borkerdf['證券商名稱'] ==  Mborkerdfidx['證券商名稱'][Mborkeridx]]

    fullbuy = loadBrokerPikle(Mborkerid)
    fullbuy['date'] = pd.to_datetime(fullbuy['date']).dt.date
    fullbuy.set_index('date',inplace=True)

    #if fullbuy is None:
    #    continue
    #fullbuy = fullbuy.append(fullsell)
    #fullbuy = fullbuy['stockid']
    #fullbuy.drop_duplicates(subset=['stockid'],inplace=True)
    #stkidlist = fullbuy['stockid']
    #fullbuy=None
    #fullsell = None
    gc.collect()
    for subbrokerIdidx in subBrokerid.index:
        dfpdit = pd.DataFrame(columns=col)
        #if subBrokerid['subBroderId'][subbrokerIdidx] == subBrokerid['證券商名稱'][subbrokerIdidx]:
        #    subborkerid = Mborkerid
        #else:
        subborkerid = subBrokerid['證券商代號'][subbrokerIdidx]
        #if borkerdf['valid'][subbrokerIdidx] == 'N':
        #    continue
        scount = 0
        #subborkerid = '2200'
        mainid = Mborkerid
        subid = subborkerid

        #stkidlist = f"select * from broker_buy where mainbroker = '{Mborkerid}' and subbroker='{subid}'"
        #stkidlist = pd.read_sql(stkidlist,conn)
        stkidlist = fullbuy['stockid'].value_counts()

        #stkidlist = fullbuy[(fullbuy['mainBroker']==mainid) & (fullbuy['subBroker']==subid)]
        #stkidlist = fullbuy['stockid'].value_count()
        try:
            for stkid in stkidlist.index:
                if stkid == '':
                    continue
                #stkid = '8044'
                profitResults=[]
                Result = []

                stockid= stkid
                t3 = datetime.datetime.now()
                scount += 1
                sql = f"select * from pdit_data where mainid='{mainid}' and subid='{subid}' and stockid='{stockid}' and update_date='{date.strftime('%Y-%m-%d')}'"
                #s1 = pd.read_sql(sql,conn)
                s1 = process_sql(None,sql,True)
                #s1 = dfpdit[(dfpdit['mainid']==mainid) & (dfpdit['subid']==subid) & (dfpdit['stockid']==stockid) & (dfpdit['update_date']==date)]
                if len(s1) !=0:
                    t4 = datetime.datetime.now()
                    print(f"{mainid}{subid} -{stockid} - {scount}/{len(stkidlist)}-t:{round((t4.timestamp()-t3.timestamp()),2)}-skip")
                    continue
                try:
                    currprice  = alldata[stockid][alldata[stockid].index.max()]
                    print(alldata[stockid].index.max())
                except Exception as e:
                    currprice = -1

                Result.append(stockid)
                Result.append(mainid)
                Result.append(subid)

                brokerdata = fullbuy[(fullbuy['mainBroker']==mainid) & (fullbuy['subBroker']==subid) & (fullbuy['stockid']==stockid)]
                #merge_sell_buy_data(mainid,subid,stockid,pd.to_datetime(datetime.date(2022,3,1)))
                #print(len(brokerdata))
                #計算正相關係數
                Result.append(len(brokerdata))
                corr,close,cnt = get_correlation_value(brokerdata,stockid,pd.to_datetime(datetime.date(2022,3,1)))
                #get LinerRegression
                
                Result.append(round(corr, 2))
                arr1 = close[stockid]
                arr2 = close['bkdata']
                a = np.array(arr2).reshape(-1,1)
                b = arr1
                reg = LinearRegression().fit(a,b)
                b_pred = reg.predict(a)
                #print(b_pred)'
                close['pred'] = b_pred
                close.to_csv('psotck1.csv')
                s1 = close[stockid]
                #transation condition 1: pred是否有變化 
                #   - pred 前後有差值代表有變化 , 轉化成0,1 [p_shift_diff]
                close['bs'] = 0
                pshift =  close['pred'].shift(1)
                close['p_shift_diff'] =  close['pred']  - pshift
                close['p_shift_diff'].fillna(0,inplace=True)
                #close['p_shift_diff'] = close['p_shift_diff'].astype(np.int8)
                s= (close['p_shift_diff'] != 0)
                hold = pd.DataFrame(np.nan, index=close.index, columns=['t'])
                hold[s] = 1
                hold.fillna(0,inplace=True)
                close['p_shift_diff']  = hold
                close['p_shift_diff'] = close['p_shift_diff'].astype(np.int8)
                #transation condition 2: pred跟stk price 是否有差異
                #  - pred - close
                close['p_stk_diff'] = close['pred'] -  close[stockid]
                close['hold'] = np.nan

                #test case1
                close = case1_trans(close)
                close.fillna(0,inplace=True)
                close.head(30)
                #close.to_csv('phold.csv')
                #cacl case1 profit
                close['case1profit'] = 0
                
                close ,profit= caclprofit('case1profit','trans','hold_price',close)
                Result.append(round(profit, 2))
                Result.append(len(close[close['trans']!=0]))
                #Result.append(profit)
                #close.to_csv('phold.csv')    

                #test case2
                close = case2_trans(close)
                #close['hold'].ffill(inplace= True)
                #close['hold_price'].ffill(inplace= True)
                close.fillna(0,inplace=True)
                close.head(30)
                #close.to_csv('phold.csv')
                #cacl case2 profit
                close['case2profit'] = 0
                close ,profit1= caclprofit('case2profit','trans2','hold_price2',close)
                Result.append(round(profit1, 2))
                Result.append(len(close[close['trans2']!=0]))
                Result.append(currprice)
                Result.append(date)
                profitResults.append(Result)
                print(Result)
                
                df = pd.DataFrame(data=profitResults,columns=col)
                close.to_csv(f"./analysis/phold_{mainid}_{subid}_{stockid}.csv")
                #dfpdit = dfpdit.append(df)
                #dfpdit.to_pickle('./predict/pdit.pkl')
                df.to_sql('pdit_data', conn,if_exists='append', index=False)
                #process_sql(df,sql,False)
                t2 = datetime.datetime.now()
        except Exception as e:
            print(f"excep {mainid} {subid} {stockid} -{str(e)}")
        
t2 = datetime.datetime.now()
print("processtime:" + str(t2-t1))
    #close.to_csv('phold.csv')
#df = pd.read_pickle('./predict/pdit.pkl')
sql = f"select * from pdit_data where update_date='{date.strftime('%Y-%m-%d')}'"
s1 = pd.read_sql(sql,conn)
s1.to_csv(f"./predict/pdit_{date.strftime('%Y-%m-%d')}.csv")