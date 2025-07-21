#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試庫存系統修正
"""

import os
import pandas as pd
from stock_inventory_system import StockInventorySystem

def test_inventory_system():
    """測試庫存系統"""
    print("🧪 測試庫存系統修正")
    print("=" * 50)
    
    # 檢查庫存檔案
    inventory_file = 'stock_inventory.xlsx'
    
    if not os.path.exists(inventory_file):
        print(f"❌ 庫存檔案不存在: {inventory_file}")
        return False
    
    print(f"✅ 找到庫存檔案: {inventory_file}")
    
    # 檢查工作表
    try:
        excel_file = pd.ExcelFile(inventory_file)
        print(f"📋 工作表: {excel_file.sheet_names}")
        
        if '當前庫存' in excel_file.sheet_names:
            print("✅ 找到 '當前庫存' 工作表")
        else:
            print("❌ 沒有找到 '當前庫存' 工作表")
            print("💡 可用的工作表:", excel_file.sheet_names)
            return False
            
    except Exception as e:
        print(f"❌ 檢查工作表失敗: {e}")
        return False
    
    # 測試庫存系統
    try:
        print(f"\n📊 測試庫存系統...")
        system = StockInventorySystem(inventory_file)
        
        print("📦 測試讀取庫存...")
        system.show_inventory()
        
        print("✅ 庫存系統測試成功！")
        return True
        
    except Exception as e:
        print(f"❌ 庫存系統測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函數"""
    print("🧪 庫存系統修正測試")
    print("=" * 40)
    
    success = test_inventory_system()
    
    if success:
        print(f"\n🎉 測試成功！")
        print("💡 現在可以正常使用 stock_inventory_system.py")
        print("💡 執行: python stock_inventory_system.py")
    else:
        print(f"\n❌ 測試失敗！")
        print("💡 請檢查:")
        print("  1. stock_inventory.xlsx 檔案是否存在")
        print("  2. 檔案中是否有 '當前庫存' 工作表")
        print("  3. 工作表格式是否正確")

if __name__ == "__main__":
    main()
