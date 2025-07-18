#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
從台灣證券交易所獲取除息資料
將JSON資料轉換並儲存為Excel格式
"""

import requests
import json
import pandas as pd
from datetime import datetime
import urllib3
import os

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class TSEDividendFetcher:
    """台灣證券交易所除息資料獲取器"""
    
    def __init__(self):
        """初始化"""
        self.base_url = "https://www.tpex.org.tw/web/stock/exright/dailyquo/exDailyQ_result.php"
        self.session = requests.Session()
        self.session.verify = False  # 不使用SSL驗證
        
    def fetch_dividend_data(self, start_date: str, end_date: str) -> dict:
        """
        從證交所獲取除息資料
        
        Args:
            start_date: 開始日期 (民國年格式，例如: "114/06/16")
            end_date: 結束日期 (民國年格式，例如: "114/07/16")
            
        Returns:
            JSON資料字典，失敗時返回None
        """
        params = {
            'l': 'zh-tw',
            'd': start_date,
            'ed': end_date
        }
        
        url = f"{self.base_url}?l={params['l']}&d={params['d']}&ed={params['ed']}"
        
        print(f"🔍 從證交所獲取除息資料...")
        print(f"📅 查詢期間: {start_date} ~ {end_date}")
        print(f"🌐 URL: {url}")
        print("=" * 80)
        
        try:
            # 發送請求
            response = self.session.get(url, timeout=30)
            
            print(f"HTTP狀態碼: {response.status_code}")
            print(f"Content-Type: {response.headers.get('Content-Type', 'N/A')}")
            print(f"回應長度: {len(response.text)} 字元")
            
            if response.status_code != 200:
                print(f"❌ HTTP請求失敗: {response.status_code}")
                return None
            
            # 儲存原始回應
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            raw_file = f'證交所原始回應_{timestamp}.txt'
            with open(raw_file, 'w', encoding='utf-8') as f:
                f.write(response.text)
            print(f"✅ 原始回應已儲存: {raw_file}")
            
            # 解析JSON
            try:
                json_data = response.json()
                print("✅ JSON解析成功")
                
                # 儲存格式化JSON
                json_file = f'證交所格式化_{timestamp}.json'
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(json_data, f, ensure_ascii=False, indent=2)
                print(f"💾 格式化JSON已儲存: {json_file}")
                
                return json_data
                
            except json.JSONDecodeError as e:
                print(f"❌ JSON解析失敗: {e}")
                print("前500字元:")
                print(response.text[:500])
                return None
                
        except Exception as e:
            print(f"❌ 獲取資料失敗: {e}")
            return None
    
    def analyze_json_structure(self, json_data: dict) -> tuple:
        """
        分析JSON結構並找出fields和data

        Args:
            json_data: JSON資料字典

        Returns:
            (fields, data) 元組，失敗時返回 (None, None)
        """
        print(f"\n📊 JSON結構分析:")
        print(f"資料類型: {type(json_data)}")

        if not isinstance(json_data, dict):
            print(f"❌ JSON不是字典格式: {type(json_data)}")
            return None, None

        print(f"主要鍵值: {list(json_data.keys())}")

        # 顯示每個鍵值的詳細資訊
        for key, value in json_data.items():
            print(f"\n🔍 鍵值 '{key}':")
            print(f"  類型: {type(value)}")

            if isinstance(value, str):
                print(f"  內容: {value[:100]}{'...' if len(value) > 100 else ''}")
            elif isinstance(value, (int, float)):
                print(f"  值: {value}")
            elif isinstance(value, list):
                print(f"  長度: {len(value)}")
                if len(value) > 0:
                    print(f"  第一個元素類型: {type(value[0])}")
                    if isinstance(value[0], dict):
                        print(f"  第一個元素鍵值: {list(value[0].keys())}")
                        # 檢查是否有tables結構
                        if 'fields' in value[0] and 'data' in value[0]:
                            print(f"  ✅ 第一個元素包含 fields 和 data!")
                    elif isinstance(value[0], list):
                        print(f"  第一個元素長度: {len(value[0])}")
                        if len(value[0]) > 0:
                            print(f"  第一個元素內容: {value[0][:3]}...")
                    else:
                        print(f"  第一個元素: {value[0]}")
            elif isinstance(value, dict):
                print(f"  子鍵值: {list(value.keys())}")

        # 特別處理這個網站的JSON結構
        # 結構: {"tables": [{"fields": [...], "data": [...]}]}
        if 'tables' in json_data and isinstance(json_data['tables'], list):
            tables = json_data['tables']
            if len(tables) > 0 and isinstance(tables[0], dict):
                table = tables[0]
                if 'fields' in table and 'data' in table:
                    fields = table['fields']
                    data = table['data']

                    print(f"\n✅ 在 'tables[0]' 找到 fields 和 data!")
                    print(f"\n📋 欄位名稱 (共 {len(fields)} 個):")
                    for i, field in enumerate(fields):
                        print(f"  {i+1:2d}. {field}")

                    print(f"\n📊 資料筆數: {len(data)}")

                    # 顯示其他表格資訊
                    if 'title' in table:
                        print(f"📄 表格標題: {table['title']}")
                    if 'totalCount' in table:
                        print(f"📊 總筆數: {table['totalCount']}")

                    return fields, data

        # 如果沒有找到tables結構，使用原來的遞迴搜尋
        def search_fields_data(obj, path=""):
            if isinstance(obj, dict):
                if 'fields' in obj and 'data' in obj:
                    print(f"\n✅ 在 '{path}' 找到 fields 和 data!")
                    return obj['fields'], obj['data']

                for key, value in obj.items():
                    new_path = f"{path}.{key}" if path else key
                    result = search_fields_data(value, new_path)
                    if result[0] is not None:
                        return result

            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    new_path = f"{path}[{i}]" if path else f"[{i}]"
                    result = search_fields_data(item, new_path)
                    if result[0] is not None:
                        return result

            return None, None

        print(f"\n🔍 搜尋 fields 和 data 結構...")
        fields, data = search_fields_data(json_data)

        if fields is not None and data is not None:
            print(f"\n📋 欄位名稱 (共 {len(fields)} 個):")
            for i, field in enumerate(fields):
                print(f"  {i+1:2d}. {field}")

            print(f"\n📊 資料筆數: {len(data)}")
            return fields, data
        else:
            print("❌ 未找到 fields 和 data 結構")
            return None, None
    
    def save_to_excel(self, fields: list, data: list, start_date: str, end_date: str) -> str:
        """
        將資料儲存為Excel格式
        
        Args:
            fields: 欄位名稱列表
            data: 資料列表
            start_date: 開始日期
            end_date: 結束日期
            
        Returns:
            Excel檔案名稱
        """
        if not fields or not data:
            print("❌ 無資料可儲存")
            return None
        
        # 創建DataFrame
        df = pd.DataFrame(data, columns=fields)
        
        print(f"\n📈 DataFrame 資訊:")
        print(f"  形狀: {df.shape}")
        print(f"  欄位數: {len(df.columns)}")
        
        # 顯示前幾行
        print(f"\n📋 前 3 行資料預覽:")
        print(df.head(3).to_string(index=False))
        
        # 生成檔案名稱
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        start_clean = start_date.replace('/', '')
        end_clean = end_date.replace('/', '')
        excel_file = f'證交所除息資料_{start_clean}_{end_clean}_{timestamp}.xlsx'
        
        try:
            # 儲存為Excel
            with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
                # 主要資料工作表
                df.to_excel(writer, sheet_name='除息資料', index=False)
                
                # 摘要資訊工作表
                summary_data = {
                    '項目': [
                        '查詢期間',
                        '資料筆數',
                        '欄位數量',
                        '產生時間',
                        '資料來源'
                    ],
                    '內容': [
                        f"{start_date} ~ {end_date}",
                        len(df),
                        len(df.columns),
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "台灣證券交易所"
                    ]
                }
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='摘要資訊', index=False)
                
                # 欄位說明工作表
                fields_data = {
                    '序號': range(1, len(fields) + 1),
                    '欄位名稱': fields,
                    '資料類型': [str(df[field].dtype) for field in fields],
                    '非空值數量': [df[field].count() for field in fields]
                }
                fields_df = pd.DataFrame(fields_data)
                fields_df.to_excel(writer, sheet_name='欄位說明', index=False)
            
            print(f"\n✅ Excel檔案已儲存: {excel_file}")
            print(f"📊 包含 {len(df)} 筆資料，{len(df.columns)} 個欄位")
            
            # 顯示統計資訊
            print(f"\n📈 資料統計:")
            print(f"  總記錄數: {len(df):,}")
            print(f"  工作表數: 3 (除息資料、摘要資訊、欄位說明)")
            
            return excel_file
            
        except Exception as e:
            print(f"❌ 儲存Excel失敗: {e}")
            return None
    
    def run(self, start_date: str = "114/06/16", end_date: str = "114/07/16"):
        """
        執行完整的資料獲取和儲存流程
        
        Args:
            start_date: 開始日期 (民國年格式)
            end_date: 結束日期 (民國年格式)
        """
        print("🏦 台灣證券交易所除息資料獲取器")
        print("=" * 60)
        print(f"🕐 執行時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 1. 獲取JSON資料
        json_data = self.fetch_dividend_data(start_date, end_date)
        if json_data is None:
            print("❌ 無法獲取資料，程式結束")
            return
        
        # 2. 分析JSON結構
        fields, data = self.analyze_json_structure(json_data)
        if fields is None or data is None:
            print("❌ 無法解析資料結構，程式結束")
            return
        
        # 3. 儲存為Excel
        excel_file = self.save_to_excel(fields, data, start_date, end_date)
        if excel_file:
            print(f"\n🎉 處理完成!")
            print(f"📁 Excel檔案: {excel_file}")
        else:
            print("❌ 儲存失敗")


def main():
    """主程序"""
    fetcher = TSEDividendFetcher()
    
    # 使用範例中的日期範圍
    fetcher.run("114/06/16", "114/07/16")


if __name__ == "__main__":
    main()
