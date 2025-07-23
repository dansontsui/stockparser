#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
調試庫存調整功能
"""

import pandas as pd
import os
from datetime import datetime
from stock_inventory_system import StockInventorySystem

def debug_adjust_inventory():
    """調試庫存調整功能"""
    print("🔍 調試庫存調整功能")
    print("=" * 50)
    
    inventory_file = 'stock_inventory.xlsx'
    
    if not os.path.exists(inventory_file):
        print(f"❌ 庫存檔案不存在: {inventory_file}")
        return
    
    try:
        # 建立庫存系統
        system = StockInventorySystem(inventory_file)
        
        # 1. 檢查當前庫存
        print("📦 步驟1: 檢查當前庫存")
        df_inventory_before = system._read_inventory()
        
        stock_0056_before = df_inventory_before[df_inventory_before['股票代碼'] == '0056']
        
        if stock_0056_before.empty:
            print("❌ 沒有找到 0056 的庫存記錄")
            return
        
        current_qty = int(stock_0056_before.iloc[0]['持有股數'])
        stock_name = stock_0056_before.iloc[0]['股票名稱']
        
        print(f"   0056 ({stock_name}) 目前持有: {current_qty:,} 股")
        
        # 2. 檢查交易歷史記錄數
        print(f"\n📋 步驟2: 檢查交易歷史")
        df_transactions_before = system._read_transactions()
        transactions_count_before = len(df_transactions_before)
        
        print(f"   交易歷史記錄數: {transactions_count_before} 筆")
        
        # 3. 執行調整（小幅調整以便測試）
        target_qty = current_qty + 100  # 增加100股
        
        print(f"\n🔄 步驟3: 執行調整")
        print(f"   目標數量: {target_qty:,} 股 (增加 100 股)")
        
        # 手動執行調整步驟
        difference = target_qty - current_qty
        
        print(f"   計算差額: {difference:+,} 股")
        
        # 手動新增交易記錄
        transaction_data = {
            "交易日期": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "股票代碼": "0056",
            "股票名稱": stock_name,
            "交易類型": "買入",
            "數量": abs(difference),
            "價格": 25.0,
            "總金額": abs(difference) * 25.0,
            "手續費": 0,
            "備註": "調試測試調整"
        }
        
        print(f"   新增交易記錄: {transaction_data}")
        
        # 保存交易記錄
        system._save_transaction(transaction_data)
        
        # 4. 檢查交易記錄是否保存成功
        print(f"\n📋 步驟4: 檢查交易記錄保存")
        df_transactions_after = system._read_transactions()
        transactions_count_after = len(df_transactions_after)
        
        print(f"   保存前交易記錄: {transactions_count_before} 筆")
        print(f"   保存後交易記錄: {transactions_count_after} 筆")
        
        if transactions_count_after > transactions_count_before:
            print("   ✅ 交易記錄保存成功")
            
            # 顯示最新的交易記錄
            latest_transaction = df_transactions_after.iloc[-1]
            print(f"   最新交易: {latest_transaction['交易日期']} | {latest_transaction['股票代碼']} | {latest_transaction['交易類型']} | {latest_transaction['數量']} 股")
        else:
            print("   ❌ 交易記錄保存失敗")
            return
        
        # 5. 執行庫存重新整理
        print(f"\n🔄 步驟5: 執行庫存重新整理")
        system.reindex_inventory()
        
        # 6. 檢查庫存是否更新
        print(f"\n📦 步驟6: 檢查庫存更新")
        df_inventory_after = system._read_inventory()
        
        stock_0056_after = df_inventory_after[df_inventory_after['股票代碼'] == '0056']
        
        if not stock_0056_after.empty:
            new_qty = int(stock_0056_after.iloc[0]['持有股數'])
            
            print(f"   調整前數量: {current_qty:,} 股")
            print(f"   調整後數量: {new_qty:,} 股")
            print(f"   目標數量: {target_qty:,} 股")
            
            if new_qty == target_qty:
                print("   ✅ 庫存調整成功！")
            else:
                print(f"   ❌ 庫存調整失敗，實際: {new_qty:,}，預期: {target_qty:,}")
        else:
            print("   ❌ 調整後找不到 0056 的庫存記錄")
        
        # 7. 檢查檔案內容
        print(f"\n📁 步驟7: 檢查檔案內容")
        
        try:
            excel_file = pd.ExcelFile(inventory_file)
            print(f"   工作表: {excel_file.sheet_names}")
            
            # 檢查當前庫存工作表
            if '當前庫存' in excel_file.sheet_names:
                df_current = pd.read_excel(inventory_file, sheet_name='當前庫存')
                stock_0056_file = df_current[df_current['股票代碼'] == '0056']
                
                if not stock_0056_file.empty:
                    file_qty = int(stock_0056_file.iloc[0]['持有股數'])
                    print(f"   檔案中 0056 數量: {file_qty:,} 股")
                else:
                    print("   ❌ 檔案中找不到 0056")
            
            # 檢查交易歷史工作表
            if '交易歷史' in excel_file.sheet_names:
                df_trans_file = pd.read_excel(inventory_file, sheet_name='交易歷史')
                print(f"   檔案中交易記錄: {len(df_trans_file)} 筆")
                
                # 顯示最後幾筆交易
                print("   最後3筆交易:")
                for _, row in df_trans_file.tail(3).iterrows():
                    print(f"     {row['交易日期']} | {row['股票代碼']} | {row['交易類型']} | {row['數量']} 股")
        
        except Exception as e:
            print(f"   ❌ 檢查檔案內容失敗: {e}")
        
    except Exception as e:
        print(f"❌ 調試失敗: {e}")
        import traceback
        traceback.print_exc()

def main():
    """主函數"""
    print("🔍 庫存調整功能調試")
    print("=" * 40)
    
    print("💡 此調試會:")
    print("1. 檢查當前 0056 庫存")
    print("2. 新增一筆買入 100 股的交易記錄")
    print("3. 執行庫存重新整理")
    print("4. 檢查結果是否正確")
    
    choice = input("\n確認執行調試？(y/N): ").strip().lower()
    
    if choice not in ['y', 'yes']:
        print("❌ 調試已取消")
        return
    
    debug_adjust_inventory()

if __name__ == "__main__":
    main()
