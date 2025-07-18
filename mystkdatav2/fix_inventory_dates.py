#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修復庫存檔案中的日期格式問題
"""

import pandas as pd
import os
from datetime import datetime

def analyze_date_issues(filename):
    """分析日期問題"""
    print(f"🔍 分析日期問題: {filename}")
    print("=" * 50)
    
    try:
        excel_file = pd.ExcelFile(filename)
        
        for sheet_name in excel_file.sheet_names:
            print(f"\n📋 工作表: {sheet_name}")
            
            try:
                df = pd.read_excel(filename, sheet_name=sheet_name)
                
                # 查找日期相關欄位
                date_columns = [col for col in df.columns if '日期' in col or 'date' in col.lower()]
                
                if date_columns:
                    print(f"   日期欄位: {date_columns}")
                    
                    for col in date_columns:
                        print(f"\n   📅 分析欄位: {col}")
                        
                        # 顯示原始資料樣本
                        print("   原始資料樣本:")
                        sample_values = df[col].head(10).tolist()
                        for i, val in enumerate(sample_values):
                            print(f"     第{i+1}行: '{val}' (類型: {type(val).__name__})")
                        
                        # 統計資料類型
                        value_types = df[col].apply(lambda x: type(x).__name__).value_counts()
                        print(f"   資料類型統計: {dict(value_types)}")
                        
                        # 檢查是否有問題值
                        problem_values = []
                        for idx, val in enumerate(df[col]):
                            if pd.isna(val):
                                continue
                            
                            val_str = str(val).strip()
                            
                            # 檢查是否是純數字且長度很短（可能是錯誤的日期）
                            if val_str.isdigit() and len(val_str) <= 2:
                                problem_values.append((idx+1, val))
                            # 檢查是否包含無效字符
                            elif not any(char.isdigit() for char in val_str):
                                if val_str not in ['', 'NaN', 'None']:
                                    problem_values.append((idx+1, val))
                        
                        if problem_values:
                            print(f"   ⚠️  發現 {len(problem_values)} 個可能有問題的日期值:")
                            for row_num, val in problem_values[:5]:  # 只顯示前5個
                                print(f"     第{row_num}行: '{val}'")
                            if len(problem_values) > 5:
                                print(f"     ... 還有 {len(problem_values) - 5} 個")
                        else:
                            print("   ✅ 沒有發現明顯的日期問題")
                else:
                    print("   沒有找到日期欄位")
                    
            except Exception as e:
                print(f"   ❌ 分析工作表失敗: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ 分析檔案失敗: {e}")
        return False

def fix_date_column(df, column_name):
    """修復日期欄位"""
    print(f"🔧 修復日期欄位: {column_name}")
    
    fixed_dates = []
    fix_count = 0
    
    for i, date_value in enumerate(df[column_name]):
        try:
            if pd.isna(date_value) or date_value == '':
                fixed_dates.append(pd.NaT)
                continue
            
            # 如果已經是datetime類型
            if isinstance(date_value, datetime):
                fixed_dates.append(date_value)
                continue
            
            # 轉換為字符串處理
            date_str = str(date_value).strip()
            
            # 如果是純數字且很短，可能是錯誤的資料
            if date_str.isdigit() and len(date_str) <= 2:
                print(f"  ⚠️  第{i+1}行: '{date_str}' 看起來不是有效日期，設為空值")
                fixed_dates.append(pd.NaT)
                fix_count += 1
                continue
            
            # 如果是較大的數字，可能是Excel序列號
            if date_str.isdigit() and len(date_str) >= 3:
                try:
                    # Excel日期序列號轉換（1900年1月1日為1）
                    excel_date = pd.to_datetime('1900-01-01') + pd.Timedelta(days=int(date_str)-2)
                    fixed_dates.append(excel_date)
                    print(f"  🔧 第{i+1}行: Excel序列號 '{date_str}' -> {excel_date.strftime('%Y-%m-%d')}")
                    fix_count += 1
                    continue
                except:
                    pass
            
            # 嘗試各種日期格式
            date_formats = [
                '%Y-%m-%d',
                '%Y/%m/%d', 
                '%m/%d/%Y',
                '%d/%m/%Y',
                '%Y-%m-%d %H:%M:%S',
                '%Y/%m/%d %H:%M:%S'
            ]
            
            parsed_date = None
            for fmt in date_formats:
                try:
                    parsed_date = datetime.strptime(date_str, fmt)
                    break
                except ValueError:
                    continue
            
            if parsed_date:
                fixed_dates.append(parsed_date)
            else:
                # 使用pandas的智能解析
                try:
                    parsed_date = pd.to_datetime(date_str, infer_datetime_format=True)
                    fixed_dates.append(parsed_date)
                except:
                    print(f"  ❌ 第{i+1}行: 無法解析 '{date_value}' -> 設為空值")
                    fixed_dates.append(pd.NaT)
                    fix_count += 1
                    
        except Exception as e:
            print(f"  ❌ 第{i+1}行: 處理錯誤 '{date_value}' -> {e}")
            fixed_dates.append(pd.NaT)
            fix_count += 1
    
    print(f"  ✅ 修復完成，共修復 {fix_count} 個日期值")
    return pd.Series(fixed_dates), fix_count

def fix_inventory_dates(filename):
    """修復庫存檔案的日期問題"""
    print(f"🔧 修復庫存檔案日期: {filename}")
    print("=" * 50)
    
    # 備份原始檔案
    backup_file = f"{filename.replace('.xlsx', '')}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    
    try:
        import shutil
        shutil.copy2(filename, backup_file)
        print(f"✅ 原始檔案已備份: {backup_file}")
    except Exception as e:
        print(f"❌ 備份失敗: {e}")
        choice = input("是否繼續？(y/N): ").strip().lower()
        if choice not in ['y', 'yes']:
            return False
    
    try:
        # 讀取所有工作表
        excel_file = pd.ExcelFile(filename)
        fixed_sheets = {}
        total_fixes = 0
        
        for sheet_name in excel_file.sheet_names:
            print(f"\n📋 處理工作表: {sheet_name}")
            
            try:
                df = pd.read_excel(filename, sheet_name=sheet_name)
                
                # 查找日期相關欄位
                date_columns = [col for col in df.columns if '日期' in col or 'date' in col.lower()]
                
                if date_columns:
                    df_fixed = df.copy()
                    sheet_fixes = 0
                    
                    for col in date_columns:
                        fixed_series, fix_count = fix_date_column(df, col)
                        df_fixed[col] = fixed_series
                        sheet_fixes += fix_count
                    
                    fixed_sheets[sheet_name] = df_fixed
                    total_fixes += sheet_fixes
                    print(f"  ✅ 工作表修復完成，共修復 {sheet_fixes} 個日期值")
                else:
                    fixed_sheets[sheet_name] = df
                    print("  ℹ️  沒有日期欄位需要修復")
                    
            except Exception as e:
                print(f"  ❌ 處理工作表失敗: {e}")
                return False
        
        # 保存修復後的檔案
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            for sheet_name, df in fixed_sheets.items():
                df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        print(f"\n✅ 日期修復完成！")
        print(f"📊 總共修復 {total_fixes} 個日期值")
        print(f"💾 備份檔案: {backup_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ 修復過程失敗: {e}")
        return False

def main():
    """主函數"""
    print("🔧 庫存檔案日期修復工具")
    print("=" * 40)
    
    # 檢查可用的庫存檔案
    possible_files = ['inventory.xlsx', 'stock_inventory.xlsx', 'test_excel_inventory.xlsx']
    available_files = [f for f in possible_files if os.path.exists(f)]
    
    if not available_files:
        print("❌ 沒有找到庫存檔案")
        return
    
    print("📁 可用的庫存檔案:")
    for i, filename in enumerate(available_files, 1):
        file_size = os.path.getsize(filename)
        print(f"  {i}. {filename} ({file_size:,} bytes)")
    
    # 選擇檔案
    if len(available_files) == 1:
        selected_file = available_files[0]
        print(f"\n🎯 使用檔案: {selected_file}")
    else:
        try:
            choice = int(input(f"\n請選擇檔案 (1-{len(available_files)}): ")) - 1
            if 0 <= choice < len(available_files):
                selected_file = available_files[choice]
            else:
                print("❌ 無效的選擇")
                return
        except ValueError:
            print("❌ 請輸入有效的數字")
            return
    
    # 分析日期問題
    print(f"\n🔍 分析日期問題...")
    if not analyze_date_issues(selected_file):
        return
    
    # 詢問是否修復
    print(f"\n{'='*50}")
    choice = input("是否要修復日期問題？(y/N): ").strip().lower()
    
    if choice in ['y', 'yes']:
        if fix_inventory_dates(selected_file):
            print("\n🎉 日期修復成功！現在可以重新執行庫存整理工具。")
        else:
            print("\n❌ 日期修復失敗！")
    else:
        print("❌ 操作已取消")

if __name__ == "__main__":
    main()
