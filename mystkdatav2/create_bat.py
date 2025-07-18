#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
創建正確編碼的批次檔案
"""

def create_batch_files():
    """創建多個版本的批次檔案"""

    # 版本1: 簡單版本 (英文)
    simple_content = """@echo off
cd /d "%~dp0"
python daily_dividend_checker.py --auto
pause
"""

    # 版本2: 完整版本 (英文)
    full_content = """@echo off
chcp 65001 > nul
echo Daily Dividend Checker
echo ========================
echo Time: %date% %time%
echo.

cd /d "%~dp0"

echo Starting dividend check...
python daily_dividend_checker.py --auto

echo.
echo Check completed!
echo Please check: dividend_database.xlsx
echo CSV report also generated
echo.
pause
"""

    # 版本3: 超簡單版本
    minimal_content = """@echo off
python daily_dividend_checker.py --auto
pause
"""

    files_to_create = [
        ('daily_dividend_check_simple.bat', simple_content, '簡單版本'),
        ('daily_dividend_check.bat', full_content, '完整版本'),
        ('daily_dividend_check_minimal.bat', minimal_content, '超簡單版本')
    ]

    for filename, content, description in files_to_create:
        try:
            # 嘗試使用不同編碼
            encodings = ['cp950', 'gbk', 'utf-8', 'ansi', None]

            for encoding in encodings:
                try:
                    if encoding:
                        with open(filename, 'w', encoding=encoding, newline='\r\n') as f:
                            f.write(content)
                        print(f"✅ {description} 創建成功: {filename} (編碼: {encoding})")
                    else:
                        with open(filename, 'w', newline='\r\n') as f:
                            f.write(content)
                        print(f"✅ {description} 創建成功: {filename} (預設編碼)")
                    break
                except Exception as e:
                    if encoding == encodings[-1]:  # 最後一個編碼也失敗
                        print(f"❌ {description} 創建失敗: {filename} - {e}")
                    continue

        except Exception as e:
            print(f"❌ 創建 {filename} 時發生錯誤: {e}")

    print("\n📝 使用說明:")
    print("1. 先試試 daily_dividend_check_minimal.bat (最簡單)")
    print("2. 如果不行，試試 daily_dividend_check_simple.bat")
    print("3. 最後試試 daily_dividend_check.bat (完整版)")
    print("\n💡 如果都不行，請直接在命令提示字元執行:")
    print("   python daily_dividend_checker.py --auto")

if __name__ == "__main__":
    create_batch_files()
