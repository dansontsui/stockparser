#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡單版本：獲取00878股價並存入SQLite
"""

import sqlite3
from datetime import datetime, timedelta
import stkfunction as sf

def init_database():
    """初始化資料庫"""
    try:
        with sqlite3.connect('stock_data.db') as conn:
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
            return True
    except Exception as e:
        print(f"資料庫初始化失敗: {e}")
        return False

def get_00878_data():
    """獲取00878資料"""
    stock_code = '00878'
    
    # 計算日期範圍 (近30天)
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=30)
    
    print(f"開始獲取 {stock_code} 從 {start_date} 到 {end_date} 的資料")
    
    try:
        # 使用現有函數獲取資料
        sf.crawl_stock_data(stock_code, start_date, end_date)
        print("資料獲取完成")
        return True
    except Exception as e:
        print(f"獲取資料失敗: {e}")
        return False

def import_csv_to_sqlite():
    """將CSV檔案匯入SQLite"""
    import os
    import glob
    
    stock_code = '00878'
    csv_pattern = f"{stock_code}/*.csv"
    csv_files = glob.glob(csv_pattern)
    
    if not csv_files:
        print("未找到CSV檔案")
        return 0
    
    total_saved = 0
    
    try:
        with sqlite3.connect('stock_data.db') as conn:
            cursor = conn.cursor()
            
            for csv_file in csv_files:
                print(f"處理檔案: {csv_file}")
                
                try:
                    with open(csv_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                    
                    if len(lines) < 2:
                        continue
                    
                    # 跳過標題行，處理資料行
                    for line in lines[1:]:
                        try:
                            # 移除引號並分割
                            values = line.strip().replace('"', '').split(',')
                            if len(values) < 9:
                                continue
                            
                            # 轉換民國年日期為西元年
                            date_parts = values[0].split('/')
                            if len(date_parts) == 3:
                                year = int(date_parts[0]) + 1911
                                month = int(date_parts[1])
                                day = int(date_parts[2])
                                date_str = f"{year:04d}-{month:02d}-{day:02d}"
                            else:
                                continue
                            
                            # 清理數值資料
                            def clean_number(val):
                                try:
                                    if val == '--' or val == '':
                                        return 0
                                    return int(val.replace(',', ''))
                                except:
                                    return 0
                            
                            def clean_price(val):
                                try:
                                    if val == '--' or val == '':
                                        return 0.0
                                    return float(val.replace(',', ''))
                                except:
                                    return 0.0
                            
                            trade_volume = clean_number(values[1])
                            trade_value = clean_number(values[2])
                            open_price = clean_price(values[3])
                            high_price = clean_price(values[4])
                            low_price = clean_price(values[5])
                            close_price = clean_price(values[6])
                            price_change = clean_price(values[7])
                            transaction_count = clean_number(values[8])
                            
                            created_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            
                            # 插入資料
                            cursor.execute('''
                                INSERT OR REPLACE INTO stock_prices_00878 
                                (date, stock_code, stock_name, trade_volume, trade_value, 
                                 open_price, high_price, low_price, close_price, price_change, 
                                 transaction_count, created_date)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            ''', (date_str, stock_code, '國泰永續高股息', trade_volume, trade_value,
                                  open_price, high_price, low_price, close_price, price_change,
                                  transaction_count, created_date))
                            
                            total_saved += 1
                            
                        except Exception as e:
                            print(f"處理資料行失敗: {line.strip()}, 錯誤: {e}")
                            continue
                    
                    print(f"處理完成: {csv_file}")
                    
                except Exception as e:
                    print(f"處理檔案失敗: {csv_file}, 錯誤: {e}")
                    continue
            
            conn.commit()
            print(f"總共存入 {total_saved} 筆資料")
            return total_saved
            
    except Exception as e:
        print(f"匯入SQLite失敗: {e}")
        return 0

def view_data(limit=10):
    """查看資料"""
    try:
        with sqlite3.connect('stock_data.db') as conn:
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
                print(f"\n=== 00878 最近 {len(rows)} 天股價資料 ===")
                print("日期        開盤    最高    最低    收盤    成交量      漲跌")
                print("-" * 65)
                
                for row in rows:
                    date, open_p, high_p, low_p, close_p, volume, change = row
                    print(f"{date} {open_p:6.2f} {high_p:6.2f} {low_p:6.2f} {close_p:6.2f} {volume:8d} {change:+6.2f}")
            else:
                print("資料庫中無資料")
                
    except Exception as e:
        print(f"查詢資料失敗: {e}")

def get_data_count():
    """取得資料筆數"""
    try:
        with sqlite3.connect('stock_data.db') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM stock_prices_00878')
            count = cursor.fetchone()[0]
            print(f"資料庫中共有 {count} 筆 00878 資料")
            return count
    except Exception as e:
        print(f"查詢資料筆數失敗: {e}")
        return 0

def main():
    """主程式"""
    print("=== 00878股價獲取程式 (簡單版) ===")
    
    # 1. 初始化資料庫
    if not init_database():
        return
    
    # 2. 檢查現有資料
    get_data_count()
    
    # 3. 獲取新資料
    if get_00878_data():
        # 4. 匯入SQLite
        saved_count = import_csv_to_sqlite()
        
        if saved_count > 0:
            # 5. 顯示結果
            view_data(10)
            get_data_count()
        else:
            print("未能匯入任何資料")
    else:
        print("資料獲取失敗")

if __name__ == "__main__":
    main()
