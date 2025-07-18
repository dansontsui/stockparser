#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
安全的庫存重新整理工具
專門處理資料類型混合問題
"""

from inventory_reorganizer import InventoryReorganizer
import pandas as pd
import os
from datetime import datetime

class SafeInventoryReorganizer(InventoryReorganizer):
    """安全的庫存重新整理器"""
    
    def safe_load_transaction_history(self):
        """安全載入交易歷史"""
        if not os.path.exists(self.inventory_file):
            print(f"❌ 庫存檔案不存在: {self.inventory_file}")
            return None
        
        try:
            # 讀取交易歷史
            df_transactions = pd.read_excel(self.inventory_file, sheet_name='交易歷史')
            
            print(f"📊 載入交易歷史: {len(df_transactions)} 筆記錄")
            
            # 檢查必要欄位
            required_columns = ['交易日期', '股票代碼', '股票名稱', '交易類型', '數量', '價格']
            missing_columns = [col for col in required_columns if col not in df_transactions.columns]
            
            if missing_columns:
                print(f"❌ 缺少必要欄位: {missing_columns}")
                return None
            
            # 安全的資料類型轉換
            print("🔧 進行安全的資料類型轉換...")
            
            # 1. 股票代碼統一為字符串
            df_transactions['股票代碼'] = df_transactions['股票代碼'].astype(str).str.strip()
            print(f"✅ 股票代碼已統一為字符串類型")
            
            # 2. 股票名稱統一為字符串
            df_transactions['股票名稱'] = df_transactions['股票名稱'].astype(str).str.strip()
            
            # 3. 交易類型統一為字符串
            df_transactions['交易類型'] = df_transactions['交易類型'].astype(str).str.strip()
            
            # 4. 數量轉換為數值
            df_transactions['數量'] = pd.to_numeric(df_transactions['數量'], errors='coerce')
            invalid_quantity = df_transactions['數量'].isna().sum()
            if invalid_quantity > 0:
                print(f"⚠️  發現 {invalid_quantity} 筆無效數量記錄")
                df_transactions = df_transactions.dropna(subset=['數量'])
            
            # 5. 價格轉換為數值
            df_transactions['價格'] = pd.to_numeric(df_transactions['價格'], errors='coerce')
            invalid_price = df_transactions['價格'].isna().sum()
            if invalid_price > 0:
                print(f"⚠️  發現 {invalid_price} 筆無效價格記錄")
                df_transactions = df_transactions.dropna(subset=['價格'])
            
            # 6. 日期轉換
            df_transactions['交易日期'] = self._convert_date_column(df_transactions['交易日期'])
            invalid_dates = df_transactions['交易日期'].isna().sum()
            if invalid_dates > 0:
                print(f"⚠️  發現 {invalid_dates} 筆無效日期記錄")
                df_transactions = df_transactions.dropna(subset=['交易日期'])
            
            # 7. 移除無效記錄
            before_count = len(df_transactions)
            df_transactions = df_transactions[
                (df_transactions['數量'] > 0) & 
                (df_transactions['價格'] > 0) &
                (df_transactions['股票代碼'] != '') &
                (df_transactions['股票代碼'] != 'nan')
            ]
            after_count = len(df_transactions)
            
            if before_count != after_count:
                print(f"🧹 移除了 {before_count - after_count} 筆無效記錄")
            
            # 8. 按日期排序
            df_transactions = df_transactions.sort_values('交易日期')
            
            print(f"✅ 最終有效記錄: {len(df_transactions)} 筆")
            
            # 顯示資料統計
            print(f"📊 資料統計:")
            print(f"  股票檔數: {df_transactions['股票代碼'].nunique()}")
            print(f"  交易類型: {dict(df_transactions['交易類型'].value_counts())}")
            print(f"  日期範圍: {df_transactions['交易日期'].min()} ~ {df_transactions['交易日期'].max()}")
            
            return df_transactions
            
        except Exception as e:
            print(f"❌ 載入交易歷史失敗: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def safe_reorganize_inventory(self):
        """安全的庫存重新整理"""
        print("🔄 開始安全的庫存重新整理")
        print("=" * 50)
        
        # 1. 備份當前庫存
        if not self.backup_current_inventory():
            choice = input("備份失敗，是否繼續？(y/N): ").strip().lower()
            if choice not in ['y', 'yes']:
                print("❌ 操作已取消")
                return False
        
        # 2. 安全載入交易歷史
        df_transactions = self.safe_load_transaction_history()
        if df_transactions is None or df_transactions.empty:
            print("❌ 無法載入有效的交易歷史")
            return False
        
        # 3. 計算當前持有量
        current_holdings = self.calculate_current_holdings(df_transactions)
        if not current_holdings:
            print("❌ 無法計算當前持有量")
            return False
        
        # 4. 建立當前庫存工作表
        df_inventory = self.create_current_inventory_sheet(current_holdings)
        
        # 5. 建立交易摘要
        df_summary = self.create_transaction_summary(df_transactions)
        
        # 6. 保存到Excel檔案
        try:
            with pd.ExcelWriter(self.inventory_file, engine='openpyxl') as writer:
                # 當前庫存
                df_inventory.to_excel(writer, sheet_name='當前庫存', index=False)
                
                # 交易歷史 (保持清理後的資料)
                df_transactions.to_excel(writer, sheet_name='交易歷史', index=False)
                
                # 交易摘要
                df_summary.to_excel(writer, sheet_name='交易摘要', index=False)
            
            print(f"✅ 庫存檔案已更新: {self.inventory_file}")
            
        except Exception as e:
            print(f"❌ 保存庫存檔案失敗: {e}")
            return False
        
        # 7. 顯示結果摘要
        self.show_reorganization_summary(df_inventory, df_summary)
        
        return True

def main():
    """主函數"""
    print("🛡️  安全的庫存重新整理工具")
    print("=" * 50)
    
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
        # 建立安全的重新整理器
        reorganizer = SafeInventoryReorganizer(inventory_file)
        
        # 執行安全的重新整理
        print("\n🔄 開始安全的庫存重新整理...")
        success = reorganizer.safe_reorganize_inventory()
        
        if success:
            print("\n🎉 庫存重新整理成功！")
            print(f"📁 檔案已更新: {inventory_file}")
            print("💡 請打開Excel檔案查看結果")
        else:
            print("\n❌ 庫存重新整理失敗！")
            
    except Exception as e:
        print(f"\n❌ 執行失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
