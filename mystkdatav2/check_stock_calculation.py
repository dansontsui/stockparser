#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
檢查特定股票的計算過程
"""

import pandas as pd
import os
from datetime import datetime

def check_stock_calculation(stock_code='5871', inventory_file='stock_inventory.xlsx'):
    """檢查特定股票的計算過程"""
    print(f"🔍 檢查股票 {stock_code} 的計算過程")
    print("=" * 60)
    
    if not os.path.exists(inventory_file):
        print(f"❌ 庫存檔案不存在: {inventory_file}")
        return
    
    try:
        # 讀取交易歷史
        df_transactions = pd.read_excel(inventory_file, sheet_name='交易歷史')
        print(f"📊 總交易記錄: {len(df_transactions)} 筆")
        
        # 篩選指定股票的交易
        stock_transactions = df_transactions[df_transactions['股票代碼'].astype(str) == str(stock_code)]
        
        if stock_transactions.empty:
            print(f"❌ 沒有找到股票 {stock_code} 的交易記錄")
            return
        
        print(f"🎯 找到股票 {stock_code} 的交易記錄: {len(stock_transactions)} 筆")
        
        # 顯示股票名稱
        stock_name = stock_transactions.iloc[0]['股票名稱']
        print(f"📈 股票名稱: {stock_name}")
        
        # 轉換日期
        stock_transactions = stock_transactions.copy()
        stock_transactions['交易日期'] = pd.to_datetime(stock_transactions['交易日期'], errors='coerce')
        
        # 按日期排序
        stock_transactions = stock_transactions.sort_values('交易日期')
        
        print(f"\n📋 詳細交易記錄:")
        print("=" * 80)
        
        running_quantity = 0
        running_cost = 0.0
        
        for i, (_, transaction) in enumerate(stock_transactions.iterrows(), 1):
            date = transaction['交易日期']
            transaction_type = transaction['交易類型']
            quantity = float(transaction['數量'])
            price = float(transaction['價格'])
            
            print(f"第{i:2d}筆: {date.strftime('%Y-%m-%d')} | {transaction_type:2s} | {quantity:8.0f} 股 × {price:6.2f} = {quantity*price:10.2f} 元")
            
            if transaction_type == '買入':
                running_quantity += quantity
                running_cost += quantity * price
                print(f"       累計: {running_quantity:8.0f} 股, 總成本: {running_cost:12.2f} 元")
            elif transaction_type == '賣出':
                if running_quantity > 0:
                    # 按比例減少成本
                    cost_per_share = running_cost / running_quantity
                    sold_cost = quantity * cost_per_share
                    running_quantity -= quantity
                    running_cost -= sold_cost
                    print(f"       賣出成本: {sold_cost:10.2f} 元 (每股成本: {cost_per_share:.2f})")
                    print(f"       累計: {running_quantity:8.0f} 股, 總成本: {running_cost:12.2f} 元")
                else:
                    print(f"       ⚠️  警告: 賣出時沒有持有股票!")
            
            print()
        
        print("=" * 80)
        print(f"🎯 最終計算結果:")
        print(f"   持有股數: {running_quantity:,.0f} 股")
        print(f"   總成本: {running_cost:,.2f} 元")
        if running_quantity > 0:
            avg_cost = running_cost / running_quantity
            print(f"   平均成本: {avg_cost:.2f} 元")
        
        # 統計買賣總量
        buy_transactions = stock_transactions[stock_transactions['交易類型'] == '買入']
        sell_transactions = stock_transactions[stock_transactions['交易類型'] == '賣出']
        
        total_buy_quantity = buy_transactions['數量'].sum() if not buy_transactions.empty else 0
        total_sell_quantity = sell_transactions['數量'].sum() if not sell_transactions.empty else 0
        total_buy_amount = (buy_transactions['數量'] * buy_transactions['價格']).sum() if not buy_transactions.empty else 0
        total_sell_amount = (sell_transactions['數量'] * sell_transactions['價格']).sum() if not sell_transactions.empty else 0
        
        print(f"\n📊 交易統計:")
        print(f"   總買入: {total_buy_quantity:,.0f} 股, 金額: {total_buy_amount:,.2f} 元")
        print(f"   總賣出: {total_sell_quantity:,.0f} 股, 金額: {total_sell_amount:,.2f} 元")
        print(f"   淨持有: {total_buy_quantity - total_sell_quantity:,.0f} 股")
        
        # 檢查是否有重複記錄
        print(f"\n🔍 檢查重複記錄:")
        duplicates = stock_transactions.groupby(['交易日期', '交易類型', '數量', '價格']).size()
        duplicate_records = duplicates[duplicates > 1]
        
        if not duplicate_records.empty:
            print(f"⚠️  發現 {len(duplicate_records)} 組重複記錄:")
            for (date, trans_type, qty, price), count in duplicate_records.items():
                print(f"   {date.strftime('%Y-%m-%d')} {trans_type} {qty} 股 × {price} 元: {count} 次")
        else:
            print("✅ 沒有發現重複記錄")
        
        # 檢查異常記錄
        print(f"\n🔍 檢查異常記錄:")
        
        # 檢查數量或價格為0的記錄
        zero_records = stock_transactions[(stock_transactions['數量'] <= 0) | (stock_transactions['價格'] <= 0)]
        if not zero_records.empty:
            print(f"⚠️  發現 {len(zero_records)} 筆數量或價格為0的記錄")
        else:
            print("✅ 沒有發現數量或價格為0的記錄")
        
        # 檢查日期異常
        invalid_dates = stock_transactions[stock_transactions['交易日期'].isna()]
        if not invalid_dates.empty:
            print(f"⚠️  發現 {len(invalid_dates)} 筆日期無效的記錄")
        else:
            print("✅ 所有日期都有效")
        
        print(f"\n💡 您提到的手動計算結果是 13,809 股")
        print(f"💡 系統計算結果是 {running_quantity:,.0f} 股")
        print(f"💡 差異: {running_quantity - 13809:,.0f} 股")
        
        if abs(running_quantity - 13809) > 0:
            print(f"\n🔍 可能的原因:")
            print(f"   1. 交易記錄中有重複資料")
            print(f"   2. 某些交易被重複計算")
            print(f"   3. 賣出計算邏輯有問題")
            print(f"   4. 日期範圍或篩選條件不同")
            
            # 建議檢查步驟
            print(f"\n💡 建議檢查:")
            print(f"   1. 檢查上述重複記錄")
            print(f"   2. 確認所有交易日期正確")
            print(f"   3. 檢查是否有遺漏的賣出記錄")
            print(f"   4. 確認交易類型標記正確")
        
    except Exception as e:
        print(f"❌ 檢查失敗: {e}")
        import traceback
        traceback.print_exc()

def main():
    """主函數"""
    print("🔍 股票計算檢查工具")
    print("=" * 40)
    
    # 預設檢查中租KY (5871)
    stock_code = input("請輸入股票代碼 (預設: 5871 中租KY): ").strip()
    if not stock_code:
        stock_code = '5871'
    
    inventory_file = 'stock_inventory.xlsx'
    if not os.path.exists(inventory_file):
        print(f"❌ 庫存檔案不存在: {inventory_file}")
        return
    
    check_stock_calculation(stock_code, inventory_file)

if __name__ == "__main__":
    main()
