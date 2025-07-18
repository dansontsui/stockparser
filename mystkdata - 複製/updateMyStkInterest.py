import numpy as np
import pandas as pd
import io
import requests
import pandas as pd
import datetime
import json
import get_stk_v

def get_twse_div_data():
    datestr = datetime.datetime.now().strftime('%Y%m%d')
    # 獲取今天的日期
    today = datetime.datetime.now().date()
    # 計算30天前的日期
    days_ago = today - datetime.timedelta(days=30)
    start_datestr = days_ago.strftime('%Y%m%d')
    querystring = f"https://www.twse.com.tw/rwd/zh/exRight/TWT49U?startDate={start_datestr}&endDate={datestr}&response=csv"

    #querystring = f"https://www.twse.com.tw/exchangeReport/TWT49U?response=csv&strDate={start_datestr}&endDate={datestr}"
    #https://www.twse.com.tw/zh/announcement/ex-right/twt49u.html
    #querystring = f"https://www.twse.com.tw/exchangeReport/TWT49U?response=csv"
    print(querystring)
    res = requests.get(querystring)
    df = pd.read_csv(io.StringIO(res.text.replace("=", "")), header=1)
    df = df.dropna(thresh=5).dropna(how='all', axis=1)
    df = df[~df['資料日期'].isnull()]
    years = df['資料日期'].str.split('年').str[0].astype(int) #+ 1911

        #years.loc[df['資料日期'].str[3] != '年'] = np.nan
    years.loc[df['資料日期'].str.find('年') == -1] = np.nan
    years.loc[years > datetime.datetime.now().year] = np.nan
    years.ffill(inplace=True)
    dates = years.astype(int).astype(str) +'/'+ df['資料日期'].str.split('年').str[1].str.replace('月', '/').str.replace('日', '')
    df['date'] = dates #pd.to_datetime(dates, errors='coerce')

    #float_name_list = ['除權息前收盤價', '除權息參考價', '權值+息值', '漲停價格',
    #                    '跌停價格', '開盤競價基準', '減除股利參考價' , '最近一次申報每股 (單位)淨值',
    #                    '最近一次申報每股 (單位)盈餘']
    float_name_list = ['除權息前收盤價', '除權息參考價', '權值+息值', '漲停價格',
                        '跌停價格', '開盤競價基準', '減除股利參考價' , '最近一次申報每股 (單位)淨值']
    

    df[float_name_list] = df[float_name_list].astype(str).apply(lambda s:s.str.replace(',', '')).astype(float)
    df['twse_divide_ratio'] = df['除權息前收盤價'] / df['開盤競價基準']
    df.to_csv(f'twse_div_data.csv',index=0)
    df.to_csv(f'twse_div_data_{today}.csv',index=0)
    return df





