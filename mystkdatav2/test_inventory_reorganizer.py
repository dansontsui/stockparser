#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試庫存重新整理工具
"""

from inventory_reorganizer import InventoryReorganizer
import pandas as pd
import os

def test_inventory_reorganizer():
    """測試庫存重新整理工具"""
    print("🧪 測試庫存重新整理工具")
    print("=" * 50)
    
    # 檢查庫存檔案是否存在
    if not os.path.exists('inventory.xlsx'):
        print("❌ inventory.xlsx 檔案不存在")
        return
    
    try:
        # 1. 檢查當前庫存檔案結構
        print("📋 檢查當前庫存檔案結構...")
        
        excel_file = pd.ExcelFile('inventory.xlsx')
        print(f"📊 當前工作表: {excel_file.sheet_names}")
        
        # 檢查交易歷史
        if '交易歷史' in excel_file.sheet_names:
            df_transactions = pd.read_excel('inventory.xlsx', sheet_name='交易歷史')
            print(f"📈 交易歷史記錄: {len(df_transactions)} 筆")
            
            # 顯示交易統計
            if not df_transactions.empty:
                print("📊 交易統計:")
                print(f"  股票檔數: {df_transactions['股票代碼'].nunique()}")
                print(f"  買入交易: {len(df_transactions[df_transactions['交易類型'] == '買入'])}")
                print(f"  賣出交易: {len(df_transactions[df_transactions['交易類型'] == '賣出'])}")
                
                # 顯示日期範圍
                df_transactions['交易日期'] = pd.to_datetime(df_transactions['交易日期'])
                min_date = df_transactions['交易日期'].min()
                max_date = df_transactions['交易日期'].max()
                print(f"  交易期間: {min_date.strftime('%Y-%m-%d')} ~ {max_date.strftime('%Y-%m-%d')}")
                
                # 顯示股票清單
                stock_list = df_transactions['股票代碼'].unique()
                print(f"  交易股票: {', '.join(sorted(stock_list))}")
            
        else:
            print("❌ 沒有找到 '交易歷史' 工作表")
            return
        
        # 2. 建立重新整理器並測試
        print(f"\n🔄 建立庫存重新整理器...")
        reorganizer = InventoryReorganizer()
        
        # 3. 載入交易歷史測試
        print("📥 測試載入交易歷史...")
        df_transactions = reorganizer.load_transaction_history()
        
        if df_transactions is not None:
            print("✅ 交易歷史載入成功")
            
            # 4. 計算當前持有量測試
            print("🔢 測試計算當前持有量...")
            current_holdings = reorganizer.calculate_current_holdings(df_transactions)
            
            if current_holdings:
                print(f"✅ 當前持有量計算成功: {len(current_holdings)} 檔股票")
                
                print("📊 計算結果預覽:")
                for stock_code, data in list(current_holdings.items())[:5]:  # 顯示前5檔
                    avg_cost = data['total_cost'] / data['quantity'] if data['quantity'] > 0 else 0
                    print(f"  {stock_code} ({data['stock_name']}): {data['quantity']} 股, 平均成本 {avg_cost:.2f} 元")
                
                if len(current_holdings) > 5:
                    print(f"  ... 還有 {len(current_holdings) - 5} 檔股票")
                
                # 5. 建立工作表測試
                print(f"\n📋 測試建立工作表...")
                df_inventory = reorganizer.create_current_inventory_sheet(current_holdings)
                df_summary = reorganizer.create_transaction_summary(df_transactions)
                
                print(f"✅ 當前庫存工作表: {len(df_inventory)} 筆記錄")
                print(f"✅ 交易摘要工作表: {len(df_summary)} 筆記錄")
                
                # 檢查是否有異常
                negative_holdings = df_summary[df_summary['淨持有股數'] < 0]
                if not negative_holdings.empty:
                    print(f"⚠️  發現 {len(negative_holdings)} 檔股票淨持有量為負數:")
                    for _, row in negative_holdings.iterrows():
                        print(f"    {row['股票代碼']} ({row['股票名稱']}): {row['淨持有股數']} 股")
                
                # 6. 詢問是否執行實際重新整理
                print(f"\n{'='*50}")
                print("🎯 測試完成，所有功能正常")
                
                choice = input("是否要執行實際的庫存重新整理？(y/N): ").strip().lower()
                
                if choice in ['y', 'yes']:
                    print("\n🔄 執行實際庫存重新整理...")
                    success = reorganizer.reorganize_inventory()
                    
                    if success:
                        print("✅ 庫存重新整理成功！")
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
    test_inventory_reorganizer()
    
    print(f"\n{'='*60}")
    print("💡 庫存重新整理工具使用說明:")
    print("=" * 60)
    print("1. 執行重新整理:")
    print("   python inventory_reorganizer.py")
    print("   或雙擊 reorganize_inventory.bat")
    print()
    print("2. 功能說明:")
    print("   • 根據交易歷史重新計算當前持有量")
    print("   • 計算每檔股票的平均成本")
    print("   • 建立交易摘要統計")
    print("   • 自動備份原始檔案")
    print()
    print("3. 生成的工作表:")
    print("   • 當前庫存: 目前持有的股票和成本")
    print("   • 交易歷史: 原有的交易記錄")
    print("   • 交易摘要: 每檔股票的交易統計")
    print()
    print("4. 注意事項:")
    print("   • 執行前會自動備份 inventory.xlsx")
    print("   • 確保交易歷史資料正確完整")
    print("   • 檢查是否有淨持有量為負數的異常情況")
