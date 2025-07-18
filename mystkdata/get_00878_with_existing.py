#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用現有stkfunction模組獲取00878股價並存入SQLite
"""

import sqlite3
from datetime import datetime, timedelta
import stkfunction as sf
import os

class Stock00878WithExisting:
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
    
    def fetch_recent_data(self, days=30):
        """使用現有函數獲取近期資料"""
        print(f"開始獲取 {self.stock_code} 近 {days} 天的股價資料")
        
        # 計算日期範圍
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        print(f"日期範圍: {start_date} 到 {end_date}")
        
        try:
            # 使用現有的crawl_stock_data函數
            sf.crawl_stock_data(self.stock_code, start_date, end_date)
            
            # 讀取生成的CSV檔案並存入SQLite
            self._import_csv_to_sqlite()
            
        except Exception as e:
            print(f"獲取資料失敗: {e}")
    
    def _import_csv_to_sqlite(self):
        """將CSV檔案匯入SQLite"""
        import glob

        csv_pattern = f"{self.stock_code}/*.csv"
        csv_files = glob.glob(csv_pattern)

        if not csv_files:
            print("未找到CSV檔案")
            return

        total_saved = 0

        try:
            with sqlite3.connect(self.db_file) as conn:
                for csv_file in csv_files:
                    print(f"處理檔案: {csv_file}")

                    try:
                        # 手動讀取CSV檔案
                        with open(csv_file, 'r', encoding='utf-8') as f:
                            lines = f.readlines()

                        if len(lines) < 2:
                            continue

                        # 解析標題行
                        header = lines[0].strip().split(',')

                        # 處理資料
                        processed_data = []

                        for line in lines[1:]:
                            try:
                                values = line.strip().split(',')
                                if len(values) < 9:
                                    continue

                                # 轉換民國年日期為西元年
                                date_str = self._convert_roc_to_ad(values[0])

                                # 清理數值資料
                                trade_volume = self._clean_number(values[1])
                                trade_value = self._clean_number(values[2])
                                open_price = self._clean_price(values[3])
                                high_price = self._clean_price(values[4])
                                low_price = self._clean_price(values[5])
                                close_price = self._clean_price(values[6])
                                price_change = self._clean_price(values[7])
                                transaction_count = self._clean_number(values[8])

                                created_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                                processed_data.append((
                                    date_str, self.stock_code, self.stock_name,
                                    trade_volume, trade_value, open_price, high_price,
                                    low_price, close_price, price_change,
                                    transaction_count, created_date
                                ))

                            except Exception as e:
                                print(f"處理資料行失敗: {e}")
                                continue

                        # 批次插入資料
                        cursor = conn.cursor()
                        cursor.executemany('''
                            INSERT OR REPLACE INTO stock_prices_00878
                            (date, stock_code, stock_name, trade_volume, trade_value,
                             open_price, high_price, low_price, close_price, price_change,
                             transaction_count, created_date)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', processed_data)

                        saved_count = len(processed_data)
                        total_saved += saved_count
                        print(f"從 {csv_file} 存入 {saved_count} 筆資料")

                    except Exception as e:
                        print(f"處理檔案 {csv_file} 失敗: {e}")
                        continue

                conn.commit()
                print(f"總共存入 {total_saved} 筆資料")

        except Exception as e:
            print(f"匯入SQLite失敗: {e}")
    
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
    
    def _clean_number(self, value):
        """清理數值資料"""
        try:
            if value == '--' or value == '' or value is None:
                return 0
            return int(str(value).replace(',', '').replace('"', ''))
        except:
            return 0

    def _clean_price(self, value):
        """清理價格資料"""
        try:
            if value == '--' or value == '' or value is None:
                return 0.0
            return float(str(value).replace(',', '').replace('"', ''))
        except:
            return 0.0
    
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
        print("=== 使用現有模組獲取00878股價 ===")
        
        fetcher = Stock00878WithExisting()
        
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
