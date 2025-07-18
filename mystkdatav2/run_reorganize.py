#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接執行庫存重新整理
"""

from inventory_reorganizer import InventoryReorganizer
import os

def main():
    """主函數"""
    print("📊 庫存重新整理工具")
    print("=" * 30)
    
    # 自動檢測可用的庫存檔案
    possible_files = ['stock_inventory.xlsx', 'inventory.xlsx', 'test_excel_inventory.xlsx']
    inventory_file = None
    
    print("🔍 檢查可用的庫存檔案...")
    for filename in possible_files:
        if os.path.exists(filename):
            file_size = os.path.getsize(filename)
            print(f"✅ 找到: {filename} ({file_size:,} bytes)")
            if inventory_file is None:  # 使用第一個找到的檔案
                inventory_file = filename
        else:
            print(f"❌ 不存在: {filename}")
    
    if inventory_file is None:
        print("\n❌ 沒有找到庫存檔案")
        print("請確認以下任一檔案存在:")
        for filename in possible_files:
            print(f"  • {filename}")
        return
    
    print(f"\n🎯 使用庫存檔案: {inventory_file}")
    
    try:
        # 建立重新整理器
        reorganizer = InventoryReorganizer(inventory_file)
        
        # 詢問是否執行
        choice = input("\n是否要重新整理庫存？(y/N): ").strip().lower()
        
        if choice in ['y', 'yes']:
            print("\n🔄 開始重新整理庫存...")
            success = reorganizer.reorganize_inventory()
            
            if success:
                print("\n🎉 庫存重新整理成功！")
                print(f"📁 檔案已更新: {inventory_file}")
                print("💡 請打開Excel檔案查看以下工作表:")
                print("  • 當前庫存: 目前持有的股票和成本")
                print("  • 交易歷史: 原有的交易記錄")
                print("  • 交易摘要: 每檔股票的交易統計")
            else:
                print("\n❌ 庫存重新整理失敗！")
        else:
            print("❌ 操作已取消")
            
    except Exception as e:
        print(f"\n❌ 執行失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
    input("\n按 Enter 鍵退出...")
