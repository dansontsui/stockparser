#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試統計功能整合
"""

import pandas as pd
import os
from datetime import datetime

def test_statistics_integration():
    """測試統計功能整合"""
    print("🧪 測試統計功能整合")
    print("=" * 50)
    
    # 1. 檢查是否有配息資料庫
    database_file = 'dividend_database.xlsx'
    
    if not os.path.exists(database_file):
        print(f"❌ 配息資料庫不存在: {database_file}")
        print("💡 請先執行 historical_dividend_tracker.py 生成配息資料")
        return False
    
    print(f"✅ 找到配息資料庫: {database_file}")
    
    # 2. 檢查配息記錄
    try:
        df = pd.read_excel(database_file, sheet_name='配息記錄')
        print(f"📊 配息記錄: {len(df)} 筆")
        
        if df.empty:
            print("⚠️  配息記錄為空，無法生成統計")
            return False
            
    except Exception as e:
        print(f"❌ 讀取配息記錄失敗: {e}")
        return False
    
    # 3. 測試統計功能
    print(f"\n📊 測試統計功能...")
    
    try:
        from dividend_statistics import DividendStatistics
        
        stats = DividendStatistics(database_file)
        success = stats.generate_all_statistics()
        
        if success:
            print("✅ 統計功能測試成功！")
            
            # 檢查生成的工作表
            excel_file = pd.ExcelFile(database_file)
            expected_sheets = ['配息記錄', '年度統計', '月度統計', '股票統計', '進階統計']
            
            print(f"\n📋 檢查工作表:")
            for sheet in expected_sheets:
                if sheet in excel_file.sheet_names:
                    try:
                        sheet_df = pd.read_excel(database_file, sheet_name=sheet)
                        print(f"   ✅ {sheet}: {len(sheet_df)} 筆記錄")
                    except Exception as e:
                        print(f"   ❌ {sheet}: 讀取失敗 - {e}")
                else:
                    print(f"   ❌ {sheet}: 工作表不存在")
            
            return True
            
        else:
            print("❌ 統計功能測試失敗！")
            return False
            
    except ImportError as e:
        print(f"❌ 無法導入統計模組: {e}")
        return False
    except Exception as e:
        print(f"❌ 統計功能測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def simulate_dividend_tracker_call():
    """模擬配息追蹤器的調用"""
    print("🎯 模擬配息追蹤器調用統計功能")
    print("=" * 50)
    
    # 模擬成功的配息追蹤
    success = True  # 假設配息追蹤成功
    
    if success:
        print(f"📊 生成配息統計報表...")
        try:
            from dividend_statistics import DividendStatistics
            stats = DividendStatistics()
            stats_success = stats.generate_all_statistics()
            
            if stats_success:
                print("✅ 配息統計報表生成完成！")
                print("📁 請打開 dividend_database.xlsx 查看統計工作表")
                return True
            else:
                print("⚠️  統計報表生成失敗")
                return False
                
        except Exception as e:
            print(f"⚠️  統計報表生成失敗: {e}")
            print("💡 您可以手動執行: python dividend_statistics.py")
            return False
    else:
        print("⚠️  配息追蹤未成功，跳過統計報表生成")
        return False

def main():
    """主函數"""
    print("🧪 統計功能整合測試")
    print("=" * 40)
    
    print("選擇測試:")
    print("1. 測試統計功能")
    print("2. 模擬追蹤器調用")
    print("3. 兩者都測試")
    
    choice = input("\n請選擇 (1-3): ").strip()
    
    if choice == "1":
        success = test_statistics_integration()
    elif choice == "2":
        success = simulate_dividend_tracker_call()
    elif choice == "3":
        success1 = test_statistics_integration()
        print(f"\n" + "="*50)
        success2 = simulate_dividend_tracker_call()
        success = success1 and success2
    else:
        print("❌ 無效選擇")
        return
    
    if success:
        print(f"\n🎉 測試成功！統計功能整合正常")
    else:
        print(f"\n❌ 測試失敗！請檢查統計功能")

if __name__ == "__main__":
    main()
