import numpy as np
from finlab.data import Data
import gc
from sklearn.linear_model import LinearRegression
import numpy as np
import datetime
#import matplotlib.pyplot as plot
import warnings
import pandas as pd
import matplotlib.pyplot as plot

warnings.filterwarnings("ignore")

def merge_sell_buy_data(mid,subid,sotckid,startdate):
    cnt = 0
    fs = pd.read_pickle(f".\\broker\\broker_sell_{mid}.pkl")
    fs.sort_values('subBroker')
    fs = fs[fs['subBroker']== subid]
    fs = fs[fs['stockid'] == sotckid]
    fs.set_index('date',inplace= True)
    fs.sort_index(inplace=True)
    fs = fs[fs.index > pd.to_datetime(startdate)]
    #-----------------------
    fs1 = pd.read_pickle(f".\\broker\\broker_buy_{mid}.pkl")
    fs1.sort_values('subBroker')
    fs1 = fs1[fs1['subBroker']==subid]
    fs1 = fs1[fs1['stockid'] == sotckid]
    fs1.set_index('date',inplace= True)
    fs1.sort_index(inplace=True)
    fs1 = fs1[fs1.index > pd.to_datetime(startdate)]
    fs = fs.append(fs1)
    fs.sort_index(inplace=True)
    fs1 = None
    gc.collect()
    return fs

def get_correlation_value(brokerdata,stockid,startdate,cumsum=False):
    data = Data()
    s89 = data.get("收盤價")
    close = pd.DataFrame(s89)
    close = close[stockid]
    close = pd.DataFrame(close)
    close = close[close.index > pd.to_datetime(startdate)]
    #dff = brokerdata #pd.DataFrame(brokerdata)
    if (cumsum) == True:
        s= brokerdata['差額'].cumsum()
    else:
        s=brokerdata['差額']
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


import matplotlib.pyplot as plt
def bs_chart(s1,stockid):
    fig = plt.figure(figsize = (10, 8),dpi=80)
    s1 = s1.reset_index()
    usesz = pd.to_numeric(s1[stockid])
    useszstr = []
    pretrans=''
    for idx in s1.index:
        if s1['bs'][idx] == -1 and s1['trans2'][idx]==1:
            useszstr.append('s')
            pretrans = 's'
        elif s1['bs'][idx] == 1 and s1['trans2'][idx]==1:
            useszstr.append('b')
            pretrans = 'b'
        elif s1['trans2'][idx]==-1:
            if pretrans == 's':
                useszstr.append('b')
            else:
                useszstr.append('s')
        else:
                useszstr.append('')


    #xtickss = s1['']
    for i in usesz.index:
        plt.annotate(useszstr[i],xy=(i,usesz[i]),xytext=(i,usesz[i]), size=14)
        #xtickss.append(df1['date'][i])

    #plt.plot(s1.index,usesz,color='r',marker='.',linestyle=".",markersize=5,linewidth=1)
    plt.plot(s1.index,usesz,color='r',marker='o',linestyle="-",markersize=2,linewidth=1)
    plt.savefig(f"./analysis/phold_{mainid}_{subid}_{stockid}_bs.png")
    plt.show()
    #plt.xticks(usesz.index, xtickss,rotation = 60)


#s1 = close[['3017','bs','trans2','hold_price2']]
#s1.head(2)   


import sys

mainid = '7750'
subid = '7750'
stockid= '2354'

print(sys.argv)
if len(sys.argv)<4:
    print('inpurt mid,sid,stkid')
    sys.exit()
else:
    mainid = sys.argv[1]
    subid = sys.argv[2]
    stockid= sys.argv[3]


data = Data()
s89 = data.get("收盤價")
alldata = pd.DataFrame(s89)
p = alldata['8299'][alldata['8299'].index.max()]



data = Data()
s89 = data.get("收盤價")
alldata = pd.DataFrame(s89)
stkidlist = alldata.columns
#alldata = None
s89 = None
data = None
gc.collect()
profitResults = []
i=0
col = ['stockid','mainid','subid','broker_trans_count','correc','case1profit','trans1_cnt','case2profit','trans2_cnt','currentPrice']

#for stkid in stkidlist:
Result = []

try:
    currprice  = alldata[stockid][alldata[stockid].index.max()]
except Exception as e:
    currprice = -1
Result.append(stockid)
Result.append(mainid)
Result.append(subid)

brokerdata = merge_sell_buy_data(mainid,subid,stockid,pd.to_datetime(datetime.date(2022,3,1)))
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

#close.to_csv('phold.csv')    

#test case2
close = case2_trans(close)
#close['hold'].ffill(inplace= True)
#close['hold_price'].ffill(inplace= True)
close.fillna(0,inplace=True)
#close.head(30)
#close.to_csv('phold.csv')
#cacl case2 profit
close['case2profit'] = 0
close ,profit1= caclprofit('case2profit','trans2','hold_price2',close)
Result.append(round(profit1, 2))
Result.append(len(close[close['trans2']!=0]))
Result.append(currprice)
profitResults.append(Result)
df = pd.DataFrame(data = profitResults,columns = col)
print(df)
close.to_csv(f"./analysis/phold_{mainid}_{subid}_{stockid}.csv")
plot.plot(close['pred'])
s1 = close[stockid]
s2 = s1[s1 != 0]
plot.plot(s2)
plot.savefig(f"./analysis/phold_{mainid}_{subid}_{stockid}.png")
#plot.show()

s1 = close[[stockid,'bs','trans2','hold_price2']]
bs_chart(s1,stockid)



#df = pd.DataFrame(data=profitResults,columns=col)
#df.to_pickle('./predict/pdit.pkl')

    #close.to_csv('phold.csv')
#df = pd.read_pickle('./predict/pdit.pkl')
#df.to_csv('res.csv')