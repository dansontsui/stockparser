#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡化版00878股價獲取程式 (使用內建套件)
"""

import sqlite3
import urllib.request
import urllib.parse
import json
import time
from datetime import datetime, timedelta

class Simple00878Fetcher:
    def __init__(self, db_file='stock_data.db'):
        self.db_file = db_file
        self.stock_code = '00878'
        self.stock_name = '國泰永續高股息'
        self._init_database()
    
    def _init_database(self):
        """初始化資料庫"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS stock_prices_00878 (
                        date TEXT,
                        stock_code TEXT,
                        stock_name TEXT,
                        trade_volume INTEGER,
                        trade_value INTEGER,
                        open_price REAL,
                        high_price REAL,
                        low_price REAL,
                        close_price REAL,
                        price_change REAL,
                        transaction_count INTEGER,
                        created_date TEXT,
                        PRIMARY KEY (date, stock_code)
                    )
                ''')
                print("資料庫初始化完成")
        except Exception as e:
            print(f"資料庫初始化失敗: {e}")
            raise
    
    def _fetch_data(self, year_month):
        """使用urllib獲取股價資料"""
        url = f'https://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&date={year_month}&stockNo={self.stock_code}'
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        
        try:
            print(f"正在獲取 {year_month} 的資料...")
            
            req = urllib.request.Request(url, headers=headers)
            
            with urllib.request.urlopen(req, timeout=30) as response:
                data = json.loads(response.read().decode('utf-8'))
                
                if data.get('stat') == 'OK' and data.get('data'):
                    print(f"成功獲取 {len(data['data'])} 筆資料")
                    return data
                else:
                    print(f"API回應無資料: {data.get('stat', 'Unknown')}")
                    return None
                    
        except Exception as e:
            print(f"獲取資料失敗: {e}")
            return None
    
    def _convert_roc_to_ad(self, roc_date):
        """轉換民國年日期為西元年日期"""
        try:
            parts = roc_date.split('/')
            year = int(parts[0]) + 1911
            month = int(parts[1])
            day = int(parts[2])
            return f"{year:04d}-{month:02d}-{day:02d}"
        except:
            return roc_date
    
    def _process_and_save_data(self, data):
        """處理並存入資料"""
        if not data or not data.get('data'):
            return 0
        
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                saved_count = 0
                
                for row in data['data']:
                    try:
                        # 解析資料
                        date_str = self._convert_roc_to_ad(row[0])  # 日期
                        trade_volume = int(row[1].replace(',', '')) if row[1] != '--' else 0  # 成交股數
                        trade_value = int(row[2].replace(',', '')) if row[2] != '--' else 0   # 成交金額
                        open_price = float(row[3]) if row[3] != '--' else 0.0    # 開盤價
                        high_price = float(row[4]) if row[4] != '--' else 0.0    # 最高價
                        low_price = float(row[5]) if row[5] != '--' else 0.0     # 最低價
                        close_price = float(row[6]) if row[6] != '--' else 0.0   # 收盤價
                        price_change = float(row[7]) if row[7] != '--' else 0.0  # 漲跌價差
                        transaction_count = int(row[8].replace(',', '')) if row[8] != '--' else 0  # 成交筆數
                        
                        created_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        
                        # 插入資料 (使用 INSERT OR REPLACE 避免重複)
                        cursor.execute('''
                            INSERT OR REPLACE INTO stock_prices_00878 
                            (date, stock_code, stock_name, trade_volume, trade_value, 
                             open_price, high_price, low_price, close_price, price_change, 
                             transaction_count, created_date)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (date_str, self.stock_code, self.stock_name, trade_volume, trade_value,
                              open_price, high_price, low_price, close_price, price_change,
                              transaction_count, created_date))
                        
                        saved_count += 1
                        
                    except Exception as e:
                        print(f"處理資料行失敗: {row}, 錯誤: {e}")
                        continue
                
                conn.commit()
                print(f"成功存入 {saved_count} 筆資料")
                return saved_count
                
        except Exception as e:
            print(f"存入資料庫失敗: {e}")
            return 0
    
    def fetch_recent_data(self, days=30):
        """獲取近期資料"""
        print(f"開始獲取 {self.stock_code} 近 {days} 天的股價資料")
        
        # 計算需要查詢的年月
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        year_months = []
        current = start_date.replace(day=1)
        
        while current <= end_date:
            year_months.append(current.strftime('%Y%m01'))
            if current.month == 12:
                current = current.replace(year=current.year + 1, month=1)
            else:
                current = current.replace(month=current.month + 1)
        
        total_saved = 0
        
        for year_month in year_months:
            data = self._fetch_data(year_month)
            if data:
                saved = self._process_and_save_data(data)
                total_saved += saved
                time.sleep(2)  # 延遲避免過於頻繁請求
        
        print(f"總共存入 {total_saved} 筆資料")
        return total_saved
    
    def view_recent_data(self, limit=10):
        """查看最近的資料"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT date, open_price, high_price, low_price, close_price, 
                           trade_volume, price_change
                    FROM stock_prices_00878 
                    ORDER BY date DESC 
                    LIMIT ?
                ''', (limit,))
                
                rows = cursor.fetchall()
                
                if rows:
                    print(f"\n=== {self.stock_code} 最近 {len(rows)} 天股價資料 ===")
                    print("日期        開盤    最高    最低    收盤    成交量      漲跌")
                    print("-" * 65)
                    
                    for row in rows:
                        date, open_p, high_p, low_p, close_p, volume, change = row
                        print(f"{date} {open_p:6.2f} {high_p:6.2f} {low_p:6.2f} {close_p:6.2f} {volume:8d} {change:+6.2f}")
                else:
                    print("資料庫中無資料")
                    
        except Exception as e:
            print(f"查詢資料失敗: {e}")
    
    def get_data_count(self):
        """取得資料筆數"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM stock_prices_00878')
                count = cursor.fetchone()[0]
                print(f"資料庫中共有 {count} 筆 {self.stock_code} 資料")
                return count
        except Exception as e:
            print(f"查詢資料筆數失敗: {e}")
            return 0

def main():
    """主程式"""
    try:
        print("=== 00878股價獲取程式 ===")
        
        fetcher = Simple00878Fetcher()
        
        # 檢查現有資料
        fetcher.get_data_count()
        
        # 獲取近30天資料
        fetcher.fetch_recent_data(days=30)
        
        # 顯示最近10天資料
        fetcher.view_recent_data(limit=10)
        
        # 最終統計
        fetcher.get_data_count()
        
    except Exception as e:
        print(f"程式執行失敗: {e}")

if __name__ == "__main__":
    main()
