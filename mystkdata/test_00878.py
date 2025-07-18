#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試獲取00878股價資料
"""

import requests
import json
import time
from datetime import datetime

def test_api():
    """測試台灣證券交易所API"""
    stock_code = '00878'
    
    # 使用當前年月
    current_date = datetime.now()
    year_month = current_date.strftime('%Y%m01')
    
    url = f'https://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&date={year_month}&stockNo={stock_code}'
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    
    try:
        print(f"正在測試API: {url}")
        response = requests.get(url, headers=headers, timeout=30)
        print(f"HTTP狀態碼: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"API回應狀態: {data.get('stat', 'Unknown')}")
            
            if data.get('stat') == 'OK' and data.get('data'):
                print(f"成功獲取資料，共 {len(data['data'])} 筆")
                print("欄位名稱:", data.get('fields', []))
                
                # 顯示前3筆資料
                for i, row in enumerate(data['data'][:3]):
                    print(f"第{i+1}筆: {row}")
                
                return True
            else:
                print("API回應無資料")
                return False
        else:
            print(f"HTTP請求失敗: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"測試失敗: {e}")
        return False

def test_sqlite():
    """測試SQLite連接"""
    try:
        import sqlite3
        
        with sqlite3.connect('stock_data.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            print(f"資料庫中的表格: {[table[0] for table in tables]}")
            
            # 測試建立表格
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS test_stock_prices (
                    date TEXT,
                    stock_code TEXT,
                    close_price REAL,
                    PRIMARY KEY (date, stock_code)
                )
            ''')
            
            print("SQLite測試成功")
            return True
            
    except Exception as e:
        print(f"SQLite測試失敗: {e}")
        return False

def main():
    print("=== 00878股價獲取程式測試 ===")
    
    print("\n1. 測試SQLite連接...")
    sqlite_ok = test_sqlite()
    
    print("\n2. 測試API連接...")
    api_ok = test_api()
    
    print(f"\n=== 測試結果 ===")
    print(f"SQLite: {'✓' if sqlite_ok else '✗'}")
    print(f"API: {'✓' if api_ok else '✗'}")
    
    if sqlite_ok and api_ok:
        print("所有測試通過，可以執行完整程式")
    else:
        print("部分測試失敗，請檢查環境設定")

if __name__ == "__main__":
    main()
