#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接執行庫存重新整理（無互動）
"""

from inventory_reorganizer import InventoryReorganizer
import os

def main():
    """主函數"""
    print("📊 直接執行庫存重新整理")
    print("=" * 40)
    
    # 檢查 stock_inventory.xlsx
    inventory_file = 'stock_inventory.xlsx'
    
    if not os.path.exists(inventory_file):
        print(f"❌ 庫存檔案不存在: {inventory_file}")
        
        # 檢查其他可能的檔案
        other_files = ['inventory.xlsx', 'test_excel_inventory.xlsx']
        for filename in other_files:
            if os.path.exists(filename):
                inventory_file = filename
                print(f"✅ 找到替代檔案: {filename}")
                break
        else:
            print("❌ 沒有找到任何庫存檔案")
            return
    
    print(f"🎯 使用庫存檔案: {inventory_file}")
    
    try:
        # 建立重新整理器
        reorganizer = InventoryReorganizer(inventory_file)
        
        # 直接執行重新整理
        print("\n🔄 開始重新整理庫存...")
        success = reorganizer.reorganize_inventory()
        
        if success:
            print("\n🎉 庫存重新整理成功！")
            print(f"📁 檔案已更新: {inventory_file}")
            
            # 檢查結果
            print("\n📊 檢查重新整理結果...")
            import pandas as pd
            
            try:
                excel_file = pd.ExcelFile(inventory_file)
                print(f"📋 工作表: {excel_file.sheet_names}")
                
                if '當前庫存' in excel_file.sheet_names:
                    df_inventory = pd.read_excel(inventory_file, sheet_name='當前庫存')
                    print(f"✅ 當前庫存: {len(df_inventory)} 檔股票")
                    
                    if not df_inventory.empty:
                        total_cost = df_inventory['總成本'].sum()
                        print(f"💰 總投資成本: {total_cost:,.2f} 元")
                        
                        print("\n📊 持有股票明細:")
                        for _, row in df_inventory.iterrows():
                            print(f"  {row['股票代碼']} ({row['股票名稱']}): {row['持有股數']:,} 股, 平均成本 {row['平均成本']:.2f} 元")
                
                if '交易摘要' in excel_file.sheet_names:
                    df_summary = pd.read_excel(inventory_file, sheet_name='交易摘要')
                    print(f"✅ 交易摘要: {len(df_summary)} 檔股票")
                    
                    # 檢查異常
                    negative_holdings = df_summary[df_summary['淨持有股數'] < 0]
                    if not negative_holdings.empty:
                        print(f"⚠️  發現 {len(negative_holdings)} 檔股票淨持有量為負數:")
                        for _, row in negative_holdings.iterrows():
                            print(f"    {row['股票代碼']} ({row['股票名稱']}): {row['淨持有股數']} 股")
                    else:
                        print("✅ 沒有發現異常的負持有量")
                
            except Exception as e:
                print(f"⚠️  檢查結果時出錯: {e}")
            
        else:
            print("\n❌ 庫存重新整理失敗！")
            
    except Exception as e:
        print(f"\n❌ 執行失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
