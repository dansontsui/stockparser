#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試所有版本的00878股價獲取程式
"""

import os
import sqlite3
import subprocess
import sys
from datetime import datetime

def test_python_environment():
    """測試Python環境"""
    print("=== 測試Python環境 ===")
    print(f"Python版本: {sys.version}")
    print(f"當前目錄: {os.getcwd()}")
    
    # 測試標準庫
    try:
        import sqlite3
        import urllib.request
        import json
        print("✓ 標準庫可用")
    except ImportError as e:
        print(f"✗ 標準庫問題: {e}")
        return False
    
    # 測試可選套件
    optional_packages = ['requests', 'pandas']
    for package in optional_packages:
        try:
            __import__(package)
            print(f"✓ {package} 可用")
        except ImportError:
            print(f"- {package} 未安裝 (可選)")
    
    return True

def test_existing_modules():
    """測試現有模組"""
    print("\n=== 測試現有模組 ===")
    
    try:
        import stkfunction as sf
        print("✓ stkfunction 模組可用")
        
        # 測試函數
        if hasattr(sf, 'crawl_stock_data'):
            print("✓ crawl_stock_data 函數存在")
        else:
            print("✗ crawl_stock_data 函數不存在")
            
        return True
    except ImportError as e:
        print(f"✗ stkfunction 模組問題: {e}")
        return False

def test_database():
    """測試資料庫功能"""
    print("\n=== 測試資料庫功能 ===")
    
    try:
        # 測試連接
        with sqlite3.connect('test_db.db') as conn:
            cursor = conn.cursor()
            
            # 建立測試表格
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS test_table (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    value REAL
                )
            ''')
            
            # 插入測試資料
            cursor.execute('INSERT INTO test_table (name, value) VALUES (?, ?)', 
                          ('test', 123.45))
            
            # 查詢測試資料
            cursor.execute('SELECT * FROM test_table')
            rows = cursor.fetchall()
            
            if rows:
                print("✓ SQLite資料庫功能正常")
                print(f"  測試資料: {rows[0]}")
            else:
                print("✗ SQLite查詢無結果")
                return False
                
        # 清理測試檔案
        if os.path.exists('test_db.db'):
            os.remove('test_db.db')
            
        return True
        
    except Exception as e:
        print(f"✗ 資料庫測試失敗: {e}")
        return False

def test_network():
    """測試網路連接"""
    print("\n=== 測試網路連接 ===")
    
    try:
        import urllib.request
        
        # 測試台灣證券交易所連接
        url = 'https://www.twse.com.tw'
        req = urllib.request.Request(url)
        
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.getcode() == 200:
                print("✓ 台灣證券交易所網站可連接")
                return True
            else:
                print(f"✗ 網站回應碼: {response.getcode()}")
                return False
                
    except Exception as e:
        print(f"✗ 網路連接測試失敗: {e}")
        return False

def check_files():
    """檢查程式檔案"""
    print("\n=== 檢查程式檔案 ===")
    
    files_to_check = [
        'get_00878_stock_price.py',
        'simple_00878.py', 
        'get_00878_with_existing.py',
        'get_00878_simple.py',
        'run_00878.bat',
        'stkfunction.py'
    ]
    
    all_exist = True
    
    for filename in files_to_check:
        if os.path.exists(filename):
            size = os.path.getsize(filename)
            print(f"✓ {filename} ({size} bytes)")
        else:
            print(f"✗ {filename} 不存在")
            all_exist = False
    
    return all_exist

def check_database_structure():
    """檢查現有資料庫結構"""
    print("\n=== 檢查現有資料庫 ===")
    
    db_file = 'stock_data.db'
    
    if not os.path.exists(db_file):
        print(f"- {db_file} 不存在 (將會自動建立)")
        return True
    
    try:
        with sqlite3.connect(db_file) as conn:
            cursor = conn.cursor()
            
            # 取得所有表格
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            print(f"✓ 資料庫存在，包含 {len(tables)} 個表格")
            
            for table in tables:
                table_name = table[0]
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                print(f"  - {table_name}: {count} 筆資料")
            
            return True
            
    except Exception as e:
        print(f"✗ 檢查資料庫失敗: {e}")
        return False

def generate_report():
    """產生測試報告"""
    print("\n" + "="*50)
    print("測試報告")
    print("="*50)
    
    tests = [
        ("Python環境", test_python_environment),
        ("現有模組", test_existing_modules),
        ("資料庫功能", test_database),
        ("網路連接", test_network),
        ("程式檔案", check_files),
        ("資料庫結構", check_database_structure)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"測試 {test_name} 時發生錯誤: {e}")
            results.append((test_name, False))
    
    print("\n" + "="*50)
    print("測試結果摘要")
    print("="*50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✓ 通過" if result else "✗ 失敗"
        print(f"{test_name:12} : {status}")
        if result:
            passed += 1
    
    print(f"\n總計: {passed}/{total} 項測試通過")
    
    if passed == total:
        print("\n🎉 所有測試通過！可以執行00878股價獲取程式")
        print("\n建議執行順序:")
        print("1. python get_00878_simple.py (推薦)")
        print("2. python simple_00878.py (備選)")
        print("3. 雙擊 run_00878.bat (圖形介面)")
    else:
        print(f"\n⚠️  有 {total-passed} 項測試失敗，請檢查環境設定")
        
        if not any(name == "現有模組" and result for name, result in results):
            print("- 建議使用 simple_00878.py (不依賴現有模組)")
        
        if not any(name == "網路連接" and result for name, result in results):
            print("- 請檢查網路連接")

def main():
    """主程式"""
    print("00878股價獲取程式 - 環境測試工具")
    print(f"測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    generate_report()

if __name__ == "__main__":
    main()
