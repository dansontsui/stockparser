#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查找庫存檔案中的所有股票
"""

import pandas as pd
import os

def find_all_stocks():
    """查找所有股票"""
    inventory_file = 'stock_inventory.xlsx'
    
    if not os.path.exists(inventory_file):
        print(f"❌ 庫存檔案不存在: {inventory_file}")
        return
    
    try:
        df = pd.read_excel(inventory_file, sheet_name='交易歷史')
        print(f"📊 總交易記錄: {len(df)} 筆")
        print(f"📋 欄位: {list(df.columns)}")
        
        print(f"\n📈 所有股票代碼:")
        print("=" * 60)
        
        stock_codes = df['股票代碼'].unique()
        
        for code in sorted([str(c) for c in stock_codes]):
            stock_data = df[df['股票代碼'].astype(str) == str(code)]
            if not stock_data.empty:
                stock_name = stock_data['股票名稱'].iloc[0]
                count = len(stock_data)
                
                # 計算買賣統計
                buy_count = len(stock_data[stock_data['交易類型'] == '買入'])
                sell_count = len(stock_data[stock_data['交易類型'] == '賣出'])
                
                print(f"{code:>8s}: {stock_name:<20s} ({count:2d} 筆交易, 買:{buy_count} 賣:{sell_count})")
        
        print(f"\n🔍 尋找中租相關股票:")
        print("=" * 40)
        
        found_zhongzu = False
        for code in stock_codes:
            stock_data = df[df['股票代碼'] == code]
            if not stock_data.empty:
                stock_name = str(stock_data['股票名稱'].iloc[0])
                if '中租' in stock_name:
                    print(f"✅ 找到中租: {code} - {stock_name}")
                    found_zhongzu = True
                    
                    # 顯示詳細統計
                    buy_data = stock_data[stock_data['交易類型'] == '買入']
                    sell_data = stock_data[stock_data['交易類型'] == '賣出']
                    
                    total_buy = buy_data['數量'].sum() if not buy_data.empty else 0
                    total_sell = sell_data['數量'].sum() if not sell_data.empty else 0
                    
                    print(f"   總買入: {total_buy:,.0f} 股")
                    print(f"   總賣出: {total_sell:,.0f} 股") 
                    print(f"   淨持有: {total_buy - total_sell:,.0f} 股")
        
        if not found_zhongzu:
            print("❌ 沒有找到中租相關股票")
            print("💡 請檢查股票名稱是否包含其他關鍵字")
        
        # 顯示一些樣本資料
        print(f"\n📄 交易記錄樣本 (前5筆):")
        print("=" * 80)
        sample_data = df.head()
        for i, (_, row) in enumerate(sample_data.iterrows(), 1):
            print(f"第{i}筆: {row['交易日期']} | {row['股票代碼']} | {row['股票名稱']} | {row['交易類型']} | {row['數量']} 股 × {row['價格']} 元")
        
    except Exception as e:
        print(f"❌ 查找失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    find_all_stocks()
