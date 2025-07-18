#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
匯入交易記錄工具
將外部Excel檔案的交易記錄匯入到主要庫存檔案中
"""

import pandas as pd
import os
from datetime import datetime

class TransactionImporter:
    """交易記錄匯入器"""
    
    def __init__(self, main_inventory_file='stock_inventory.xlsx'):
        self.main_inventory_file = main_inventory_file
        self.backup_file = f'stock_inventory_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    
    def analyze_import_file(self, import_file):
        """分析要匯入的檔案結構"""
        print(f"🔍 分析匯入檔案: {import_file}")
        print("=" * 50)
        
        if not os.path.exists(import_file):
            print(f"❌ 匯入檔案不存在: {import_file}")
            return None
        
        try:
            # 檢查工作表
            excel_file = pd.ExcelFile(import_file)
            print(f"📋 工作表: {excel_file.sheet_names}")
            
            # 分析每個工作表
            sheets_data = {}
            
            for sheet_name in excel_file.sheet_names:
                try:
                    df = pd.read_excel(import_file, sheet_name=sheet_name)
                    print(f"\n📊 工作表 '{sheet_name}':")
                    print(f"   記錄數: {len(df)} 筆")
                    print(f"   欄位: {list(df.columns)}")
                    
                    # 顯示前幾筆資料
                    if len(df) > 0:
                        print("   資料樣本:")
                        for i, (_, row) in enumerate(df.head(3).iterrows()):
                            print(f"     第{i+1}筆: {dict(row)}")
                    
                    sheets_data[sheet_name] = df
                    
                except Exception as e:
                    print(f"   ❌ 讀取工作表失敗: {e}")
            
            return sheets_data
            
        except Exception as e:
            print(f"❌ 分析檔案失敗: {e}")
            return None
    
    def standardize_transaction_data(self, df, stock_code_hint=None):
        """標準化交易資料格式"""
        print("🔧 標準化交易資料格式...")
        
        df_clean = df.copy()
        
        # 嘗試識別欄位對應
        column_mapping = {}
        
        # 日期欄位
        date_candidates = ['日期', '交易日期', '成交日期', 'Date', 'date', '委託日期']
        for col in df_clean.columns:
            if any(candidate in str(col) for candidate in date_candidates):
                column_mapping['交易日期'] = col
                break
        
        # 股票代碼欄位
        code_candidates = ['股票代碼', '代碼', '股票代號', 'Code', 'Symbol']
        for col in df_clean.columns:
            if any(candidate in str(col) for candidate in code_candidates):
                column_mapping['股票代碼'] = col
                break
        
        # 股票名稱欄位
        name_candidates = ['股票名稱', '名稱', '股票', 'Name', '證券名稱']
        for col in df_clean.columns:
            if any(candidate in str(col) for candidate in name_candidates):
                column_mapping['股票名稱'] = col
                break
        
        # 交易類型欄位
        type_candidates = ['交易類型', '買賣', '類型', 'Type', '委託種類']
        for col in df_clean.columns:
            if any(candidate in str(col) for candidate in type_candidates):
                column_mapping['交易類型'] = col
                break
        
        # 數量欄位
        qty_candidates = ['數量', '股數', '成交股數', 'Quantity', 'Qty', '委託股數']
        for col in df_clean.columns:
            if any(candidate in str(col) for candidate in qty_candidates):
                column_mapping['數量'] = col
                break
        
        # 價格欄位
        price_candidates = ['價格', '成交價', '成交價格', 'Price', '委託價格']
        for col in df_clean.columns:
            if any(candidate in str(col) for candidate in price_candidates):
                column_mapping['價格'] = col
                break
        
        print(f"📋 欄位對應: {column_mapping}")
        
        # 建立標準化的DataFrame
        standardized_data = []
        
        for _, row in df_clean.iterrows():
            try:
                record = {}
                
                # 交易日期
                if '交易日期' in column_mapping:
                    date_value = row[column_mapping['交易日期']]
                    if pd.notna(date_value):
                        if isinstance(date_value, str):
                            record['交易日期'] = pd.to_datetime(date_value, errors='coerce')
                        else:
                            record['交易日期'] = pd.to_datetime(date_value)
                    else:
                        continue
                else:
                    print("⚠️  沒有找到日期欄位，使用今日日期")
                    record['交易日期'] = datetime.now()
                
                # 股票代碼
                if '股票代碼' in column_mapping:
                    record['股票代碼'] = str(row[column_mapping['股票代碼']]).strip()
                elif stock_code_hint:
                    record['股票代碼'] = str(stock_code_hint).strip()
                else:
                    print("⚠️  沒有找到股票代碼欄位")
                    continue
                
                # 股票名稱
                if '股票名稱' in column_mapping:
                    record['股票名稱'] = str(row[column_mapping['股票名稱']]).strip()
                else:
                    # 根據股票代碼推測名稱
                    if record['股票代碼'] == '00934':
                        record['股票名稱'] = '中信小資高股息'
                    else:
                        record['股票名稱'] = f"股票{record['股票代碼']}"
                
                # 交易類型
                if '交易類型' in column_mapping:
                    trans_type = str(row[column_mapping['交易類型']]).strip()
                    # 標準化交易類型
                    if '買' in trans_type or 'Buy' in trans_type or 'B' == trans_type:
                        record['交易類型'] = '買入'
                    elif '賣' in trans_type or 'Sell' in trans_type or 'S' == trans_type:
                        record['交易類型'] = '賣出'
                    else:
                        record['交易類型'] = trans_type
                else:
                    print("⚠️  沒有找到交易類型欄位，預設為買入")
                    record['交易類型'] = '買入'
                
                # 數量
                if '數量' in column_mapping:
                    qty_value = row[column_mapping['數量']]
                    record['數量'] = float(qty_value) if pd.notna(qty_value) else 0
                else:
                    print("⚠️  沒有找到數量欄位")
                    continue
                
                # 價格
                if '價格' in column_mapping:
                    price_value = row[column_mapping['價格']]
                    record['價格'] = float(price_value) if pd.notna(price_value) else 0
                else:
                    print("⚠️  沒有找到價格欄位")
                    continue
                
                # 只添加有效記錄
                if record['數量'] > 0 and record['價格'] > 0:
                    standardized_data.append(record)
                
            except Exception as e:
                print(f"⚠️  處理記錄時出錯: {e}")
                continue
        
        if standardized_data:
            df_standardized = pd.DataFrame(standardized_data)
            print(f"✅ 標準化完成: {len(df_standardized)} 筆有效記錄")
            return df_standardized
        else:
            print("❌ 沒有有效的記錄可以標準化")
            return None
    
    def import_transactions(self, import_file, sheet_name=None, stock_code_hint=None):
        """匯入交易記錄"""
        print(f"📥 匯入交易記錄")
        print("=" * 50)
        
        # 1. 備份主要庫存檔案
        if os.path.exists(self.main_inventory_file):
            try:
                import shutil
                shutil.copy2(self.main_inventory_file, self.backup_file)
                print(f"✅ 主要庫存檔案已備份: {self.backup_file}")
            except Exception as e:
                print(f"❌ 備份失敗: {e}")
                choice = input("是否繼續？(y/N): ").strip().lower()
                if choice not in ['y', 'yes']:
                    return False
        
        # 2. 分析匯入檔案
        sheets_data = self.analyze_import_file(import_file)
        if not sheets_data:
            return False
        
        # 3. 選擇要匯入的工作表
        if sheet_name and sheet_name in sheets_data:
            selected_sheet = sheet_name
        elif len(sheets_data) == 1:
            selected_sheet = list(sheets_data.keys())[0]
        else:
            print(f"\n📋 請選擇要匯入的工作表:")
            for i, name in enumerate(sheets_data.keys(), 1):
                print(f"  {i}. {name}")
            
            try:
                choice = int(input("請選擇 (輸入數字): ")) - 1
                selected_sheet = list(sheets_data.keys())[choice]
            except (ValueError, IndexError):
                print("❌ 無效的選擇")
                return False
        
        print(f"🎯 選擇工作表: {selected_sheet}")
        
        # 4. 標準化資料
        import_df = sheets_data[selected_sheet]
        standardized_df = self.standardize_transaction_data(import_df, stock_code_hint)
        
        if standardized_df is None or standardized_df.empty:
            print("❌ 沒有可匯入的資料")
            return False
        
        # 5. 載入現有交易歷史
        if os.path.exists(self.main_inventory_file):
            try:
                existing_df = pd.read_excel(self.main_inventory_file, sheet_name='交易歷史')
                print(f"📊 現有交易記錄: {len(existing_df)} 筆")
            except:
                existing_df = pd.DataFrame()
                print("📊 建立新的交易歷史")
        else:
            existing_df = pd.DataFrame()
            print("📊 建立新的交易歷史")
        
        # 6. 合併資料
        if not existing_df.empty:
            combined_df = pd.concat([existing_df, standardized_df], ignore_index=True)
        else:
            combined_df = standardized_df
        
        # 7. 按日期排序
        combined_df['交易日期'] = pd.to_datetime(combined_df['交易日期'])
        combined_df = combined_df.sort_values('交易日期')
        
        print(f"📊 合併後總記錄: {len(combined_df)} 筆")
        
        # 8. 保存到主要庫存檔案
        try:
            # 如果主檔案存在，保留其他工作表
            if os.path.exists(self.main_inventory_file):
                with pd.ExcelWriter(self.main_inventory_file, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                    combined_df.to_excel(writer, sheet_name='交易歷史', index=False)
            else:
                with pd.ExcelWriter(self.main_inventory_file, engine='openpyxl') as writer:
                    combined_df.to_excel(writer, sheet_name='交易歷史', index=False)
            
            print(f"✅ 交易記錄已匯入: {self.main_inventory_file}")
            
            # 9. 顯示匯入摘要
            print(f"\n📊 匯入摘要:")
            print(f"   匯入記錄: {len(standardized_df)} 筆")
            print(f"   總記錄: {len(combined_df)} 筆")
            
            # 按股票統計
            if '股票代碼' in standardized_df.columns:
                stock_stats = standardized_df.groupby('股票代碼').agg({
                    '股票名稱': 'first',
                    '數量': 'count'
                }).rename(columns={'數量': '交易次數'})
                
                print(f"   匯入的股票:")
                for stock_code, row in stock_stats.iterrows():
                    print(f"     {stock_code} ({row['股票名稱']}): {row['交易次數']} 筆交易")
            
            return True
            
        except Exception as e:
            print(f"❌ 保存失敗: {e}")
            return False

def main():
    """主函數"""
    print("📥 交易記錄匯入工具")
    print("=" * 40)
    
    # 檢查要匯入的檔案
    import_file = input("請輸入要匯入的檔案名稱 (預設: 00934.xlsx): ").strip()
    if not import_file:
        import_file = '00934.xlsx'
    
    if not os.path.exists(import_file):
        print(f"❌ 匯入檔案不存在: {import_file}")
        return
    
    # 詢問股票代碼提示
    stock_code_hint = input("請輸入股票代碼提示 (預設: 00934): ").strip()
    if not stock_code_hint:
        stock_code_hint = '00934'
    
    # 建立匯入器
    importer = TransactionImporter()
    
    # 執行匯入
    success = importer.import_transactions(import_file, stock_code_hint=stock_code_hint)
    
    if success:
        print("\n🎉 交易記錄匯入成功！")
        print("💡 建議接下來執行庫存重新整理")
    else:
        print("\n❌ 交易記錄匯入失敗！")

if __name__ == "__main__":
    main()
