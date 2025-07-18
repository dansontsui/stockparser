#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配息資料庫查看器
簡單的工具來查看和分析配息資料庫
"""

import pandas as pd
import os
from datetime import datetime


def view_dividend_database():
    """查看配息資料庫"""
    db_file = "dividend_database.xlsx"
    
    if not os.path.exists(db_file):
        print("❌ 配息資料庫不存在")
        print("💡 請先執行 daily_dividend_checker.py 來建立資料庫")
        return
    
    try:
        df = pd.read_excel(db_file, sheet_name="配息記錄")
    except Exception as e:
        print(f"❌ 讀取配息資料庫失敗: {e}")
        return
    
    if df.empty:
        print("📦 配息資料庫為空")
        return
    
    print("💰 配息資料庫內容")
    print("=" * 80)
    print(f"📊 總記錄數: {len(df)} 筆")
    print(f"📈 涉及股票: {df['股票代碼'].nunique()} 檔")
    print(f"📅 涉及月份: {df['年月'].nunique()} 個月")
    print(f"💰 總配息收益: {df['總配息收益'].sum():.2f} 元")
    print()
    
    # 按年月分組顯示
    for year_month in sorted(df['年月'].unique()):
        month_data = df[df['年月'] == year_month]
        month_total = month_data['總配息收益'].sum()
        
        print(f"📅 {year_month} (共 {len(month_data)} 檔股票，總收益: {month_total:.2f} 元)")
        print("-" * 60)
        
        for _, row in month_data.iterrows():
            print(f"  {row['股票代碼']} ({row['股票名稱']})")
            print(f"    持股: {row['持有股數']:,} 股")
            print(f"    配息: {row['每股配息']} 元/股")
            print(f"    收益: {row['總配息收益']:.2f} 元")
            print(f"    日期: {row['除息日期']}")
            if row['備註']:
                print(f"    備註: {row['備註']}")
            print()


def export_dividend_summary():
    """匯出配息摘要"""
    db_file = "dividend_database.xlsx"
    
    if not os.path.exists(db_file):
        print("❌ 配息資料庫不存在")
        return
    
    try:
        df = pd.read_excel(db_file, sheet_name="配息記錄")
    except Exception as e:
        print(f"❌ 讀取配息資料庫失敗: {e}")
        return
    
    if df.empty:
        print("📦 配息資料庫為空")
        return
    
    # 按年月統計
    monthly_summary = df.groupby('年月').agg({
        '股票代碼': 'count',
        '總配息收益': 'sum'
    }).rename(columns={
        '股票代碼': '配息股票數',
        '總配息收益': '月總收益'
    })
    
    # 按股票統計
    stock_summary = df.groupby(['股票代碼', '股票名稱']).agg({
        '年月': 'count',
        '總配息收益': 'sum'
    }).rename(columns={
        '年月': '配息次數',
        '總配息收益': '累計收益'
    })
    
    # 匯出檔案
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    summary_file = f"配息摘要_{timestamp}.xlsx"
    
    with pd.ExcelWriter(summary_file) as writer:
        monthly_summary.to_excel(writer, sheet_name="月度摘要")
        stock_summary.to_excel(writer, sheet_name="股票摘要")
        df.to_excel(writer, sheet_name="完整記錄", index=False)
    
    print(f"📄 配息摘要已匯出: {summary_file}")
    print(f"📊 包含 {len(monthly_summary)} 個月的配息記錄")
    print(f"📈 涉及 {len(stock_summary)} 檔股票")
    print(f"💰 總配息收益: {df['總配息收益'].sum():.2f} 元")


def main():
    """主程序"""
    print("💰 配息資料庫查看器")
    print("=" * 50)
    
    while True:
        print("\n請選擇操作:")
        print("1. 查看配息資料庫")
        print("2. 匯出配息摘要")
        print("3. 退出")
        
        choice = input("\n請輸入選項 (1-3): ").strip()
        
        if choice == "1":
            view_dividend_database()
        
        elif choice == "2":
            export_dividend_summary()
        
        elif choice == "3":
            print("👋 感謝使用配息資料庫查看器！")
            break
        
        else:
            print("❌ 無效的選項，請重新選擇")


if __name__ == "__main__":
    main()