def get_otc_div_data():
    y = datetime.datetime.now().year
    m = datetime.datetime.now().month
    d = datetime.datetime.now().day

    y = str(y-1911)
    m = str(m) if m > 9 else '0' + str(m)
    d = str(d) if d > 9 else '0' + str(d)
    datestr = '%s/%s/%s' % (y,m,d)


    # 獲取今天的日期
    today = datetime.datetime.now().date()
    # 計算30天前的日期
    days_ago = today - datetime.timedelta(days=30)

    y = str(days_ago.year-1911)
    m = str(days_ago.month) if days_ago.month > 9 else '0' + str(days_ago.month)
    d = str(days_ago.day) if days_ago.day > 9 else '0' + str(days_ago.day)
    # 計算30天前的日期
    start_datestr = '%s/%s/%s' % (y,m,d)
   
    res_otc = requests.get(f'https://www.tpex.org.tw/web/stock/exright/dailyquo/exDailyQ_result.php?l=zh-tw&d={start_datestr}&ed={datestr}')

    #df = pd.DataFrame(json.loads(res_otc.text)['aaData'])
    df = pd.DataFrame(json.loads(res_otc.text)['tables'][0]['data'])
    #df = pd.DataFrame(json.loads(res_otc.text))
    df.columns = ['除權息日期', '代號', '名稱', '除權息前收盤價', '除權息參考價',
                        '權值', '息值',"權+息值","權/息","漲停價格","跌停價格","開盤競價基準",
                        "減除股利參考價","現金股利", "每千股無償配股", "現金增資股數", "現金增資認購價",
                        "公開承銷股數", "員工認購股數","原股東認購數", "按持股比例千股認購"]


    float_name_list = [ '除權息前收盤價', '除權息參考價',
                            '權值', '息值',"權+息值","漲停價格","跌停價格","開盤競價基準",
                            "減除股利參考價","現金股利", "每千股無償配股", "現金增資股數", "現金增資認購價",
                            "公開承銷股數", "員工認購股數","原股東認購數", "按持股比例千股認購"
    ]
    df[float_name_list] = df[float_name_list].astype(str).apply(lambda s:s.str.replace(',', '')).astype(float)

    # set stock id
    df['stock_id'] = df['代號'] + ' ' + df['名稱']

    # set dates
    dates = df['除權息日期'].str.split('/')
    dates = (dates.str[0].astype(int) + 1911).astype(str) + '/' + dates.str[1] + '/' + dates.str[2]
    df['date'] = pd.to_datetime(dates)

    df['otc_divide_ratio'] = df['除權息前收盤價'] / df['開盤競價基準']
    df.to_csv('otc_div_data.csv')
    return df
#return df.set_index(['stock_id', 'date'])


def update_interest_data_twse(stkid):
    from datetime import datetime
    global mystk_his
    myhis_stkid = stkid
    stkid = stkid.replace('X','')
    stkinfo = twse_div_data[twse_div_data['股票代號']==stkid]
    #print(stkinfo)
    mystk_his1 =  mystk_his[mystk_his['stkid']==myhis_stkid]
    for idx in stkinfo.index:
        #print(idx)
        s = stkinfo['date'][idx]
        sdiv = stkinfo['權值+息值'][idx]
        print(sdiv)
        year_month = s.split('/')[0] + '/' + s.split('/')[1]
        print(year_month)
        index = mystk_his1.index[(mystk_his1["date"] == year_month)]
        myminimusDate = mystk_his1["date"].min()
        index = mystk_his1.index[(mystk_his1["date"] == year_month)]
        Myyear = str(int(myminimusDate.split('/')[0])+1911)
        stkyear = str(int(year_month.split('/')[0])+1911)
        stkyear = stkyear + '/' + year_month.split('/')[1]
        Myyear = Myyear + '/' + myminimusDate.split('/')[1]
        # 將字串轉換成日期格式
        date_format = '%Y/%m'
        stkdate1 = datetime.strptime(stkyear, date_format)
        mydate2 = datetime.strptime(Myyear, date_format)
        # 比較兩個日期
        if stkdate1 < mydate2:
            continue
        # mystk日期不存在 就新增一筆
        if len(index) == 0: 
            cumulative_sum = mystk_his1['Qty'].sum()
            new_data = [{'date': year_month, 'Qty': 0, 'stkid': myhis_stkid, 'stkdiv': sdiv, 'Interest': 0}]
            new_data[0]['Interest'] =  sdiv *  cumulative_sum *1000
            new_data[0]['stkdiv'] = sdiv
            new_df = pd.DataFrame(new_data)
            mystk_his = pd.concat([mystk_his, new_df], ignore_index=True)
            #mystk = pd.merge(mystk_his,mystk_his1)
            continue

        cumulative_sum = mystk_his1.loc[:index[0], 'Qty'].sum()        
        print(index[0])
        #print(mystk_his1.iloc[index[0]].to_frame().T)
        mystk_his.loc[index[0],'stkdiv'] = sdiv
        mystk_his.loc[index[0],'Interest'] = sdiv *  cumulative_sum * 1000
    mystk_his.to_csv('aaa.csv')
    return mystk_his

