#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
庫存重新整理工具
根據歷史交易記錄重新計算和整理庫存
"""

import pandas as pd
import os
from datetime import datetime
from collections import defaultdict

class InventoryReorganizer:
    """庫存重新整理器"""
    
    def __init__(self, inventory_file: str = 'inventory.xlsx'):
        self.inventory_file = inventory_file
        self.backup_file = f'inventory_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'

    def _convert_date_column(self, date_series):
        """強健的日期轉換方法"""
        converted_dates = []

        for i, date_value in enumerate(date_series):
            try:
                if pd.isna(date_value) or date_value == '':
                    converted_dates.append(pd.NaT)
                    continue

                # 如果已經是datetime類型
                if isinstance(date_value, datetime):
                    converted_dates.append(date_value)
                    continue

                # 轉換為字符串處理
                date_str = str(date_value).strip()

                # 如果是純數字（可能是Excel的序列號）
                if date_str.isdigit():
                    try:
                        # Excel日期序列號轉換（1900年1月1日為1）
                        excel_date = pd.to_datetime('1900-01-01') + pd.Timedelta(days=int(date_str)-2)
                        converted_dates.append(excel_date)
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
                    converted_dates.append(parsed_date)
                else:
                    # 使用pandas的智能解析
                    try:
                        parsed_date = pd.to_datetime(date_str, infer_datetime_format=True)
                        converted_dates.append(parsed_date)
                    except:
                        print(f"⚠️  無法解析日期 (第{i+1}行): '{date_value}' -> 設為今日")
                        converted_dates.append(datetime.now())

            except Exception as e:
                print(f"⚠️  日期轉換錯誤 (第{i+1}行): '{date_value}' -> {e}")
                converted_dates.append(datetime.now())

        return pd.Series(converted_dates)

    def _clean_numeric_columns(self, df):
        """清理數值欄位"""
        df_clean = df.copy()

        # 確保股票代碼是字符串類型
        if '股票代碼' in df_clean.columns:
            df_clean['股票代碼'] = df_clean['股票代碼'].astype(str).str.strip()

        # 清理數量欄位
        if '數量' in df_clean.columns:
            df_clean['數量'] = pd.to_numeric(df_clean['數量'], errors='coerce').fillna(0)

        # 清理價格欄位
        if '價格' in df_clean.columns:
            df_clean['價格'] = pd.to_numeric(df_clean['價格'], errors='coerce').fillna(0)

        # 移除數量或價格為0的記錄
        if '數量' in df_clean.columns and '價格' in df_clean.columns:
            before_count = len(df_clean)
            df_clean = df_clean[(df_clean['數量'] > 0) & (df_clean['價格'] > 0)]
            after_count = len(df_clean)

            if before_count != after_count:
                print(f"⚠️  移除了 {before_count - after_count} 筆數量或價格無效的記錄")

        return df_clean

    def backup_current_inventory(self):
        """備份當前庫存檔案"""
        if os.path.exists(self.inventory_file):
            try:
                # 複製整個檔案
                import shutil
                shutil.copy2(self.inventory_file, self.backup_file)
                print(f"✅ 庫存檔案已備份: {self.backup_file}")
                return True
            except Exception as e:
                print(f"❌ 備份失敗: {e}")
                return False
        else:
            print("⚠️  庫存檔案不存在，無需備份")
            return True
    
    def load_transaction_history(self):
        """載入交易歷史"""
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
            
            # 轉換交易日期 - 使用更強健的日期處理
            df_transactions['交易日期'] = self._convert_date_column(df_transactions['交易日期'])
            
            # 按日期排序 - 先移除無效日期
            df_transactions = df_transactions.dropna(subset=['交易日期'])
            df_transactions = df_transactions.sort_values('交易日期')

            # 確保數量和價格是數值類型
            df_transactions = self._clean_numeric_columns(df_transactions)

            return df_transactions
            
        except Exception as e:
            print(f"❌ 載入交易歷史失敗: {e}")
            return None
    
    def calculate_current_holdings(self, df_transactions):
        """根據交易歷史計算當前持有量"""
        print("🔄 根據交易歷史計算當前持有量...")
        
        holdings = defaultdict(lambda: {
            'quantity': 0,
            'total_cost': 0.0,
            'stock_name': '',
            'transactions': []
        })
        
        # 處理每筆交易
        for _, transaction in df_transactions.iterrows():
            stock_code = str(transaction['股票代碼']).strip()
            stock_name = str(transaction['股票名稱']).strip()
            transaction_type = str(transaction['交易類型']).strip()

            # 確保數量和價格是數值
            try:
                quantity = float(transaction['數量'])
                price = float(transaction['價格'])
            except (ValueError, TypeError):
                print(f"⚠️  跳過無效的數量或價格記錄: {transaction['股票代碼']}")
                continue

            transaction_date = transaction['交易日期']
            
            # 更新股票名稱
            holdings[stock_code]['stock_name'] = stock_name
            
            # 記錄交易
            holdings[stock_code]['transactions'].append({
                'date': transaction_date,
                'type': transaction_type,
                'quantity': quantity,
                'price': price
            })
            
            if transaction_type == '買入':
                holdings[stock_code]['quantity'] += quantity
                holdings[stock_code]['total_cost'] += quantity * price
            elif transaction_type == '賣出':
                holdings[stock_code]['quantity'] -= quantity
                # 按比例減少成本
                if holdings[stock_code]['quantity'] > 0:
                    cost_per_share = holdings[stock_code]['total_cost'] / (holdings[stock_code]['quantity'] + quantity)
                    holdings[stock_code]['total_cost'] -= quantity * cost_per_share
                else:
                    holdings[stock_code]['total_cost'] = 0
        
        # 移除持有量為0或負數的股票
        current_holdings = {}
        for stock_code, data in holdings.items():
            if data['quantity'] > 0:
                current_holdings[stock_code] = data
        
        print(f"📈 計算完成，目前持有 {len(current_holdings)} 檔股票")
        
        return current_holdings
    
    def create_current_inventory_sheet(self, current_holdings):
        """建立當前庫存工作表"""
        print("📋 建立當前庫存工作表...")
        
        inventory_data = []
        
        for stock_code, data in current_holdings.items():
            avg_cost = data['total_cost'] / data['quantity'] if data['quantity'] > 0 else 0
            
            inventory_data.append({
                '股票代碼': stock_code,
                '股票名稱': data['stock_name'],
                '持有股數': data['quantity'],
                '平均成本': round(avg_cost, 2),
                '總成本': round(data['total_cost'], 2),
                '最後更新': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
        
        # 按股票代碼排序 - 確保都是字符串類型
        inventory_data.sort(key=lambda x: str(x['股票代碼']))
        
        df_inventory = pd.DataFrame(inventory_data)
        
        print(f"✅ 當前庫存工作表建立完成: {len(df_inventory)} 檔股票")
        
        return df_inventory
    
    def create_transaction_summary(self, df_transactions):
        """建立交易摘要"""
        print("📊 建立交易摘要...")
        
        # 按股票代碼分組統計
        summary_data = []
        
        for stock_code in df_transactions['股票代碼'].unique():
            stock_transactions = df_transactions[df_transactions['股票代碼'] == stock_code]
            stock_name = stock_transactions.iloc[0]['股票名稱']
            
            buy_transactions = stock_transactions[stock_transactions['交易類型'] == '買入']
            sell_transactions = stock_transactions[stock_transactions['交易類型'] == '賣出']
            
            total_buy_quantity = buy_transactions['數量'].sum() if not buy_transactions.empty else 0
            total_sell_quantity = sell_transactions['數量'].sum() if not sell_transactions.empty else 0
            total_buy_amount = (buy_transactions['數量'] * buy_transactions['價格']).sum() if not buy_transactions.empty else 0
            total_sell_amount = (sell_transactions['數量'] * sell_transactions['價格']).sum() if not sell_transactions.empty else 0
            
            first_buy_date = buy_transactions['交易日期'].min() if not buy_transactions.empty else None
            last_transaction_date = stock_transactions['交易日期'].max()
            
            summary_data.append({
                '股票代碼': stock_code,
                '股票名稱': stock_name,
                '總買入股數': total_buy_quantity,
                '總賣出股數': total_sell_quantity,
                '淨持有股數': total_buy_quantity - total_sell_quantity,
                '總買入金額': round(total_buy_amount, 2),
                '總賣出金額': round(total_sell_amount, 2),
                '首次買入日期': first_buy_date.strftime('%Y-%m-%d') if first_buy_date else '',
                '最後交易日期': last_transaction_date.strftime('%Y-%m-%d'),
                '交易次數': len(stock_transactions)
            })
        
        # 按股票代碼排序 - 確保都是字符串類型
        summary_data.sort(key=lambda x: str(x['股票代碼']))
        
        df_summary = pd.DataFrame(summary_data)
        
        print(f"✅ 交易摘要建立完成: {len(df_summary)} 檔股票")
        
        return df_summary
    
    def reorganize_inventory(self):
        """重新整理庫存"""
        print("🔄 開始重新整理庫存")
        print("=" * 50)
        
        # 1. 備份當前庫存
        if not self.backup_current_inventory():
            choice = input("備份失敗，是否繼續？(y/N): ").strip().lower()
            if choice not in ['y', 'yes']:
                print("❌ 操作已取消")
                return False
        
        # 2. 載入交易歷史
        df_transactions = self.load_transaction_history()
        if df_transactions is None:
            return False
        
        # 3. 計算當前持有量
        current_holdings = self.calculate_current_holdings(df_transactions)
        
        # 4. 建立當前庫存工作表
        df_inventory = self.create_current_inventory_sheet(current_holdings)
        
        # 5. 建立交易摘要
        df_summary = self.create_transaction_summary(df_transactions)
        
        # 6. 保存到Excel檔案
        try:
            with pd.ExcelWriter(self.inventory_file, engine='openpyxl') as writer:
                # 當前庫存
                df_inventory.to_excel(writer, sheet_name='當前庫存', index=False)
                
                # 交易歷史 (保持原有資料)
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
    
    def show_reorganization_summary(self, df_inventory, df_summary):
        """顯示重新整理摘要"""
        print(f"\n{'='*50}")
        print("📊 庫存重新整理摘要")
        print("=" * 50)
        
        print(f"📈 當前持有股票: {len(df_inventory)} 檔")
        print(f"📋 交易摘要記錄: {len(df_summary)} 檔")
        
        if not df_inventory.empty:
            total_cost = df_inventory['總成本'].sum()
            print(f"💰 總投資成本: {total_cost:,.2f} 元")
            
            print(f"\n📊 當前持有股票明細:")
            for _, row in df_inventory.iterrows():
                print(f"  {row['股票代碼']} ({row['股票名稱']}): {row['持有股數']:,} 股, 平均成本 {row['平均成本']:.2f} 元")
        
        # 檢查是否有異常
        negative_holdings = df_summary[df_summary['淨持有股數'] < 0]
        if not negative_holdings.empty:
            print(f"\n⚠️  發現 {len(negative_holdings)} 檔股票淨持有量為負數:")
            for _, row in negative_holdings.iterrows():
                print(f"  {row['股票代碼']} ({row['股票名稱']}): {row['淨持有股數']} 股")
        
        print(f"\n💾 備份檔案: {self.backup_file}")
        print("🎉 庫存重新整理完成！")
    
    def interactive_menu(self):
        """互動式選單"""
        print("📊 庫存重新整理工具")
        print("=" * 30)
        print("此工具將根據交易歷史重新計算和整理庫存")
        print("⚠️  執行前會自動備份當前庫存檔案")
        print()
        
        choice = input("是否要重新整理庫存？(y/N): ").strip().lower()
        
        if choice in ['y', 'yes']:
            success = self.reorganize_inventory()
            if success:
                print("\n✅ 庫存重新整理成功！")
            else:
                print("\n❌ 庫存重新整理失敗！")
        else:
            print("❌ 操作已取消")

if __name__ == "__main__":
    import sys

    # 檢查命令列參數
    if len(sys.argv) > 1:
        inventory_file = sys.argv[1]
    else:
        # 自動檢測可用的庫存檔案
        possible_files = ['stock_inventory.xlsx', 'inventory.xlsx', 'test_excel_inventory.xlsx']
        inventory_file = None

        for filename in possible_files:
            if os.path.exists(filename):
                inventory_file = filename
                break

        if inventory_file is None:
            print("❌ 沒有找到庫存檔案")
            print("請確認以下任一檔案存在:")
            for filename in possible_files:
                print(f"  • {filename}")
            exit(1)

    print(f"🎯 使用庫存檔案: {inventory_file}")
    reorganizer = InventoryReorganizer(inventory_file)
    reorganizer.interactive_menu()
