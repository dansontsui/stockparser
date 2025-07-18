#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配息資料管理工具
"""

from historical_dividend_tracker import HistoricalDividendTracker
import pandas as pd
import os
from datetime import datetime

class DividendDataManager:
    """配息資料管理器"""
    
    def __init__(self):
        self.tracker = HistoricalDividendTracker()
    
    def download_and_save_year_data(self, year: int):
        """下載並保存指定年份的配息資料"""
        print(f"📥 下載並保存 {year} 年的配息資料")
        print("=" * 50)
        
        try:
            # 下載資料（會自動保存）
            tpex_data, tse_data = self.tracker.fetch_dividend_data_for_year(year)
            
            print(f"✅ {year} 年配息資料下載完成")
            return True
            
        except Exception as e:
            print(f"❌ {year} 年配息資料下載失敗: {e}")
            return False
    
    def download_range_data(self, start_year: int, end_year: int = None):
        """下載範圍年份的配息資料"""
        if end_year is None:
            end_year = datetime.now().year
        
        print(f"📥 下載 {start_year} ~ {end_year} 年的配息資料")
        print("=" * 60)
        
        successful_years = 0
        total_years = end_year - start_year + 1
        
        for year in range(start_year, end_year + 1):
            print(f"\n📅 處理第 {year - start_year + 1}/{total_years} 年: {year}")
            
            if self.download_and_save_year_data(year):
                successful_years += 1
        
        print(f"\n🎉 範圍下載完成！")
        print(f"📊 成功下載: {successful_years}/{total_years} 年")
        
        return successful_years > 0
    
    def list_saved_data_files(self):
        """列出已保存的配息資料檔案"""
        print("📁 已保存的配息資料檔案")
        print("=" * 50)
        
        # 查找所有相關檔案
        patterns = [
            ('Excel配息資料', 'dividend_records_*.xlsx')
        ]
        
        import glob
        
        for category, pattern in patterns:
            files = glob.glob(pattern)
            if files:
                print(f"\n📊 {category}:")
                for file in sorted(files):
                    file_size = os.path.getsize(file)
                    mod_time = datetime.fromtimestamp(os.path.getmtime(file))
                    print(f"  {file} ({file_size:,} bytes, {mod_time.strftime('%Y-%m-%d %H:%M')})")
            else:
                print(f"\n❌ {category}: 無檔案")
    
    def analyze_saved_data(self, year: int):
        """分析已保存的配息資料"""
        print(f"📊 分析 {year} 年的配息資料")
        print("=" * 50)
        
        try:
            # 讀取Excel資料
            filename = f'dividend_records_{year}.xlsx'
            if not os.path.exists(filename):
                print(f"❌ 檔案不存在: {filename}")
                return

            df = pd.read_excel(filename, sheet_name=f'{year}年配息記錄')
            
            if df.empty:
                print("❌ 資料為空")
                return
            
            print(f"✅ 總記錄數: {len(df)} 筆")
            
            # 按資料來源統計
            if '資料來源' in df.columns:
                print(f"\n📈 資料來源統計:")
                source_stats = df['資料來源'].value_counts()
                for source, count in source_stats.items():
                    print(f"  {source}: {count} 筆")
            
            # 按月份統計
            if '配息日期' in df.columns:
                try:
                    df['配息月份'] = pd.to_datetime(df['配息日期']).dt.strftime('%Y-%m')
                    print(f"\n📅 月份統計:")
                    monthly_stats = df['配息月份'].value_counts().sort_index()
                    for month, count in monthly_stats.items():
                        print(f"  {month}: {count} 筆")
                except:
                    print("⚠️  無法解析配息日期")
            
            # 檢查重要股票
            important_stocks = ['0056', '00937B', '0050', '006208']
            if '股票代碼' in df.columns:
                print(f"\n🎯 重要股票檢查:")
                for stock_code in important_stocks:
                    stock_records = df[df['股票代碼'] == stock_code]
                    if not stock_records.empty:
                        stock_name = stock_records.iloc[0].get('股票名稱', 'N/A')
                        print(f"  {stock_code} ({stock_name}): {len(stock_records)} 筆")
                    else:
                        print(f"  {stock_code}: 無記錄")
            
        except Exception as e:
            print(f"❌ 分析失敗: {e}")
    
    def interactive_menu(self):
        """互動式選單"""
        while True:
            print(f"\n{'='*60}")
            print("📊 配息資料管理工具")
            print("=" * 60)
            print("1. 下載單一年份配息資料")
            print("2. 下載範圍年份配息資料")
            print("3. 列出已保存的檔案")
            print("4. 分析已保存的資料")
            print("5. 退出")
            
            choice = input("\n請選擇功能 (1-5): ").strip()
            
            if choice == '1':
                try:
                    year = int(input("請輸入年份 (例如: 2025): "))
                    self.download_and_save_year_data(year)
                except ValueError:
                    print("❌ 請輸入有效的年份")
            
            elif choice == '2':
                try:
                    start_year = int(input("請輸入起始年份 (例如: 2024): "))
                    end_year_input = input("請輸入結束年份 (留空為當前年份): ").strip()
                    end_year = int(end_year_input) if end_year_input else None
                    self.download_range_data(start_year, end_year)
                except ValueError:
                    print("❌ 請輸入有效的年份")
            
            elif choice == '3':
                self.list_saved_data_files()
            
            elif choice == '4':
                try:
                    year = int(input("請輸入要分析的年份 (例如: 2025): "))
                    self.analyze_saved_data(year)
                except ValueError:
                    print("❌ 請輸入有效的年份")
            
            elif choice == '5':
                print("👋 再見！")
                break
            
            else:
                print("❌ 無效的選擇，請重新輸入")

if __name__ == "__main__":
    manager = DividendDataManager()
    manager.interactive_menu()
