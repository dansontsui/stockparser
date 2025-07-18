#import stkfunction as sf
from datetime import datetime, timedelta
import stkfunction as sf
sf.aaa()
# 假設今天是2025/01/01，你可以根據實際情況更改
today = datetime.today()

# 計算昨天的日期
yesterday = today - timedelta(days=1)
# 格式化日期為所需的字符串格式
formatted_date = yesterday.strftime('%Y/%m/%d')
df_twse_stk =  sf.get_stk_twse_info(formatted_date)

df_otc_stk =  sf.get_stk_otc_info(formatted_date)
df_otc_stk



import csv
import os
import pandas as pd
# 假設stkPool.csv文件位於./TraceTarget資料夾中
stkPool_file_path = os.path.join('./TraceTarget', 'stkPool.csv')

# 讀取stkPool.csv文件中的股票代號
df_stkpool = pd.read_csv(stkPool_file_path)
df_stkpool = df_stkpool.set_index('代號',drop=True)
df_stkpool['殖利率'] = 0.0
# 遍歷股票代號列表，使用twstock獲取每個股票的昨日收盤價
for stock_code in df_stkpool.index:
    stock = df_twse_stk[df_twse_stk['代號'] == str(stock_code)]
    if len(stock) == 0:
        stock = df_otc_stk[df_otc_stk['代號'] == str(stock_code)]
    try:
        print(f"{stock_code} - { stock.iloc[0]['收盤']}")
    except Exception as e:
        print(f"Error processing {stock_code}: {e}")
        continue
    if len(stock) > 0 :
        df_stkpool.loc[stock_code, '昨日收盤價'] =  float(stock.iloc[0]['收盤'])
    current_prices = df_stkpool['昨日收盤價'][stock_code]
    estimated_dividends = df_stkpool['2025 預估配息'][stock_code]
    estimated_yields  = estimated_dividends / current_prices
    df_stkpool.loc[stock_code, '殖利率'] = round(estimated_yields*100, 2)
# 打印結果
print(df_stkpool)
df_stkpool.to_csv(stkPool_file_path)
stkmessage = ''
#df.to_csv('./TraceTarget/stkPool.csv')
for stock_code in df_stkpool.index:
    estimated_yields = df_stkpool['殖利率'][stock_code]
    if estimated_yields == 0:
        continue
    cheap = df_stkpool['便宜價'][stock_code]
    good = df_stkpool['實惠'][stock_code]
    makesense = df_stkpool['合理'][stock_code]
    stop = df_stkpool['股實'][stock_code]
    expensive = df_stkpool['昂貴'][stock_code]
    if estimated_yields >= cheap:
        stkmessage += f"<br> {stock_code} {df_stkpool['公司'][stock_code]} 便宜 <br>"
        print(f"{stock_code} {df_stkpool['公司'][stock_code]} 便宜 {df_stkpool['昨日收盤價'][stock_code]}")
    elif estimated_yields <= cheap and estimated_yields >= good:
        stkmessage += f"{stock_code} {df_stkpool['公司'][stock_code]} 實惠  <br>"
        print(f"{stock_code} {df_stkpool['公司'][stock_code]} 實惠 {df_stkpool['昨日收盤價'][stock_code]}")
    elif estimated_yields <= good and estimated_yields >= makesense:
        stkmessage += f"{stock_code} {df_stkpool['公司'][stock_code]} 合理  <br>"
        print(f"{stock_code} {df_stkpool['公司'][stock_code]} 合理 {df_stkpool['昨日收盤價'][stock_code]}")
    elif estimated_yields <= makesense and estimated_yields >= stop:
        stkmessage += f"{stock_code} {df_stkpool['公司'][stock_code]} 殷實  <br>"
        print(f"{stock_code} {df_stkpool['公司'][stock_code]} 殷實 {df_stkpool['昨日收盤價'][stock_code]}")        
    elif estimated_yields <= stop and estimated_yields >= expensive:
        stkmessage += f"{stock_code} {df_stkpool['公司'][stock_code]} 昂貴  <br>"
        print(f"{stock_code} {df_stkpool['公司'][stock_code]} 昂貴 {df_stkpool['昨日收盤價'][stock_code]}")              
    elif estimated_yields <= expensive:
        stkmessage += f"{stock_code} {df_stkpool['公司'][stock_code]} 超貴  <br>"
        print(f"{stock_code} {df_stkpool['公司'][stock_code]} 超貴 {df_stkpool['昨日收盤價'][stock_code]}")


import mail_alert as ma
ma.send_mail2('danson.tsui@gmail.com',stkmessage)