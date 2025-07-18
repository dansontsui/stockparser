#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配息統計分析工具
針對 dividend_database.xlsx 做各種統計分析
"""

import pandas as pd
import os
from datetime import datetime

class DividendStatistics:
    """配息統計分析器"""
    
    def __init__(self, database_file='dividend_database.xlsx'):
        self.database_file = database_file
    
    def load_dividend_data(self):
        """載入配息資料"""
        if not os.path.exists(self.database_file):
            print(f"❌ 配息資料庫不存在: {self.database_file}")
            return None
        
        try:
            df = pd.read_excel(self.database_file, sheet_name='配息記錄')
            print(f"📊 載入配息記錄: {len(df)} 筆")
            return df
        except Exception as e:
            print(f"❌ 載入配息資料失敗: {e}")
            return None
    
    def create_yearly_statistics(self, df):
        """建立年度統計"""
        print("📈 建立年度統計...")
        
        # 從年月欄位提取年份
        df_copy = df.copy()
        df_copy['年份'] = df_copy['年月'].str[:4]
        
        # 按年份統計
        yearly_stats = df_copy.groupby('年份').agg({
            '總配息收益': ['sum', 'count', 'mean'],
            '股票代碼': 'nunique'
        }).round(2)
        
        # 重新命名欄位
        yearly_stats.columns = ['總配息金額', '配息次數', '平均配息金額', '股票檔數']
        yearly_stats = yearly_stats.reset_index()
        
        # 計算累計金額
        yearly_stats['累計配息金額'] = yearly_stats['總配息金額'].cumsum()
        
        # 計算年度成長率
        yearly_stats['年度成長率(%)'] = yearly_stats['總配息金額'].pct_change() * 100
        yearly_stats['年度成長率(%)'] = yearly_stats['年度成長率(%)'].round(2)
        
        print(f"✅ 年度統計完成: {len(yearly_stats)} 年")
        return yearly_stats
    
    def create_monthly_statistics(self, df):
        """建立月度統計"""
        print("📅 建立月度統計...")
        
        # 按年月統計
        monthly_stats = df.groupby('年月').agg({
            '總配息收益': ['sum', 'count', 'mean'],
            '股票代碼': 'nunique'
        }).round(2)
        
        # 重新命名欄位
        monthly_stats.columns = ['總配息金額', '配息次數', '平均配息金額', '股票檔數']
        monthly_stats = monthly_stats.reset_index()
        
        # 分離年份和月份
        monthly_stats['年份'] = monthly_stats['年月'].str[:4]
        monthly_stats['月份'] = monthly_stats['年月'].str[5:7]
        
        # 計算累計金額
        monthly_stats['累計配息金額'] = monthly_stats['總配息金額'].cumsum()
        
        # 計算月度成長率
        monthly_stats['月度成長率(%)'] = monthly_stats['總配息金額'].pct_change() * 100
        monthly_stats['月度成長率(%)'] = monthly_stats['月度成長率(%)'].round(2)
        
        print(f"✅ 月度統計完成: {len(monthly_stats)} 個月")
        return monthly_stats
    
    def create_stock_statistics(self, df):
        """建立股票統計"""
        print("📊 建立股票統計...")
        
        # 按股票統計
        stock_stats = df.groupby(['股票代碼', '股票名稱']).agg({
            '總配息收益': ['sum', 'count', 'mean', 'max', 'min'],
            '每股配息': ['mean', 'max', 'min'],
            '持有股數': 'mean',
            '年月': ['min', 'max']
        }).round(2)
        
        # 重新命名欄位
        stock_stats.columns = [
            '總配息金額', '配息次數', '平均配息金額', '最高配息金額', '最低配息金額',
            '平均每股配息', '最高每股配息', '最低每股配息',
            '平均持有股數',
            '首次配息年月', '最後配息年月'
        ]
        stock_stats = stock_stats.reset_index()
        
        # 計算配息期間
        stock_stats['配息期間(月)'] = (
            pd.to_datetime(stock_stats['最後配息年月'] + '-01') - 
            pd.to_datetime(stock_stats['首次配息年月'] + '-01')
        ).dt.days / 30.44  # 平均每月天數
        stock_stats['配息期間(月)'] = stock_stats['配息期間(月)'].round(1)
        
        # 計算年化配息率（粗略估算）
        stock_stats['年化配息次數'] = stock_stats['配息次數'] / (stock_stats['配息期間(月)'] / 12)
        stock_stats['年化配息次數'] = stock_stats['年化配息次數'].round(1)
        
        # 按總配息金額排序
        stock_stats = stock_stats.sort_values('總配息金額', ascending=False)
        
        print(f"✅ 股票統計完成: {len(stock_stats)} 檔股票")
        return stock_stats
    
    def create_advanced_statistics(self, df):
        """建立進階統計"""
        print("🔍 建立進階統計...")
        
        advanced_stats = []
        
        # 總體統計
        total_dividend = df['總配息收益'].sum()
        total_records = len(df)
        unique_stocks = df['股票代碼'].nunique()
        date_range = f"{df['年月'].min()} ~ {df['年月'].max()}"
        
        advanced_stats.append({
            '統計項目': '總配息收益',
            '數值': f"{total_dividend:,.2f} 元",
            '說明': '所有配息記錄的總和'
        })
        
        advanced_stats.append({
            '統計項目': '配息記錄總數',
            '數值': f"{total_records:,} 筆",
            '說明': '所有配息記錄的數量'
        })
        
        advanced_stats.append({
            '統計項目': '投資股票檔數',
            '數值': f"{unique_stocks} 檔",
            '說明': '有配息記錄的股票數量'
        })
        
        advanced_stats.append({
            '統計項目': '配息期間',
            '數值': date_range,
            '說明': '從最早到最晚的配息記錄'
        })
        
        # 平均統計
        avg_dividend_per_record = df['總配息收益'].mean()
        avg_dividend_per_stock = df.groupby('股票代碼')['總配息收益'].sum().mean()
        
        advanced_stats.append({
            '統計項目': '平均每筆配息',
            '數值': f"{avg_dividend_per_record:.2f} 元",
            '說明': '每筆配息記錄的平均金額'
        })
        
        advanced_stats.append({
            '統計項目': '平均每檔股票配息',
            '數值': f"{avg_dividend_per_stock:.2f} 元",
            '說明': '每檔股票的平均總配息'
        })
        
        # 最高/最低統計
        max_dividend_record = df.loc[df['總配息收益'].idxmax()]
        min_dividend_record = df.loc[df['總配息收益'].idxmin()]
        
        advanced_stats.append({
            '統計項目': '最高單筆配息',
            '數值': f"{max_dividend_record['總配息收益']:.2f} 元",
            '說明': f"{max_dividend_record['股票代碼']} ({max_dividend_record['年月']})"
        })
        
        advanced_stats.append({
            '統計項目': '最低單筆配息',
            '數值': f"{min_dividend_record['總配息收益']:.2f} 元",
            '說明': f"{min_dividend_record['股票代碼']} ({min_dividend_record['年月']})"
        })
        
        # 配息頻率統計
        freq_stats = df.groupby('股票代碼').size().describe()
        
        advanced_stats.append({
            '統計項目': '平均配息頻率',
            '數值': f"{freq_stats['mean']:.1f} 次/檔",
            '說明': '每檔股票的平均配息次數'
        })
        
        advanced_stats.append({
            '統計項目': '最高配息頻率',
            '數值': f"{freq_stats['max']:.0f} 次",
            '說明': '單一股票的最多配息次數'
        })
        
        df_advanced = pd.DataFrame(advanced_stats)
        
        print(f"✅ 進階統計完成: {len(df_advanced)} 項指標")
        return df_advanced
    
    def generate_all_statistics(self):
        """生成所有統計報表"""
        print("📊 生成配息統計報表")
        print("=" * 50)
        
        # 載入資料
        df = self.load_dividend_data()
        if df is None or df.empty:
            print("❌ 沒有配息資料可以統計")
            return False
        
        try:
            # 生成各種統計
            yearly_stats = self.create_yearly_statistics(df)
            monthly_stats = self.create_monthly_statistics(df)
            stock_stats = self.create_stock_statistics(df)
            advanced_stats = self.create_advanced_statistics(df)
            
            # 保存到Excel檔案
            print(f"\n💾 保存統計報表到 {self.database_file}...")
            
            # 讀取現有的配息記錄
            existing_sheets = {}
            try:
                excel_file = pd.ExcelFile(self.database_file)
                for sheet_name in excel_file.sheet_names:
                    if sheet_name == '配息記錄':
                        existing_sheets[sheet_name] = df
                    else:
                        existing_sheets[sheet_name] = pd.read_excel(self.database_file, sheet_name=sheet_name)
            except:
                existing_sheets['配息記錄'] = df
            
            # 添加統計工作表
            existing_sheets['年度統計'] = yearly_stats
            existing_sheets['月度統計'] = monthly_stats
            existing_sheets['股票統計'] = stock_stats
            existing_sheets['進階統計'] = advanced_stats
            
            # 保存所有工作表
            with pd.ExcelWriter(self.database_file, engine='openpyxl') as writer:
                for sheet_name, sheet_df in existing_sheets.items():
                    sheet_df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            print("✅ 統計報表已保存")
            
            # 顯示統計摘要
            self.show_statistics_summary(yearly_stats, monthly_stats, stock_stats)
            
            return True
            
        except Exception as e:
            print(f"❌ 生成統計報表失敗: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def show_statistics_summary(self, yearly_stats, monthly_stats, stock_stats):
        """顯示統計摘要"""
        print(f"\n📊 統計報表摘要")
        print("=" * 50)
        
        print(f"📈 年度統計:")
        if not yearly_stats.empty:
            total_years = len(yearly_stats)
            total_amount = yearly_stats['總配息金額'].sum()
            best_year = yearly_stats.loc[yearly_stats['總配息金額'].idxmax()]
            print(f"   統計年份: {total_years} 年")
            print(f"   總配息金額: {total_amount:,.2f} 元")
            print(f"   最佳年份: {best_year['年份']} ({best_year['總配息金額']:,.2f} 元)")
        
        print(f"\n📅 月度統計:")
        if not monthly_stats.empty:
            total_months = len(monthly_stats)
            best_month = monthly_stats.loc[monthly_stats['總配息金額'].idxmax()]
            avg_monthly = monthly_stats['總配息金額'].mean()
            print(f"   統計月份: {total_months} 個月")
            print(f"   平均月配息: {avg_monthly:,.2f} 元")
            print(f"   最佳月份: {best_month['年月']} ({best_month['總配息金額']:,.2f} 元)")
        
        print(f"\n📊 股票統計:")
        if not stock_stats.empty:
            total_stocks = len(stock_stats)
            top_stock = stock_stats.iloc[0]
            print(f"   統計股票: {total_stocks} 檔")
            print(f"   最佳股票: {top_stock['股票代碼']} ({top_stock['股票名稱']})")
            print(f"   最高配息: {top_stock['總配息金額']:,.2f} 元")
        
        print(f"\n💡 統計工作表已添加到 {self.database_file}:")
        print("   • 年度統計 - 按年份統計配息金額")
        print("   • 月度統計 - 按年月統計配息金額") 
        print("   • 股票統計 - 按股票統計配息金額")
        print("   • 進階統計 - 各種統計指標")

def main():
    """主函數"""
    print("📊 配息統計分析工具")
    print("=" * 40)
    
    # 檢查配息資料庫是否存在
    database_file = 'dividend_database.xlsx'
    if not os.path.exists(database_file):
        print(f"❌ 配息資料庫不存在: {database_file}")
        print("💡 請先執行 historical_dividend_tracker.py 生成配息資料")
        return
    
    # 建立統計分析器
    stats = DividendStatistics(database_file)
    
    # 生成統計報表
    success = stats.generate_all_statistics()
    
    if success:
        print(f"\n🎉 配息統計分析完成！")
        print(f"📁 請打開 {database_file} 查看統計結果")
    else:
        print(f"\n❌ 配息統計分析失敗！")

if __name__ == "__main__":
    main()
