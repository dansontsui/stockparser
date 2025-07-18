#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試配息統計功能
"""

import pandas as pd
import os
from datetime import datetime
from dividend_statistics import DividendStatistics

def create_sample_dividend_data():
    """建立範例配息資料"""
    print("📊 建立範例配息資料...")
    
    # 範例配息記錄
    sample_data = [
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
        },
        {
            '年月': '2024-03',
            '股票代碼': '0056',
            '股票名稱': '元大高股息',
            '每股配息': 0.90,
            '持有股數': 10000,
            '總配息收益': 9000.0,
            '配息日期': '2024-03-15',
            '備註': '測試資料'
        },
        {
            '年月': '2024-04',
            '股票代碼': '00934',
            '股票名稱': '中信成長高股息',
            '每股配息': 0.25,
            '持有股數': 20000,
            '總配息收益': 5000.0,
            '配息日期': '2024-04-10',
            '備註': '測試資料'
        },
        {
            '年月': '2024-05',
            '股票代碼': '00878',
            '股票名稱': '國泰高股息',
            '每股配息': 0.35,
            '持有股數': 15000,
            '總配息收益': 5250.0,
            '配息日期': '2024-05-20',
            '備註': '測試資料'
        },
        {
            '年月': '2024-06',
            '股票代碼': '0056',
            '股票名稱': '元大高股息',
            '每股配息': 0.88,
            '持有股數': 12000,
            '總配息收益': 10560.0,
            '配息日期': '2024-06-15',
            '備註': '測試資料'
        },
        {
            '年月': '2023-12',
            '股票代碼': '0056',
            '股票名稱': '元大高股息',
            '每股配息': 0.82,
            '持有股數': 8000,
            '總配息收益': 6560.0,
            '配息日期': '2023-12-15',
            '備註': '測試資料'
        },
        {
            '年月': '2023-11',
            '股票代碼': '00878',
            '股票名稱': '國泰高股息',
            '每股配息': 0.30,
            '持有股數': 12000,
            '總配息收益': 3600.0,
            '配息日期': '2023-11-20',
            '備註': '測試資料'
        }
    ]
    
    df = pd.DataFrame(sample_data)
    
    # 保存到 dividend_database.xlsx
    database_file = 'dividend_database.xlsx'
    
    with pd.ExcelWriter(database_file, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='配息記錄', index=False)
    
    print(f"✅ 範例配息資料已保存到: {database_file}")
    print(f"📊 總記錄數: {len(df)} 筆")
    print(f"💰 總配息金額: {df['總配息收益'].sum():.2f} 元")
    
    return True

def test_dividend_statistics():
    """測試配息統計功能"""
    print("🧪 測試配息統計功能")
    print("=" * 50)
    
    # 檢查是否有配息資料
    database_file = 'dividend_database.xlsx'
    
    if not os.path.exists(database_file):
        print("📊 沒有配息資料，建立範例資料...")
        create_sample_dividend_data()
    else:
        print(f"✅ 找到配息資料庫: {database_file}")
    
    # 執行統計分析
    print(f"\n📊 執行配息統計分析...")
    stats = DividendStatistics(database_file)
    success = stats.generate_all_statistics()
    
    if success:
        print(f"\n🎉 配息統計測試成功！")
        print(f"📁 請打開 {database_file} 查看以下工作表:")
        print("   • 配息記錄 - 原始配息資料")
        print("   • 年度統計 - 按年份統計配息金額")
        print("   • 月度統計 - 按年月統計配息金額")
        print("   • 股票統計 - 按股票統計配息金額")
        print("   • 進階統計 - 各種統計指標")
        
        # 顯示統計結果預覽
        try:
            yearly_df = pd.read_excel(database_file, sheet_name='年度統計')
            monthly_df = pd.read_excel(database_file, sheet_name='月度統計')
            stock_df = pd.read_excel(database_file, sheet_name='股票統計')
            
            print(f"\n📈 統計結果預覽:")
            print(f"   年度統計: {len(yearly_df)} 年")
            print(f"   月度統計: {len(monthly_df)} 個月")
            print(f"   股票統計: {len(stock_df)} 檔股票")
            
            if not yearly_df.empty:
                total_amount = yearly_df['總配息金額'].sum()
                best_year = yearly_df.loc[yearly_df['總配息金額'].idxmax()]
                print(f"   總配息金額: {total_amount:,.2f} 元")
                print(f"   最佳年份: {best_year['年份']} ({best_year['總配息金額']:,.2f} 元)")
            
        except Exception as e:
            print(f"⚠️  預覽統計結果失敗: {e}")
        
    else:
        print(f"\n❌ 配息統計測試失敗！")
    
    return success

def main():
    """主函數"""
    print("🧪 配息統計功能測試")
    print("=" * 40)
    
    choice = input("選擇操作:\n1. 建立範例資料\n2. 測試統計功能\n3. 兩者都執行\n請選擇 (1-3): ").strip()
    
    if choice == "1":
        create_sample_dividend_data()
    elif choice == "2":
        test_dividend_statistics()
    elif choice == "3":
        create_sample_dividend_data()
        print(f"\n" + "="*50)
        test_dividend_statistics()
    else:
        print("❌ 無效選擇")

if __name__ == "__main__":
    main()
