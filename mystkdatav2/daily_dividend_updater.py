#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日自動配息更新器
"""

import schedule
import time
import os
import sys
from datetime import datetime, timedelta
from historical_dividend_tracker import HistoricalDividendTracker
import pandas as pd

class DailyDividendUpdater:
    """每日配息更新器"""
    
    def __init__(self):
        self.tracker = HistoricalDividendTracker()
        self.log_file = 'daily_dividend_update.log'
    
    def log_message(self, message: str):
        """記錄日誌訊息"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] {message}"
        print(log_entry)
        
        # 寫入日誌檔案
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry + '\n')
        except Exception as e:
            print(f"❌ 寫入日誌失敗: {e}")
    
    def daily_update(self):
        """執行每日配息更新"""
        self.log_message("🚀 開始每日配息更新")
        self.log_message("=" * 50)
        
        try:
            # 獲取當前年份
            current_year = datetime.now().year
            
            # 檢查是否需要更新當年資料
            self.log_message(f"🔍 檢查 {current_year} 年配息資料更新")
            
            # 執行當年配息追蹤
            success = self.tracker.track_dividend_by_actual_dates(current_year)
            
            if success:
                self.log_message(f"✅ {current_year} 年配息更新成功")
                
                # 檢查更新結果
                self.check_update_results()
                
            else:
                self.log_message(f"⚠️  {current_year} 年配息更新無新記錄")
            
            # 如果是年初，也檢查去年的資料
            if datetime.now().month <= 2:  # 1-2月檢查去年資料
                last_year = current_year - 1
                self.log_message(f"🔍 年初檢查 {last_year} 年配息資料")
                
                last_year_success = self.tracker.track_dividend_by_actual_dates(last_year)
                if last_year_success:
                    self.log_message(f"✅ {last_year} 年配息更新成功")
                else:
                    self.log_message(f"⚠️  {last_year} 年配息更新無新記錄")
            
            # 自動生成統計報表
            self.generate_statistics()

            self.log_message("🎉 每日配息更新完成")

        except Exception as e:
            self.log_message(f"❌ 每日配息更新失敗: {e}")
            import traceback
            error_details = traceback.format_exc()
            self.log_message(f"錯誤詳情: {error_details}")
    
    def check_update_results(self):
        """檢查更新結果"""
        try:
            # 讀取配息資料庫
            if os.path.exists('dividend_database.xlsx'):
                df_dividend = pd.read_excel('dividend_database.xlsx', sheet_name='配息記錄')
                
                # 檢查今日是否有新增記錄
                today = datetime.now().strftime('%Y-%m-%d')
                today_records = df_dividend[df_dividend['檢查日期'].str.contains(today, na=False)]
                
                if not today_records.empty:
                    self.log_message(f"📊 今日新增配息記錄: {len(today_records)} 筆")
                    
                    # 按股票統計
                    stock_stats = today_records.groupby('股票代碼').agg({
                        '股票名稱': 'first',
                        '總配息收益': 'sum'
                    })
                    
                    for stock_code, row in stock_stats.iterrows():
                        stock_name = row['股票名稱']
                        total_dividend = row['總配息收益']
                        self.log_message(f"  💰 {stock_code} ({stock_name}): {total_dividend:.2f} 元")
                else:
                    self.log_message("📊 今日無新增配息記錄")
                    
        except Exception as e:
            self.log_message(f"❌ 檢查更新結果失敗: {e}")

    def generate_statistics(self):
        """生成配息統計報表"""
        try:
            self.log_message("📊 開始生成配息統計報表...")

            # 檢查配息資料庫是否存在
            if os.path.exists("dividend_database.xlsx"):
                from dividend_statistics import DividendStatistics

                stats = DividendStatistics()
                success = stats.generate_all_statistics()

                if success:
                    self.log_message("✅ 配息統計報表生成完成")
                    self.log_message("📁 統計工作表已更新到 dividend_database.xlsx")
                else:
                    self.log_message("⚠️  配息統計報表生成失敗")
            else:
                self.log_message("⚠️  配息資料庫不存在，跳過統計報表生成")

        except ImportError as e:
            self.log_message(f"❌ 統計模組導入失敗: {e}")
        except Exception as e:
            self.log_message(f"❌ 生成統計報表失敗: {e}")

    def setup_daily_schedule(self, update_time: str = "09:00"):
        """設定每日自動更新排程
        
        Args:
            update_time: 更新時間，格式 "HH:MM"，預設 09:00
        """
        self.log_message(f"⏰ 設定每日 {update_time} 自動更新配息資料")
        
        # 設定每日排程
        schedule.every().day.at(update_time).do(self.daily_update)
        
        self.log_message("✅ 每日自動更新排程已設定")
    
    def run_scheduler(self):
        """執行排程器"""
        self.log_message("🔄 啟動每日配息更新排程器")
        self.log_message("按 Ctrl+C 停止排程器")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # 每分鐘檢查一次
                
        except KeyboardInterrupt:
            self.log_message("⏹️  使用者停止排程器")
        except Exception as e:
            self.log_message(f"❌ 排程器執行錯誤: {e}")
    
    def manual_update(self):
        """手動執行更新"""
        self.log_message("🔧 手動執行配息更新")
        self.daily_update()

        # 顯示統計摘要
        self.show_statistics_summary()

    def show_statistics_summary(self):
        """顯示統計摘要"""
        try:
            if os.path.exists("dividend_database.xlsx"):
                import pandas as pd

                # 讀取配息記錄
                df = pd.read_excel("dividend_database.xlsx", sheet_name="配息記錄")

                if not df.empty:
                    total_dividend = df['總配息收益'].sum()
                    total_records = len(df)
                    unique_stocks = df['股票代碼'].nunique()

                    self.log_message("📊 配息統計摘要:")
                    self.log_message(f"   總配息收益: {total_dividend:,.2f} 元")
                    self.log_message(f"   配息記錄: {total_records} 筆")
                    self.log_message(f"   投資股票: {unique_stocks} 檔")

                    # 檢查是否有統計工作表
                    excel_file = pd.ExcelFile("dividend_database.xlsx")
                    stats_sheets = [s for s in excel_file.sheet_names if s != '配息記錄']

                    if stats_sheets:
                        self.log_message(f"   統計工作表: {', '.join(stats_sheets)}")
                    else:
                        self.log_message("   ⚠️  沒有統計工作表")

                else:
                    self.log_message("📊 配息資料庫為空")
            else:
                self.log_message("📊 配息資料庫不存在")

        except Exception as e:
            self.log_message(f"❌ 顯示統計摘要失敗: {e}")

    def show_recent_logs(self, days: int = 7):
        """顯示最近的日誌記錄
        
        Args:
            days: 顯示最近幾天的日誌，預設7天
        """
        if not os.path.exists(self.log_file):
            print("❌ 日誌檔案不存在")
            return
        
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            print(f"📋 最近 {days} 天的更新日誌:")
            print("=" * 50)
            
            with open(self.log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            recent_lines = []
            for line in lines:
                try:
                    # 提取時間戳記
                    if line.startswith('['):
                        timestamp_str = line[1:20]  # [YYYY-MM-DD HH:MM:SS]
                        log_time = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                        
                        if log_time >= cutoff_date:
                            recent_lines.append(line.strip())
                except:
                    continue
            
            if recent_lines:
                for line in recent_lines[-50:]:  # 最多顯示50行
                    print(line)
            else:
                print(f"❌ 最近 {days} 天沒有日誌記錄")
                
        except Exception as e:
            print(f"❌ 讀取日誌失敗: {e}")
    
    def interactive_menu(self):
        """互動式選單"""
        while True:
            print(f"\n{'='*60}")
            print("⏰ 每日配息自動更新器")
            print("=" * 60)
            print("1. 手動執行配息更新")
            print("2. 啟動每日自動更新 (09:00)")
            print("3. 啟動每日自動更新 (自訂時間)")
            print("4. 查看最近7天日誌")
            print("5. 查看最近30天日誌")
            print("6. 退出")
            
            choice = input("\n請選擇功能 (1-6): ").strip()
            
            if choice == '1':
                self.manual_update()
            
            elif choice == '2':
                self.setup_daily_schedule("09:00")
                self.run_scheduler()
            
            elif choice == '3':
                update_time = input("請輸入更新時間 (格式: HH:MM，例如 09:30): ").strip()
                try:
                    # 驗證時間格式
                    datetime.strptime(update_time, '%H:%M')
                    self.setup_daily_schedule(update_time)
                    self.run_scheduler()
                except ValueError:
                    print("❌ 時間格式錯誤，請使用 HH:MM 格式")
            
            elif choice == '4':
                self.show_recent_logs(7)
            
            elif choice == '5':
                self.show_recent_logs(30)
            
            elif choice == '6':
                print("👋 再見！")
                break
            
            else:
                print("❌ 無效的選擇，請重新輸入")

if __name__ == "__main__":
    updater = DailyDividendUpdater()
    
    # 檢查命令列參數
    if len(sys.argv) > 1:
        if sys.argv[1] == '--manual':
            updater.manual_update()
        elif sys.argv[1] == '--schedule':
            update_time = sys.argv[2] if len(sys.argv) > 2 else "09:00"
            updater.setup_daily_schedule(update_time)
            updater.run_scheduler()
        elif sys.argv[1] == '--logs':
            days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
            updater.show_recent_logs(days)
        else:
            print("❌ 無效的參數")
            print("使用方法:")
            print("  python daily_dividend_updater.py --manual     # 手動更新")
            print("  python daily_dividend_updater.py --schedule   # 啟動排程 (09:00)")
            print("  python daily_dividend_updater.py --schedule 10:30  # 啟動排程 (10:30)")
            print("  python daily_dividend_updater.py --logs      # 查看日誌")
    else:
        updater.interactive_menu()
