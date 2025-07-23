#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修正批次檔編碼問題
解決 echo 顯示亂碼的問題
"""

import os
import glob

def fix_bat_file_encoding(bat_file):
    """修正單個批次檔的編碼問題"""
    print(f"🔧 修正批次檔: {bat_file}")
    
    try:
        # 讀取原始內容
        with open(bat_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # 檢查是否已經有 chcp 命令
        if 'chcp 65001' in content:
            print(f"   ✅ 已經包含編碼設定")
            return True
        
        # 在 @echo off 後添加 chcp 65001
        lines = content.split('\n')
        new_lines = []
        
        for i, line in enumerate(lines):
            new_lines.append(line)
            
            # 在 @echo off 後添加編碼設定
            if line.strip().lower() == '@echo off':
                new_lines.append('chcp 65001 >nul')
        
        # 寫回檔案
        new_content = '\n'.join(new_lines)
        
        with open(bat_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"   ✅ 編碼修正完成")
        return True
        
    except Exception as e:
        print(f"   ❌ 修正失敗: {e}")
        return False

def fix_all_bat_files():
    """修正所有批次檔的編碼問題"""
    print("🔧 批次檔編碼修正工具")
    print("=" * 50)
    
    # 尋找所有 .bat 檔案
    bat_files = glob.glob("*.bat")
    
    if not bat_files:
        print("❌ 沒有找到 .bat 檔案")
        return
    
    print(f"📁 找到 {len(bat_files)} 個批次檔:")
    for bat_file in bat_files:
        print(f"   • {bat_file}")
    
    print(f"\n🔧 開始修正...")
    
    success_count = 0
    for bat_file in bat_files:
        if fix_bat_file_encoding(bat_file):
            success_count += 1
    
    print(f"\n📊 修正結果:")
    print(f"   成功: {success_count}/{len(bat_files)} 個檔案")
    
    if success_count == len(bat_files):
        print("✅ 所有批次檔編碼修正完成！")
        print("💡 現在執行 .bat 檔案應該不會有亂碼問題")
    else:
        print("⚠️  部分檔案修正失敗，請手動檢查")

def create_test_bat():
    """建立測試批次檔"""
    test_content = """@echo off
chcp 65001 >nul
echo 🧪 批次檔編碼測試
echo ==================
echo 📊 中文字符測試
echo 💡 表情符號測試
echo ✅ 特殊符號測試
echo.
echo 如果您看到正確的符號，表示編碼修正成功！
echo 如果看到亂碼，請檢查終端機編碼設定
echo.
pause
"""
    
    with open('test_encoding.bat', 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    print("✅ 測試批次檔已建立: test_encoding.bat")
    print("💡 請執行此檔案測試編碼是否正確")

def main():
    """主函數"""
    print("🔧 批次檔亂碼修正工具")
    print("=" * 40)
    
    print("選擇操作:")
    print("1. 修正所有 .bat 檔案編碼")
    print("2. 建立編碼測試檔案")
    print("3. 兩者都執行")
    
    choice = input("\n請選擇 (1-3): ").strip()
    
    if choice == "1":
        fix_all_bat_files()
    elif choice == "2":
        create_test_bat()
    elif choice == "3":
        fix_all_bat_files()
        print("\n" + "="*50)
        create_test_bat()
    else:
        print("❌ 無效選擇")
        return
    
    print(f"\n💡 解決亂碼的方法:")
    print("1. 在批次檔開頭添加 'chcp 65001 >nul'")
    print("2. 確保檔案以 UTF-8 編碼保存")
    print("3. 使用支援 UTF-8 的終端機")

if __name__ == "__main__":
    main()
