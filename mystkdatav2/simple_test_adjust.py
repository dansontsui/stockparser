#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡化的庫存調整測試
"""

import pandas as pd
import os
from stock_inventory_system import StockInventorySystem

def simple_test():
    """簡化測試"""
    print("🧪 簡化庫存調整測試")
    print("=" * 40)
    
    inventory_file = 'stock_inventory.xlsx'
    
    if not os.path.exists(inventory_file):
        print(f"❌ 庫存檔案不存在: {inventory_file}")
        return
    
    try:
        # 建立庫存系統
        system = StockInventorySystem(inventory_file)
        
        # 檢查 0056 當前庫存
        df_inventory = system._read_inventory()
        stock_0056 = df_inventory[df_inventory['股票代碼'] == '0056']
        
        if stock_0056.empty:
            print("❌ 沒有找到 0056")
            return
        
        current_qty = int(stock_0056.iloc[0]['持有股數'])
        print(f"📊 0056 目前持有: {current_qty:,} 股")
        
        # 測試調整到 21982
        target_qty = 21982
        print(f"🎯 目標數量: {target_qty:,} 股")
        
        # 直接調用調整方法
        print(f"\n🔄 執行調整...")
        system.adjust_inventory('0056', target_qty, 25.0, '測試調整')
        
        # 檢查結果
        print(f"\n📦 檢查結果...")
        df_inventory_after = system._read_inventory()
        stock_0056_after = df_inventory_after[df_inventory_after['股票代碼'] == '0056']
        
        if not stock_0056_after.empty:
            new_qty = int(stock_0056_after.iloc[0]['持有股數'])
            print(f"📊 0056 調整後持有: {new_qty:,} 股")
            
            if new_qty == target_qty:
                print("✅ 調整成功！")
            else:
                print(f"❌ 調整失敗，預期: {target_qty:,}，實際: {new_qty:,}")
        else:
            print("❌ 調整後找不到 0056")
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    simple_test()