def update_interest_data(stkid):
    global mystk_his
    from datetime import datetime
    #mystk_his= pd.read_csv('myhistory_acc.csv',index_col=0)
    #mystk_his = mystk_his.reset_index(drop=True)
    myhis_stkid = stkid
    stkid = stkid.replace('X','')
    stkinfo = otc_div_data[otc_div_data['代號']==myhis_stkid]
    if len(stkinfo) == 0: #not found in otc data
        return update_interest_data_twse(myhis_stkid)
    #print(stkinfo)
    mystk_his1 =  mystk_his[mystk_his['stkid']==stkid]
    cumulative_sum = 0
    for idx in stkinfo.index:
        #print(idx)
        s = stkinfo['除權息日期'][idx]
        sdiv = stkinfo['息值'][idx]
        print(sdiv)
        year_month = s.split('/')[0] + '/' + s.split('/')[1]
        print(year_month)
        #做日期處理 比大小 ,以前的日期 不處理
        myminimusDate = mystk_his1["date"].min()
        index = mystk_his1.index[(mystk_his1["date"] == year_month)]
        Myyear = str(int(myminimusDate.split('/')[0])+1911)
        stkyear = str(int(year_month.split('/')[0])+1911)
        stkyear = stkyear + '/' + year_month.split('/')[1]
        Myyear = Myyear + '/' + myminimusDate.split('/')[1]
        # 將字串轉換成日期格式
        date_format = '%Y/%m'
        stkdate1 = datetime.strptime(stkyear, date_format)
        mydate2 = datetime.strptime(Myyear, date_format)

        # 比較兩個日期
        if stkdate1 < mydate2:
            continue
        # mystk日期不存在 就新增一筆
        if len(index) == 0: 
            new_data = [{'date': year_month, 'Qty': 0, 'stkid': myhis_stkid, 'stkdiv': sdiv, 'Interest': 0}]
            new_data[0]['Interest'] =  sdiv *  cumulative_sum *1000
            new_data[0]['stkdiv'] = sdiv
            new_df = pd.DataFrame(new_data)
            mystk_his = pd.concat([mystk_his, new_df], ignore_index=True)
            continue
        cumulative_sum = mystk_his1.loc[:index[0], 'Qty'].sum()   
        print(index[0])
        #print(mystk_his1.iloc[index[0]].to_frame().T)
        mystk_his.loc[index[0],'stkdiv'] = sdiv
        mystk_his.loc[index[0],'Interest'] = sdiv *  cumulative_sum *1000
    return mystk_his

mystk_his= pd.read_csv('myhistory.csv',index_col=0)

get_otc_div_data()
otc_div_data = pd.read_csv('otc_div_data.csv')
get_twse_div_data()
twse_div_data = pd.read_csv('twse_div_data.csv')

#mystk_his= pd.read_csv('myhistory.csv',index_col=0)
mystk_his = mystk_his.reset_index(drop=True)
ids = mystk_his.value_counts('stkid')
for a in ids.index:
    print(a)
    mystk_his = update_interest_data(a)
mystk_his.to_csv('myhistory.csv')
mystk_his.head(20)

writer = pd.ExcelWriter('output.xlsx', engine='xlsxwriter')

s = mystk_his.groupby(['date','stkid']).agg({'Qty': 'sum','Interest':'sum'})
#s.to_csv('sumbydate.csv')
s.to_excel(writer, sheet_name='sumbydate_stkid')

s = mystk_his.groupby(['stkid']).agg({'Qty': 'sum','Interest':'sum'})
s.to_excel(writer, sheet_name='sumbystkid')

s = mystk_his.groupby(['date']).agg({'Interest':'sum'})
s.to_excel(writer, sheet_name='sumbydate')
writer.close()
