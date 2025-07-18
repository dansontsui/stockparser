import requests
import json

# 設定 ETF 代號
etf_id = "0056"

# 發送 HTTP 請求
response = requests.get(f"https://www.twse.com.tw/zh/ETFortune/dividendCalendar?query={etf_id}")

# 解析 JSON 回應
data = json.loads(response.content)

# 輸出配息資料
for dividend in data["Dividends"]:
    print(f"配息年度：{dividend['Year']}")
    print(f"配息月分：{dividend['Month']}")
    print(f"現金股息：{dividend['CashDividend']}")
    print(f"股票股息：{dividend['StockDividend']}")
    print()
