#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速統計功能測試
"""

import pandas as pd
import os

def quick_test():
    """快速測試統計功能"""
    print("🧪 快速統計功能測試")
    print("=" * 40)
    
    # 1. 檢查配息資料庫
    database_file = 'dividend_database.xlsx'
    
    if not os.path.exists(database_file):
        print(f"❌ 配息資料庫不存在: {database_file}")
        print("💡 建立測試資料...")
        
        # 建立測試資料
        test_data = [
            {
                '年月': '2024-01',
                '股票代碼': '0056',
                '股票名稱': '元大高股息',
                '每股配息': 0.85,
                '持有股數': 10000,
                '總配息收益': 8500.0,
                '配息日期': '2024-01-15',
                '備註': '測試資料'
            },
            {
                '年月': '2024-02',
                '股票代碼': '00878',
                '股票名稱': '國泰高股息',
                '每股配息': 0.32,
                '持有股數': 15000,
                '總配息收益': 4800.0,
                '配息日期': '2024-02-20',
                '備註': '測試資料'
            }
        ]
        
        df = pd.DataFrame(test_data)
        with pd.ExcelWriter(database_file, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='配息記錄', index=False)
        
        print(f"✅ 測試資料已建立")
    
    # 2. 測試統計功能
    print(f"\n📊 測試統計功能...")
    
    try:
        from dividend_statistics import DividendStatistics
        
        stats = DividendStatistics(database_file)
        success = stats.generate_all_statistics()
        
        if success:
            print("✅ 統計功能測試成功！")
            
            # 檢查生成的工作表
            excel_file = pd.ExcelFile(database_file)
            print(f"📋 生成的工作表: {excel_file.sheet_names}")
            
            return True
        else:
            print("❌ 統計功能測試失敗！")
            return False
            
    except Exception as e:
        print(f"❌ 統計功能測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    quick_test()
