#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
強健的庫存重新整理測試
"""

from inventory_reorganizer import InventoryReorganizer
import pandas as pd
import os

def test_robust_reorganizer():
    """測試強健的庫存重新整理"""
    print("🧪 測試強健的庫存重新整理")
    print("=" * 50)
    
    # 檢查庫存檔案
    inventory_file = 'stock_inventory.xlsx'
    
    if not os.path.exists(inventory_file):
        print(f"❌ 庫存檔案不存在: {inventory_file}")
        return
    
    try:
        print(f"📁 使用庫存檔案: {inventory_file}")
        
        # 1. 先檢查檔案結構
        print("\n🔍 檢查檔案結構...")
        excel_file = pd.ExcelFile(inventory_file)
        print(f"📋 工作表: {excel_file.sheet_names}")
        
        # 檢查交易歷史工作表
        if '交易歷史' in excel_file.sheet_names:
            df_transactions = pd.read_excel(inventory_file, sheet_name='交易歷史')
            print(f"📊 交易歷史記錄: {len(df_transactions)} 筆")
            print(f"📋 欄位: {list(df_transactions.columns)}")
            
            # 檢查資料類型
            print("\n📊 資料類型檢查:")
            for col in df_transactions.columns:
                dtype_counts = df_transactions[col].apply(lambda x: type(x).__name__).value_counts()
                print(f"  {col}: {dict(dtype_counts)}")
            
            # 檢查是否有空值
            print("\n📊 空值檢查:")
            null_counts = df_transactions.isnull().sum()
            for col, count in null_counts.items():
                if count > 0:
                    print(f"  {col}: {count} 個空值")
            
            # 檢查交易類型
            if '交易類型' in df_transactions.columns:
                transaction_types = df_transactions['交易類型'].value_counts()
                print(f"\n📊 交易類型統計: {dict(transaction_types)}")
            
            # 檢查股票代碼
            if '股票代碼' in df_transactions.columns:
                stock_codes = df_transactions['股票代碼'].unique()
                print(f"\n📊 股票代碼: {sorted([str(code) for code in stock_codes])}")
        
        # 2. 建立重新整理器並測試
        print(f"\n🔄 建立庫存重新整理器...")
        reorganizer = InventoryReorganizer(inventory_file)
        
        # 3. 測試載入交易歷史
        print("\n📥 測試載入交易歷史...")
        df_transactions = reorganizer.load_transaction_history()
        
        if df_transactions is not None:
            print(f"✅ 交易歷史載入成功: {len(df_transactions)} 筆")
            
            # 顯示清理後的資料統計
            print("\n📊 清理後的資料統計:")
            print(f"  記錄數: {len(df_transactions)}")
            print(f"  股票檔數: {df_transactions['股票代碼'].nunique()}")
            print(f"  日期範圍: {df_transactions['交易日期'].min()} ~ {df_transactions['交易日期'].max()}")
            
            # 4. 測試計算當前持有量
            print("\n🔢 測試計算當前持有量...")
            current_holdings = reorganizer.calculate_current_holdings(df_transactions)
            
            if current_holdings:
                print(f"✅ 當前持有量計算成功: {len(current_holdings)} 檔股票")
                
                print("\n📊 持有量明細:")
                for stock_code, data in current_holdings.items():
                    avg_cost = data['total_cost'] / data['quantity'] if data['quantity'] > 0 else 0
                    print(f"  {stock_code} ({data['stock_name']}): {data['quantity']} 股, 平均成本 {avg_cost:.2f} 元, 總成本 {data['total_cost']:.2f} 元")
                
                # 5. 測試建立工作表
                print(f"\n📋 測試建立工作表...")
                df_inventory = reorganizer.create_current_inventory_sheet(current_holdings)
                df_summary = reorganizer.create_transaction_summary(df_transactions)
                
                print(f"✅ 當前庫存工作表: {len(df_inventory)} 筆記錄")
                print(f"✅ 交易摘要工作表: {len(df_summary)} 筆記錄")
                
                # 檢查異常
                if not df_summary.empty:
                    negative_holdings = df_summary[df_summary['淨持有股數'] < 0]
                    if not negative_holdings.empty:
                        print(f"⚠️  發現 {len(negative_holdings)} 檔股票淨持有量為負數:")
                        for _, row in negative_holdings.iterrows():
                            print(f"    {row['股票代碼']} ({row['股票名稱']}): {row['淨持有股數']} 股")
                    else:
                        print("✅ 沒有發現淨持有量為負數的股票")
                
                # 6. 詢問是否執行實際重新整理
                print(f"\n{'='*50}")
                print("🎯 所有測試通過！")
                
                choice = input("是否要執行實際的庫存重新整理？(y/N): ").strip().lower()
                
                if choice in ['y', 'yes']:
                    print("\n🔄 執行實際庫存重新整理...")
                    success = reorganizer.reorganize_inventory()
                    
                    if success:
                        print("✅ 庫存重新整理成功！")
                        
                        # 檢查結果
                        print("\n📊 檢查重新整理結果...")
                        try:
                            excel_file_new = pd.ExcelFile(inventory_file)
                            print(f"📋 新的工作表: {excel_file_new.sheet_names}")
                            
                            if '當前庫存' in excel_file_new.sheet_names:
                                df_new_inventory = pd.read_excel(inventory_file, sheet_name='當前庫存')
                                print(f"✅ 當前庫存工作表: {len(df_new_inventory)} 筆記錄")
                                
                                total_cost = df_new_inventory['總成本'].sum()
                                print(f"💰 總投資成本: {total_cost:,.2f} 元")
                            
                        except Exception as e:
                            print(f"⚠️  檢查結果時出錯: {e}")
                    else:
                        print("❌ 庫存重新整理失敗！")
                else:
                    print("⏭️  跳過實際執行")
                
            else:
                print("❌ 當前持有量計算失敗")
        else:
            print("❌ 交易歷史載入失敗")
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_robust_reorganizer()
    
    print(f"\n{'='*60}")
    print("💡 庫存重新整理工具說明:")
    print("=" * 60)
    print("1. 功能:")
    print("   • 根據交易歷史重新計算當前持有量")
    print("   • 計算每檔股票的平均成本和總成本")
    print("   • 生成當前庫存、交易歷史、交易摘要三個工作表")
    print("   • 自動備份原始檔案")
    print()
    print("2. 資料清理:")
    print("   • 修復日期格式問題")
    print("   • 清理數量和價格的資料類型")
    print("   • 移除無效的交易記錄")
    print()
    print("3. 異常檢測:")
    print("   • 檢查淨持有量為負數的情況")
    print("   • 檢查資料類型不一致的問題")
    print("   • 檢查空值和無效值")
