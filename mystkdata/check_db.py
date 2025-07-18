#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
檢查現有SQLite資料庫
"""

import sqlite3
import os

def check_database():
    """檢查資料庫狀態"""
    db_file = 'stock_data.db'
    
    if not os.path.exists(db_file):
        print(f"資料庫檔案 {db_file} 不存在")
        return
    
    try:
        with sqlite3.connect(db_file) as conn:
            cursor = conn.cursor()
            
            # 取得所有表格
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            print(f"=== 資料庫 {db_file} 資訊 ===")
            print(f"表格數量: {len(tables)}")
            
            for table in tables:
                table_name = table[0]
                print(f"\n表格: {table_name}")
                
                # 取得表格結構
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                
                print("欄位結構:")
                for col in columns:
                    print(f"  {col[1]} ({col[2]})")
                
                # 取得資料筆數
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                print(f"資料筆數: {count}")
                
                # 如果有資料，顯示前幾筆
                if count > 0:
                    cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
                    rows = cursor.fetchall()
                    print("範例資料:")
                    for i, row in enumerate(rows, 1):
                        print(f"  第{i}筆: {row}")
    
    except Exception as e:
        print(f"檢查資料庫失敗: {e}")

def create_test_table():
    """建立測試表格"""
    try:
        with sqlite3.connect('stock_data.db') as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS test_00878 (
                    id INTEGER PRIMARY KEY,
                    message TEXT,
                    created_date TEXT
                )
            ''')
            
            # 插入測試資料
            from datetime import datetime
            test_data = [
                ("測試資料1", datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
                ("測試資料2", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            ]
            
            conn.executemany(
                "INSERT INTO test_00878 (message, created_date) VALUES (?, ?)",
                test_data
            )
            
            print("測試表格建立成功")
            
    except Exception as e:
        print(f"建立測試表格失敗: {e}")

if __name__ == "__main__":
    print("=== SQLite資料庫檢查工具 ===")
    check_database()
    
    print("\n=== 建立測試表格 ===")
    create_test_table()
    
    print("\n=== 重新檢查資料庫 ===")
    check_database()
