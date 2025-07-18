#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
從台灣證券櫃檯買賣中心網站直接讀取 JSON 資料
正確解析實際的 JSON 結構
"""

import requests
import json
import pandas as pd
from datetime import datetime
import urllib3

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def fetch_and_analyze_json():
    """從網站讀取並分析實際的 JSON 結構"""
    
    url = "https://www.tpex.org.tw/web/stock/exright/dailyquo/exDailyQ_result.php?l=zh-tw&d=114/06/01&ed=114/06/30"
    
    print(f"🔍 從網站讀取 JSON 資料...")
    print(f"URL: {url}")
    print("=" * 80)
    
    try:
        # 發送請求
        res = requests.get(url, timeout=30, verify=False)
        
        print(f"HTTP狀態碼: {res.status_code}")
        print(f"Content-Type: {res.headers.get('Content-Type', 'N/A')}")
        print(f"回應長度: {len(res.text)} 字元")
        
        if res.status_code == 200:
            # 儲存原始回應
            with open('網站原始回應.txt', 'w', encoding='utf-8') as f:
                f.write(res.text)
            print("✅ 原始回應已儲存")
            
            try:
                # 解析JSON
                json_data = res.json()
                print("✅ JSON解析成功")
                
                # 儲存格式化JSON
                with open('網站格式化.json', 'w', encoding='utf-8') as f:
                    json.dump(json_data, f, ensure_ascii=False, indent=2)
                print("💾 格式化JSON已儲存")
                
                # 詳細分析JSON結構
                print(f"\n📊 JSON結構詳細分析:")
                print(f"資料類型: {type(json_data)}")
                
                if isinstance(json_data, dict):
                    print(f"主要鍵值: {list(json_data.keys())}")
                    
                    # 顯示每個鍵值的詳細資訊
                    for key, value in json_data.items():
                        print(f"\n🔍 鍵值 '{key}':")
                        print(f"  類型: {type(value)}")
                        
                        if isinstance(value, str):
                            print(f"  內容: {value[:200]}...")
                        elif isinstance(value, (int, float)):
                            print(f"  值: {value}")
                        elif isinstance(value, list):
                            print(f"  長度: {len(value)}")
                            if len(value) > 0:
                                print(f"  第一個元素類型: {type(value[0])}")
                                if isinstance(value[0], dict):
                                    print(f"  第一個元素鍵值: {list(value[0].keys())}")
                                else:
                                    print(f"  第一個元素: {value[0]}")
                        elif isinstance(value, dict):
                            print(f"  子鍵值: {list(value.keys())}")
                    
                    # 尋找包含 fields 和 data 的結構
                    fields_found = None
                    data_found = None
                    
                    def search_for_fields_data(obj, path=""):
                        """遞迴搜尋 fields 和 data"""
                        nonlocal fields_found, data_found
                        
                        if isinstance(obj, dict):
                            if 'fields' in obj and 'data' in obj:
                                print(f"\n✅ 在 '{path}' 找到 fields 和 data!")
                                fields_found = obj['fields']
                                data_found = obj['data']
                                return True
                            
                            for key, value in obj.items():
                                new_path = f"{path}.{key}" if path else key
                                if search_for_fields_data(value, new_path):
                                    return True
                        
                        elif isinstance(obj, list):
                            for i, item in enumerate(obj):
                                new_path = f"{path}[{i}]" if path else f"[{i}]"
                                if search_for_fields_data(item, new_path):
                                    return True
                        
                        return False
                    
                    # 開始搜尋
                    print(f"\n🔍 搜尋 fields 和 data 結構...")
                    found = search_for_fields_data(json_data)
                    
                    if found and fields_found and data_found:
                        print(f"\n📋 欄位名稱 (共 {len(fields_found)} 個):")
                        for i, field in enumerate(fields_found):
                            print(f"  {i+1:2d}. {field}")
                        
                        print(f"\n📊 資料筆數: {len(data_found)}")
                        
                        # 創建 DataFrame
                        df = pd.DataFrame(data_found, columns=fields_found)
                        
                        print(f"\n📈 DataFrame 資訊:")
                        print(f"  形狀: {df.shape}")
                        print(f"  欄位數: {len(df.columns)}")
                        
                        # 顯示前幾行
                        print(f"\n📋 前 3 行資料預覽:")
                        print(df.head(3).to_string(index=False))
                        
                        # 尋找 00937B
                        print(f"\n🔍 尋找 00937B...")
                        target_rows = df[df.apply(lambda row: row.astype(str).str.contains('00937B', na=False).any(), axis=1)]
                        
                        if not target_rows.empty:
                            print(f"✅ 找到 {len(target_rows)} 筆 00937B 資料:")
                            
                            for idx, row in target_rows.iterrows():
                                print(f"\n📄 資料內容:")
                                for col, val in row.items():
                                    print(f"  {col}: {val}")
                                
                                # 計算收益
                                dividend_fields = ['息值', '現金股利', '配息金額']
                                for field in dividend_fields:
                                    if field in row.index and row[field]:
                                        try:
                                            dividend = float(row[field])
                                            if dividend > 0:
                                                holdings = 171.0
                                                income = holdings * dividend
                                                print(f"  💰 配息收益: {income:.2f} 元 (持股{holdings}股)")
                                                break
                                        except (ValueError, TypeError):
                                            continue
                        else:
                            print("❌ 未找到 00937B")
                        
                        # 儲存檔案
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
                        
                        # 完整資料
                        csv_file = f'網站完整資料_{timestamp}.csv'
                        df.to_csv(csv_file, index=False, encoding='utf-8-sig')
                        print(f"\n💾 完整資料已儲存: {csv_file}")
                        
                        # 00937B 專用資料
                        if not target_rows.empty:
                            target_csv = f'網站00937B_{timestamp}.csv'
                            target_rows.to_csv(target_csv, index=False, encoding='utf-8-sig')
                            print(f"💾 00937B 資料已儲存: {target_csv}")
                        
                        return df
                    else:
                        print("❌ 未找到 fields 和 data 結構")
                        print("JSON 可能使用不同的格式")
                        return None
                
                else:
                    print(f"❌ JSON 不是字典格式: {type(json_data)}")
                    return None
                    
            except json.JSONDecodeError as e:
                print(f"❌ JSON解析失敗: {e}")
                print("前500字元:")
                print(res.text[:500])
                return None
        else:
            print(f"❌ HTTP請求失敗: {res.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ 發生錯誤: {e}")
        return None

def main():
    """主程序"""
    print("🌐 台灣證券櫃檯買賣中心網站 JSON 分析器")
    print("📊 分析實際的 JSON 結構，不假設任何格式")
    print("🎯 查詢期間: 114/06/01 - 114/06/30")
    print("=" * 80)
    
    # 分析並處理
    df = fetch_and_analyze_json()
    
    if df is not None:
        print(f"\n✅ 處理完成！")
        print(f"📊 成功處理 {len(df)} 筆資料")
    else:
        print(f"\n❌ 處理失敗")
        print("請檢查 '網站格式化.json' 檔案來了解實際的 JSON 結構")

if __name__ == "__main__":
    main()
