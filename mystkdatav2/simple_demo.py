#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡單演示調整庫存功能
"""

import pandas as pd
import os
from stock_inventory_system import StockInventorySystem

def simple_demo():
    """簡單演示"""
    print("調整庫存功能演示")
    print("=" * 30)
    
    inventory_file = 'stock_inventory.xlsx'
    
    if not os.path.exists(inventory_file):
        print("庫存檔案不存在:", inventory_file)
        return
    
    try:
        system = StockInventorySystem(inventory_file)
        
        # 模擬輸入 0056
        stock_code = "0056"
        print(f"輸入股票代碼: {stock_code}")
        
        # 顯示現有庫存
        df_inventory = system._read_inventory()
        stock_info = df_inventory[df_inventory['股票代碼'] == stock_code]
        
        if not stock_info.empty:
            current_qty = int(stock_info.iloc[0]['持有股數'])
            stock_name = stock_info.iloc[0]['股票名稱']
            avg_cost = float(stock_info.iloc[0]['平均成本'])
            total_cost = float(stock_info.iloc[0]['總成本'])
            
            print(f"股票名稱: {stock_name}")
            print(f"目前持有: {current_qty:,} 股")
            print(f"平均成本: {avg_cost:.2f} 元/股")
            print(f"總成本: {total_cost:,.2f} 元")
            
            # 顯示最近交易
            df_transactions = system._read_transactions()
            recent = df_transactions[df_transactions['股票代碼'] == stock_code].tail(3)
            
            if not recent.empty:
                print("最近3筆交易:")
                for _, row in recent.iterrows():
                    date = row['交易日期']
                    trans_type = row['交易類型']
                    quantity = row['數量']
                    price = row['價格']
                    print(f"  {date.strftime('%Y-%m-%d')} | {trans_type} | {quantity:,} 股 × {price:.2f} 元")
        else:
            print(f"目前沒有持有 {stock_code}")
        
        print("\n功能說明:")
        print("1. 輸入股票代號後立即顯示現有庫存")
        print("2. 顯示持有股數、平均成本、總成本")
        print("3. 顯示最近3筆交易記錄")
        print("4. 然後可以輸入目標數量進行調整")
        
    except Exception as e:
        print(f"演示失敗: {e}")

if __name__ == "__main__":
    simple_demo()
