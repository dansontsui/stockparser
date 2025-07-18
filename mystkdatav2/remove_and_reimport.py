#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清除特定股票資料並重新匯入
"""

import pandas as pd
import os
from datetime import datetime
from import_transactions import TransactionImporter

class StockDataManager:
    """股票資料管理器"""
    
    def __init__(self, inventory_file='stock_inventory.xlsx'):
        self.inventory_file = inventory_file
        self.backup_file = f'stock_inventory_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    
    def remove_stock_data(self, stock_code):
        """移除特定股票的所有交易記錄"""
        print(f"🗑️  移除股票 {stock_code} 的所有資料")
        print("=" * 50)
        
        if not os.path.exists(self.inventory_file):
            print(f"❌ 庫存檔案不存在: {self.inventory_file}")
            return False
        
        try:
            # 備份檔案
            import shutil
            shutil.copy2(self.inventory_file, self.backup_file)
            print(f"✅ 檔案已備份: {self.backup_file}")
            
            # 讀取交易歷史
            df_transactions = pd.read_excel(self.inventory_file, sheet_name='交易歷史')
            print(f"📊 原始交易記錄: {len(df_transactions)} 筆")
            
            # 檢查要移除的股票記錄
            stock_records = df_transactions[df_transactions['股票代碼'].astype(str) == str(stock_code)]
            
            if stock_records.empty:
                print(f"⚠️  沒有找到股票 {stock_code} 的記錄")
                return True
            
            print(f"🎯 找到股票 {stock_code} 的記錄: {len(stock_records)} 筆")
            
            # 顯示要移除的記錄
            print(f"📋 要移除的記錄:")
            for i, (_, record) in enumerate(stock_records.iterrows(), 1):
                date = record['交易日期']
                trans_type = record['交易類型']
                quantity = record['數量']
                price = record['價格']
                print(f"  第{i}筆: {date} | {trans_type} | {quantity} 股 × {price} 元")
            
            # 移除記錄
            df_cleaned = df_transactions[df_transactions['股票代碼'].astype(str) != str(stock_code)]
            print(f"✅ 移除後剩餘記錄: {len(df_cleaned)} 筆")
            
            # 保存清理後的資料
            # 讀取其他工作表（如果存在）
            excel_file = pd.ExcelFile(self.inventory_file)
            
            with pd.ExcelWriter(self.inventory_file, engine='openpyxl') as writer:
                # 保存清理後的交易歷史
                df_cleaned.to_excel(writer, sheet_name='交易歷史', index=False)
                
                # 保留其他工作表（除了可能需要重新計算的）
                for sheet_name in excel_file.sheet_names:
                    if sheet_name not in ['交易歷史', '當前庫存', '交易摘要']:
                        try:
                            df_other = pd.read_excel(self.inventory_file, sheet_name=sheet_name)
                            df_other.to_excel(writer, sheet_name=sheet_name, index=False)
                        except:
                            pass
            
            print(f"✅ 股票 {stock_code} 的資料已移除")
            return True
            
        except Exception as e:
            print(f"❌ 移除失敗: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def reimport_stock_data(self, stock_code, import_file):
        """重新匯入股票資料"""
        print(f"📥 重新匯入股票 {stock_code} 的資料")
        print("=" * 50)
        
        if not os.path.exists(import_file):
            print(f"❌ 匯入檔案不存在: {import_file}")
            return False
        
        # 使用交易匯入器
        importer = TransactionImporter(self.inventory_file)
        
        success = importer.import_transactions(
            import_file=import_file,
            stock_code_hint=stock_code
        )
        
        return success
    
    def remove_and_reimport(self, stock_code, import_file):
        """移除並重新匯入股票資料"""
        print(f"🔄 移除並重新匯入股票 {stock_code}")
        print("=" * 60)
        
        # 1. 移除現有資料
        if not self.remove_stock_data(stock_code):
            print("❌ 移除資料失敗，停止操作")
            return False
        
        print(f"\n" + "="*60)
        
        # 2. 重新匯入資料
        if not self.reimport_stock_data(stock_code, import_file):
            print("❌ 重新匯入失敗")
            return False
        
        print(f"\n" + "="*60)
        print("🎉 移除並重新匯入完成！")
        
        # 3. 建議重新整理庫存
        print("\n💡 建議接下來執行庫存重新整理:")
        print("   python safe_reorganize.py")
        
        return True

def main():
    """主函數"""
    print("🔄 股票資料移除與重新匯入工具")
    print("=" * 60)
    
    # 預設處理 00934
    stock_code = input("請輸入要處理的股票代碼 (預設: 00934): ").strip()
    if not stock_code:
        stock_code = '00934'
    
    import_file = input(f"請輸入匯入檔案名稱 (預設: {stock_code}.xlsx): ").strip()
    if not import_file:
        import_file = f'{stock_code}.xlsx'
    
    print(f"\n🎯 處理股票: {stock_code}")
    print(f"📁 匯入檔案: {import_file}")
    
    # 確認操作
    choice = input(f"\n⚠️  確定要移除 {stock_code} 的所有資料並重新匯入？(y/N): ").strip().lower()
    
    if choice not in ['y', 'yes']:
        print("❌ 操作已取消")
        return
    
    # 執行操作
    manager = StockDataManager()
    success = manager.remove_and_reimport(stock_code, import_file)
    
    if success:
        print(f"\n🎉 {stock_code} 資料處理完成！")
    else:
        print(f"\n❌ {stock_code} 資料處理失敗！")

if __name__ == "__main__":
    main()
