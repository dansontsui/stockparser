#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
檢查並重新整理庫存工具
"""

import pandas as pd
import os
from datetime import datetime
from inventory_reorganizer import InventoryReorganizer

def check_inventory_files():
    """檢查可用的庫存檔案"""
    print("📁 檢查可用的庫存檔案")
    print("=" * 40)
    
    # 可能的庫存檔案
    possible_files = [
        'inventory.xlsx',
        'stock_inventory.xlsx', 
        'test_excel_inventory.xlsx'
    ]
    
    available_files = []
    
    for filename in possible_files:
        if os.path.exists(filename):
            file_size = os.path.getsize(filename)
            mod_time = datetime.fromtimestamp(os.path.getmtime(filename))
            
            print(f"✅ {filename}")
            print(f"   大小: {file_size:,} bytes")
            print(f"   修改時間: {mod_time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # 檢查工作表
            try:
                excel_file = pd.ExcelFile(filename)
                print(f"   工作表: {excel_file.sheet_names}")
                available_files.append(filename)
            except Exception as e:
                print(f"   ❌ 讀取失敗: {e}")
            
            print()
    
    if not available_files:
        print("❌ 沒有找到可用的庫存檔案")
        return None
    
    return available_files

def analyze_inventory_file(filename):
    """分析庫存檔案內容"""
    print(f"🔍 分析庫存檔案: {filename}")
    print("=" * 50)
    
    try:
        excel_file = pd.ExcelFile(filename)
        
        for sheet_name in excel_file.sheet_names:
            print(f"\n📋 工作表: {sheet_name}")
            
            try:
                df = pd.read_excel(filename, sheet_name=sheet_name)
                print(f"   記錄數: {len(df)} 筆")
                print(f"   欄位: {list(df.columns)}")
                
                # 如果是交易歷史，顯示更多資訊
                if '交易' in sheet_name or 'transaction' in sheet_name.lower():
                    if '股票代碼' in df.columns:
                        stock_count = df['股票代碼'].nunique()
                        print(f"   股票檔數: {stock_count}")
                        
                        if '交易類型' in df.columns:
                            buy_count = len(df[df['交易類型'] == '買入'])
                            sell_count = len(df[df['交易類型'] == '賣出'])
                            print(f"   買入交易: {buy_count} 筆")
                            print(f"   賣出交易: {sell_count} 筆")
                        
                        if '交易日期' in df.columns:
                            try:
                                # 使用強健的日期轉換
                                df_temp = df.copy()
                                df_temp['交易日期'] = pd.to_datetime(df_temp['交易日期'], errors='coerce', infer_datetime_format=True)

                                # 移除無效日期
                                valid_dates = df_temp['交易日期'].dropna()

                                if not valid_dates.empty:
                                    min_date = valid_dates.min()
                                    max_date = valid_dates.max()
                                    print(f"   交易期間: {min_date.strftime('%Y-%m-%d')} ~ {max_date.strftime('%Y-%m-%d')}")
                                    print(f"   有效日期: {len(valid_dates)} 筆，無效日期: {len(df) - len(valid_dates)} 筆")
                                else:
                                    print("   ⚠️  所有日期都無法解析")
                            except Exception as e:
                                print(f"   ⚠️  日期解析失敗: {e}")
                        
                        # 顯示股票清單
                        stock_list = sorted(df['股票代碼'].unique())
                        print(f"   股票清單: {', '.join(stock_list)}")
                
                # 顯示前幾筆資料
                if len(df) > 0:
                    print("   資料樣本:")
                    print(df.head(3).to_string(index=False))
                
            except Exception as e:
                print(f"   ❌ 讀取工作表失敗: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ 分析檔案失敗: {e}")
        return False

def reorganize_selected_inventory(filename):
    """重新整理選定的庫存檔案"""
    print(f"🔄 重新整理庫存檔案: {filename}")
    print("=" * 50)
    
    try:
        # 建立重新整理器
        reorganizer = InventoryReorganizer(filename)
        
        # 執行重新整理
        success = reorganizer.reorganize_inventory()
        
        if success:
            print("✅ 庫存重新整理成功！")
            return True
        else:
            print("❌ 庫存重新整理失敗！")
            return False
            
    except Exception as e:
        print(f"❌ 重新整理過程失敗: {e}")
        return False

def main():
    """主函數"""
    print("📊 庫存檢查與重新整理工具")
    print("=" * 60)
    
    # 1. 檢查可用的庫存檔案
    available_files = check_inventory_files()
    
    if not available_files:
        print("請確認您有以下任一庫存檔案:")
        print("  • inventory.xlsx")
        print("  • stock_inventory.xlsx")
        print("  • test_excel_inventory.xlsx")
        return
    
    # 2. 如果只有一個檔案，直接使用
    if len(available_files) == 1:
        selected_file = available_files[0]
        print(f"🎯 使用檔案: {selected_file}")
    else:
        # 3. 讓使用者選擇檔案
        print("📋 請選擇要重新整理的庫存檔案:")
        for i, filename in enumerate(available_files, 1):
            print(f"  {i}. {filename}")
        
        try:
            choice = int(input(f"\n請選擇 (1-{len(available_files)}): ")) - 1
            if 0 <= choice < len(available_files):
                selected_file = available_files[choice]
            else:
                print("❌ 無效的選擇")
                return
        except ValueError:
            print("❌ 請輸入有效的數字")
            return
    
    # 4. 分析選定的檔案
    print(f"\n🔍 分析選定的檔案...")
    if not analyze_inventory_file(selected_file):
        return
    
    # 5. 詢問是否執行重新整理
    print(f"\n{'='*60}")
    choice = input("是否要重新整理此庫存檔案？(y/N): ").strip().lower()
    
    if choice in ['y', 'yes']:
        reorganize_selected_inventory(selected_file)
    else:
        print("❌ 操作已取消")

if __name__ == "__main__":
    main()
