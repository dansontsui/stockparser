#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
演示調整庫存功能
"""

import pandas as pd
import os
from stock_inventory_system import StockInventorySystem

def demo_adjust_inventory():
    """演示調整庫存功能"""
    print("🎬 演示調整庫存功能")
    print("=" * 50)
    
    inventory_file = 'stock_inventory.xlsx'
    
    if not os.path.exists(inventory_file):
        print(f"❌ 庫存檔案不存在: {inventory_file}")
        return
    
    try:
        # 建立庫存系統
        system = StockInventorySystem(inventory_file)
        
        # 模擬用戶輸入股票代碼
        stock_code = "0056"
        
        print(f"🎯 模擬輸入股票代碼: {stock_code}")
        print(f"\n📊 {stock_code} 現有庫存資訊:")
        print("-" * 40)
        
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
            
            # 顯示最近的交易記錄
            df_transactions = system._read_transactions()
            recent_transactions = df_transactions[df_transactions['股票代碼'] == stock_code].tail(3)
            
            if not recent_transactions.empty:
                print(f"\n📋 最近3筆交易:")
                for _, row in recent_transactions.iterrows():
                    date = row['交易日期']
                    trans_type = row['交易類型']
                    quantity = row['數量']
                    price = row['價格']
                    print(f"  {date.strftime('%Y-%m-%d')} | {trans_type} | {quantity:,} 股 × {price:.2f} 元")
        else:
            print(f"⚠️  目前沒有持有 {stock_code}")
            print("如果要新增此股票，請輸入目標數量")
        
        print("-" * 40)
        
        print(f"\n💡 現在您可以:")
        print(f"1. 看到 {stock_code} 的完整庫存資訊")
        print(f"2. 根據目前持有量決定調整目標")
        print(f"3. 查看最近的交易歷史作為參考")
        
        # 顯示其他股票的庫存摘要
        print(f"\n📊 所有股票庫存摘要:")
        print("-" * 60)
        
        if not df_inventory.empty:
            for _, row in df_inventory.iterrows():
                code = row['股票代碼']
                name = row['股票名稱']
                qty = int(row['持有股數'])
                cost = float(row['平均成本'])
                
                print(f"{code:>8s} | {name:<15s} | {qty:>8,} 股 | {cost:>6.2f} 元/股")
        
        print("-" * 60)
        
    except Exception as e:
        print(f"❌ 演示失敗: {e}")
        import traceback
        traceback.print_exc()

def main():
    """主函數"""
    print("🎬 調整庫存功能演示")
    print("=" * 40)
    
    print("💡 此演示會顯示:")
    print("1. 輸入股票代碼後立即顯示現有庫存")
    print("2. 股票名稱、持有股數、平均成本")
    print("3. 最近3筆交易記錄")
    print("4. 所有股票的庫存摘要")
    
    demo_adjust_inventory()
    
    print(f"\n🎯 實際使用方法:")
    print("1. 執行: python stock_inventory_system.py")
    print("2. 選擇: 3. 調整庫存")
    print("3. 輸入股票代碼後會立即顯示現有庫存資訊")
    print("4. 根據顯示的資訊決定調整目標")

if __name__ == "__main__":
    main()
