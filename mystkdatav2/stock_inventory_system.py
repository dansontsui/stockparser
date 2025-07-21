#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票庫存管理系統
使用Excel作為資料庫，記錄股票庫存和交易歷史
"""

import pandas as pd
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import openpyxl
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment


class StockInventorySystem:
    """股票庫存管理系統"""
    
    def __init__(self, excel_file: str = "stock_inventory.xlsx"):
        """
        初始化股票庫存系統
        
        Args:
            excel_file: Excel檔案路徑
        """
        self.excel_file = excel_file
        self.inventory_sheet = "當前庫存"
        self.transaction_sheet = "交易歷史"
        
        # 初始化Excel檔案
        self._initialize_excel()
    
    def _initialize_excel(self):
        """初始化Excel檔案和工作表"""
        if not os.path.exists(self.excel_file):
            # 創建新的Excel檔案
            wb = Workbook()
            
            # 創建庫存工作表
            ws_inventory = wb.active
            ws_inventory.title = self.inventory_sheet
            
            # 設定庫存表標題
            inventory_headers = [
                "股票代碼", "股票名稱", "持有股數", "平均成本", 
                "總成本", "最後更新時間", "備註"
            ]
            
            for col, header in enumerate(inventory_headers, 1):
                cell = ws_inventory.cell(row=1, column=col, value=header)
                cell.font = Font(bold=True)
                cell.fill = PatternFill(start_color="CCCCCC", end_color="CCCCCC", fill_type="solid")
                cell.alignment = Alignment(horizontal="center")
            
            # 創建交易歷史工作表
            ws_transaction = wb.create_sheet(title=self.transaction_sheet)
            
            # 設定交易歷史表標題
            transaction_headers = [
                "交易日期", "股票代碼", "股票名稱", "交易類型", 
                "數量", "價格", "總金額", "手續費", "備註"
            ]
            
            for col, header in enumerate(transaction_headers, 1):
                cell = ws_transaction.cell(row=1, column=col, value=header)
                cell.font = Font(bold=True)
                cell.fill = PatternFill(start_color="CCCCCC", end_color="CCCCCC", fill_type="solid")
                cell.alignment = Alignment(horizontal="center")
            
            # 儲存檔案
            wb.save(self.excel_file)
            print(f"✅ 已創建Excel檔案: {self.excel_file}")
        else:
            print(f"📁 Excel檔案已存在: {self.excel_file}")
    
    def _read_inventory(self) -> pd.DataFrame:
        """讀取庫存資料"""
        try:
            df = pd.read_excel(self.excel_file, sheet_name=self.inventory_sheet)
            return df
        except Exception as e:
            print(f"❌ 讀取庫存資料失敗: {e}")
            return pd.DataFrame()
    
    def _read_transactions(self) -> pd.DataFrame:
        """讀取交易歷史"""
        try:
            df = pd.read_excel(self.excel_file, sheet_name=self.transaction_sheet)
            return df
        except Exception as e:
            print(f"❌ 讀取交易歷史失敗: {e}")
            return pd.DataFrame()
    
    def _save_inventory(self, df: pd.DataFrame):
        """儲存庫存資料"""
        try:
            with pd.ExcelWriter(self.excel_file, mode='a', if_sheet_exists='replace') as writer:
                df.to_excel(writer, sheet_name=self.inventory_sheet, index=False)
            print("✅ 庫存資料已更新")
        except Exception as e:
            print(f"❌ 儲存庫存資料失敗: {e}")
    
    def _save_transaction(self, transaction_data: Dict):
        """儲存單筆交易記錄"""
        try:
            # 讀取現有交易歷史
            df_transactions = self._read_transactions()

            # 新增交易記錄
            new_transaction = pd.DataFrame([transaction_data])
            if df_transactions.empty:
                df_transactions = new_transaction
            else:
                df_transactions = pd.concat([df_transactions, new_transaction], ignore_index=True)

            # 儲存更新後的交易歷史
            with pd.ExcelWriter(self.excel_file, mode='a', if_sheet_exists='replace') as writer:
                df_transactions.to_excel(writer, sheet_name=self.transaction_sheet, index=False)

            print("✅ 交易記錄已新增")
        except Exception as e:
            print(f"❌ 儲存交易記錄失敗: {e}")

    def get_stock_name(self, stock_code: str) -> Optional[str]:
        """
        根據股票代碼查找股票名稱

        Args:
            stock_code: 股票代碼

        Returns:
            股票名稱，如果找不到則返回None
        """
        # 先從庫存中查找
        df_inventory = self._read_inventory()
        if not df_inventory.empty:
            stock_row = df_inventory[df_inventory['股票代碼'] == stock_code]
            if not stock_row.empty:
                return stock_row.iloc[0]['股票名稱']

        # 如果庫存中沒有，從交易歷史中查找
        df_transactions = self._read_transactions()
        if not df_transactions.empty:
            stock_transactions = df_transactions[df_transactions['股票代碼'] == stock_code]
            if not stock_transactions.empty:
                # 取最新的交易記錄中的股票名稱
                latest_transaction = stock_transactions.sort_values('交易日期', ascending=False).iloc[0]
                return latest_transaction['股票名稱']

        return None
    
    def buy_stock(self, stock_code: str, stock_name: Optional[str], quantity: int,
                  price: float, fee: float = 0, note: str = ""):
        """
        買入股票

        Args:
            stock_code: 股票代碼
            stock_name: 股票名稱 (可選，如果為None則嘗試從現有資料中獲取)
            quantity: 買入數量
            price: 買入價格
            fee: 手續費
            note: 備註
        """
        if quantity <= 0:
            print("❌ 買入數量必須大於0")
            return

        if price <= 0:
            print("❌ 買入價格必須大於0")
            return

        # 如果沒有提供股票名稱，嘗試從現有資料中獲取
        if stock_name is None or stock_name.strip() == "":
            existing_name = self.get_stock_name(stock_code)
            if existing_name:
                stock_name = existing_name
                print(f"✅ 自動填入股票名稱: {stock_name}")
            else:
                print("❌ 找不到股票名稱，請手動輸入")
                return

        # 計算總金額
        total_amount = quantity * price + fee

        # 記錄交易
        transaction_data = {
            "交易日期": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "股票代碼": stock_code,
            "股票名稱": stock_name,
            "交易類型": "買入",
            "數量": quantity,
            "價格": price,
            "總金額": total_amount,
            "手續費": fee,
            "備註": note
        }

        self._save_transaction(transaction_data)

        # 更新庫存
        self._update_inventory_after_buy(stock_code, stock_name, quantity, price, fee)

        print(f"✅ 成功買入 {stock_code} {quantity} 股，價格 {price} 元")
    
    def sell_stock(self, stock_code: str, quantity: int, price: float, 
                   fee: float = 0, note: str = ""):
        """
        賣出股票
        
        Args:
            stock_code: 股票代碼
            quantity: 賣出數量
            price: 賣出價格
            fee: 手續費
            note: 備註
        """
        if quantity <= 0:
            print("❌ 賣出數量必須大於0")
            return
        
        if price <= 0:
            print("❌ 賣出價格必須大於0")
            return
        
        # 檢查庫存是否足夠
        df_inventory = self._read_inventory()
        
        if df_inventory.empty:
            print("❌ 庫存為空，無法賣出")
            return
        
        stock_row = df_inventory[df_inventory['股票代碼'] == stock_code]
        
        if stock_row.empty:
            print(f"❌ 庫存中沒有股票 {stock_code}")
            return
        
        current_quantity = stock_row.iloc[0]['持有股數']
        stock_name = stock_row.iloc[0]['股票名稱']
        
        if current_quantity < quantity:
            print(f"❌ 庫存不足，目前持有 {current_quantity} 股，無法賣出 {quantity} 股")
            return
        
        # 計算總金額
        total_amount = quantity * price - fee
        
        # 記錄交易
        transaction_data = {
            "交易日期": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "股票代碼": stock_code,
            "股票名稱": stock_name,
            "交易類型": "賣出",
            "數量": quantity,
            "價格": price,
            "總金額": total_amount,
            "手續費": fee,
            "備註": note
        }
        
        self._save_transaction(transaction_data)
        
        # 更新庫存
        self._update_inventory_after_sell(stock_code, quantity)
        
        print(f"✅ 成功賣出 {stock_code} {quantity} 股，價格 {price} 元")
    
    def _update_inventory_after_buy(self, stock_code: str, stock_name: str, 
                                   quantity: int, price: float, fee: float):
        """買入後更新庫存"""
        df_inventory = self._read_inventory()
        
        # 檢查是否已有此股票
        existing_stock = df_inventory[df_inventory['股票代碼'] == stock_code]
        
        if existing_stock.empty:
            # 新股票
            new_row = {
                "股票代碼": stock_code,
                "股票名稱": stock_name,
                "持有股數": quantity,
                "平均成本": price + (fee / quantity),
                "總成本": quantity * price + fee,
                "最後更新時間": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "備註": ""
            }

            if df_inventory.empty:
                df_inventory = pd.DataFrame([new_row])
            else:
                df_inventory = pd.concat([df_inventory, pd.DataFrame([new_row])], ignore_index=True)
        else:
            # 更新現有股票
            idx = existing_stock.index[0]
            old_quantity = df_inventory.loc[idx, '持有股數']
            old_total_cost = df_inventory.loc[idx, '總成本']
            
            new_quantity = old_quantity + quantity
            new_total_cost = old_total_cost + (quantity * price + fee)
            new_avg_cost = new_total_cost / new_quantity
            
            df_inventory.loc[idx, '持有股數'] = new_quantity
            df_inventory.loc[idx, '平均成本'] = new_avg_cost
            df_inventory.loc[idx, '總成本'] = new_total_cost
            df_inventory.loc[idx, '最後更新時間'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        self._save_inventory(df_inventory)
    
    def _update_inventory_after_sell(self, stock_code: str, quantity: int):
        """賣出後更新庫存"""
        df_inventory = self._read_inventory()
        
        stock_row = df_inventory[df_inventory['股票代碼'] == stock_code]
        idx = stock_row.index[0]
        
        old_quantity = df_inventory.loc[idx, '持有股數']
        old_avg_cost = df_inventory.loc[idx, '平均成本']
        
        new_quantity = old_quantity - quantity
        
        if new_quantity == 0:
            # 完全賣出，移除該股票
            df_inventory = df_inventory.drop(idx)
        else:
            # 更新數量和總成本
            df_inventory.loc[idx, '持有股數'] = new_quantity
            df_inventory.loc[idx, '總成本'] = float(new_quantity) * float(old_avg_cost)
            df_inventory.loc[idx, '最後更新時間'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        self._save_inventory(df_inventory)
    
    def show_inventory(self):
        """顯示目前庫存"""
        df_inventory = self._read_inventory()
        
        if df_inventory.empty:
            print("📦 目前庫存為空")
            return
        
        print("\n📦 目前股票庫存:")
        print("=" * 80)
        
        for _, row in df_inventory.iterrows():
            print(f"股票代碼: {row['股票代碼']}")
            print(f"股票名稱: {row['股票名稱']}")
            print(f"持有股數: {row['持有股數']:,} 股")
            print(f"平均成本: {row['平均成本']:.2f} 元")
            print(f"總成本: {row['總成本']:,.2f} 元")
            # 檢查是否有更新時間欄位
            if '最後更新時間' in row.index:
                print(f"更新時間: {row['最後更新時間']}")

            if '備註' in row.index and row['備註']:
                print(f"備註: {row['備註']}")
            print("-" * 40)
    
    def show_transactions(self, stock_code: str = None, limit: int = 10):
        """
        顯示交易歷史

        Args:
            stock_code: 特定股票代碼，None表示顯示所有
            limit: 顯示筆數限制
        """
        df_transactions = self._read_transactions()

        if df_transactions.empty:
            print("📋 沒有交易記錄")
            return

        # 篩選特定股票
        if stock_code:
            df_transactions = df_transactions[df_transactions['股票代碼'] == stock_code]
            if df_transactions.empty:
                print(f"📋 沒有股票 {stock_code} 的交易記錄")
                return

        # 按日期排序並限制筆數
        df_transactions = df_transactions.sort_values('交易日期', ascending=False).head(limit)

        print(f"\n📋 交易歷史 (最近 {len(df_transactions)} 筆):")
        print("=" * 100)

        for _, row in df_transactions.iterrows():
            print(f"日期: {row['交易日期']}")
            print(f"股票: {row['股票代碼']} - {row['股票名稱']}")
            print(f"類型: {row['交易類型']}")
            print(f"數量: {row['數量']:,} 股")
            print(f"價格: {row['價格']:.2f} 元")
            print(f"總金額: {row['總金額']:,.2f} 元")
            if row['手續費'] > 0:
                print(f"手續費: {row['手續費']:.2f} 元")
            if row['備註']:
                print(f"備註: {row['備註']}")
            print("-" * 60)

    def reindex_inventory(self):
        """
        重新索引庫存 - 根據交易歷史重新計算所有庫存數據
        """
        print("🔄 開始重新索引庫存...")

        # 讀取所有交易記錄
        df_transactions = self._read_transactions()

        if df_transactions.empty:
            print("❌ 沒有交易記錄，無法重新索引")
            return

        # 按日期排序交易記錄
        df_transactions = df_transactions.sort_values('交易日期')

        # 初始化庫存字典
        inventory = {}

        print("📊 處理交易記錄...")

        # 逐筆處理交易記錄
        for _, transaction in df_transactions.iterrows():
            stock_code = transaction['股票代碼']
            stock_name = transaction['股票名稱']
            transaction_type = transaction['交易類型']
            quantity = int(transaction['數量'])
            price = float(transaction['價格'])
            fee = float(transaction['手續費']) if pd.notna(transaction['手續費']) else 0

            # 初始化股票記錄
            if stock_code not in inventory:
                inventory[stock_code] = {
                    '股票名稱': stock_name,
                    '持有股數': 0,
                    '總成本': 0.0,
                    '平均成本': 0.0,
                    '最後更新時間': transaction['交易日期']
                }

            # 處理買入
            if transaction_type == '買入':
                old_quantity = inventory[stock_code]['持有股數']
                old_total_cost = inventory[stock_code]['總成本']

                new_quantity = old_quantity + quantity
                new_total_cost = old_total_cost + (quantity * price + fee)

                inventory[stock_code]['持有股數'] = new_quantity
                inventory[stock_code]['總成本'] = new_total_cost
                inventory[stock_code]['平均成本'] = new_total_cost / new_quantity if new_quantity > 0 else 0
                inventory[stock_code]['最後更新時間'] = transaction['交易日期']

            # 處理賣出
            elif transaction_type == '賣出':
                old_quantity = inventory[stock_code]['持有股數']
                old_avg_cost = inventory[stock_code]['平均成本']

                if old_quantity >= quantity:
                    new_quantity = old_quantity - quantity

                    if new_quantity == 0:
                        # 完全賣出，但保留記錄以便追蹤
                        inventory[stock_code]['持有股數'] = 0
                        inventory[stock_code]['總成本'] = 0.0
                        inventory[stock_code]['平均成本'] = 0.0
                    else:
                        # 部分賣出
                        inventory[stock_code]['持有股數'] = new_quantity
                        inventory[stock_code]['總成本'] = new_quantity * old_avg_cost

                    inventory[stock_code]['最後更新時間'] = transaction['交易日期']
                else:
                    print(f"⚠️  警告: 股票 {stock_code} 在 {transaction['交易日期']} 賣出數量 ({quantity}) 超過持有數量 ({old_quantity})")

        # 轉換為DataFrame並只保留有持股的記錄
        inventory_data = []
        for stock_code, data in inventory.items():
            if data['持有股數'] > 0:  # 只保留有持股的記錄
                inventory_data.append({
                    '股票代碼': stock_code,
                    '股票名稱': data['股票名稱'],
                    '持有股數': data['持有股數'],
                    '平均成本': round(data['平均成本'], 2),
                    '總成本': round(data['總成本'], 2),
                    '最後更新時間': data['最後更新時間'],
                    '備註': ''
                })

        # 創建新的庫存DataFrame
        if inventory_data:
            df_new_inventory = pd.DataFrame(inventory_data)
            # 按股票代碼排序
            df_new_inventory = df_new_inventory.sort_values('股票代碼')
        else:
            # 創建空的DataFrame但保持正確的欄位結構
            df_new_inventory = pd.DataFrame(columns=[
                '股票代碼', '股票名稱', '持有股數', '平均成本',
                '總成本', '最後更新時間', '備註'
            ])

        # 儲存重新索引的庫存
        self._save_inventory(df_new_inventory)

        print("✅ 庫存重新索引完成！")
        print(f"📊 處理了 {len(df_transactions)} 筆交易記錄")
        print(f"📦 目前有 {len(inventory_data)} 檔股票持有庫存")

        # 顯示重新索引後的庫存
        if not df_new_inventory.empty:
            print("\n📦 重新索引後的庫存:")
            self.show_inventory()
        else:
            print("\n📦 重新索引後庫存為空")

    def adjust_inventory(self, stock_code: str, target_quantity: int, price: float, note: str = "庫存調整"):
        """
        調整庫存到指定數量

        Args:
            stock_code: 股票代碼
            target_quantity: 目標數量
            price: 調整價格
            note: 備註
        """
        if target_quantity < 0:
            print("❌ 目標數量不能為負數")
            return

        if price <= 0:
            print("❌ 調整價格必須大於0")
            return

        # 讀取當前庫存
        df_inventory = self._read_inventory()

        # 檢查股票是否存在
        if df_inventory.empty:
            current_quantity = 0
            stock_name = input(f"請輸入股票 {stock_code} 的名稱: ").strip()
            if not stock_name:
                print("❌ 股票名稱不能為空")
                return
        else:
            stock_row = df_inventory[df_inventory['股票代碼'] == stock_code]

            if stock_row.empty:
                current_quantity = 0
                stock_name = input(f"請輸入股票 {stock_code} 的名稱: ").strip()
                if not stock_name:
                    print("❌ 股票名稱不能為空")
                    return
            else:
                current_quantity = int(stock_row.iloc[0]['持有股數'])
                stock_name = stock_row.iloc[0]['股票名稱']

        # 計算差額
        difference = target_quantity - current_quantity

        print(f"\n📊 庫存調整分析:")
        print(f"股票代碼: {stock_code}")
        print(f"股票名稱: {stock_name}")
        print(f"目前數量: {current_quantity:,} 股")
        print(f"目標數量: {target_quantity:,} 股")
        print(f"差額: {difference:+,} 股")

        if difference == 0:
            print("✅ 目前數量已經等於目標數量，無需調整")
            return

        # 確認調整
        action = "買入" if difference > 0 else "賣出"
        abs_difference = abs(difference)
        total_amount = abs_difference * price

        print(f"\n🔄 將執行: {action} {abs_difference:,} 股")
        print(f"調整價格: {price:.2f} 元/股")
        print(f"調整金額: {total_amount:,.2f} 元")

        confirm = input(f"\n確認執行調整？(y/N): ").strip().lower()

        if confirm not in ['y', 'yes']:
            print("❌ 調整已取消")
            return

        # 執行調整
        if difference > 0:
            # 需要買入
            self.buy_stock(stock_code, abs_difference, price, 0, f"{note} (調整+{abs_difference})")
        else:
            # 需要賣出
            self.sell_stock(stock_code, abs_difference, price, 0, f"{note} (調整-{abs_difference})")

        print(f"✅ 庫存調整完成！{stock_code} 現在應該有 {target_quantity:,} 股")


def main():
    """主程序 - 命令列介面"""
    system = StockInventorySystem()
    
    print("🏦 股票庫存管理系統")
    print("=" * 50)
    
    while True:
        print("\n請選擇操作:")
        print("1. 買入股票")
        print("2. 賣出股票")
        print("3. 調整庫存 (輸入目前總數量)")
        print("4. 查看庫存")
        print("5. 查看交易歷史")
        print("6. 退出")
        
        choice = input("\n請輸入選項 (1-6): ").strip()
        
        if choice == "1":
            # 買入股票
            print("\n📈 買入股票")
            stock_code = input("股票代碼: ").strip().upper()

            # 檢查是否已有此股票的名稱
            existing_name = system.get_stock_name(stock_code)
            if existing_name:
                print(f"💡 找到已存在的股票: {existing_name}")
                use_existing = input("是否使用此名稱? (Y/n): ").strip().lower()
                if use_existing in ['', 'y', 'yes']:
                    stock_name = existing_name
                else:
                    stock_name = input("請輸入新的股票名稱: ").strip()
            else:
                stock_name = input("股票名稱: ").strip()

            try:
                quantity = int(input("買入數量: "))
                price = float(input("買入價格: "))
                fee = float(input("手續費 (可選，預設0): ") or "0")
                note = input("備註 (可選): ").strip()

                system.buy_stock(stock_code, stock_name, quantity, price, fee, note)
            except ValueError:
                print("❌ 請輸入有效的數字")
        
        elif choice == "2":
            # 賣出股票
            print("\n📉 賣出股票")
            stock_code = input("股票代碼: ").strip().upper()
            
            try:
                quantity = int(input("賣出數量: "))
                price = float(input("賣出價格: "))
                fee = float(input("手續費 (可選，預設0): ") or "0")
                note = input("備註 (可選): ").strip()
                
                system.sell_stock(stock_code, quantity, price, fee, note)
            except ValueError:
                print("❌ 請輸入有效的數字")
        
        elif choice == "3":
            # 調整庫存
            print("\n🔄 調整庫存")
            print("輸入目前股票總數量，系統會自動計算差額並新增對應的交易記錄")

            stock_code = input("請輸入股票代碼: ").strip().upper()
            if not stock_code:
                print("❌ 股票代碼不能為空")
                continue

            try:
                target_quantity = int(input("請輸入目標總數量: "))
                price = float(input("請輸入調整價格 (元/股): "))
                note = input("請輸入備註 (可選，預設為'庫存調整'): ").strip()

                if not note:
                    note = "庫存調整"

                system.adjust_inventory(stock_code, target_quantity, price, note)
            except ValueError:
                print("❌ 請輸入有效的數字")

        elif choice == "4":
            # 查看庫存
            system.show_inventory()

        elif choice == "5":
            # 查看交易歷史
            print("\n📋 查看交易歷史")
            stock_code = input("股票代碼 (可選，留空顯示全部): ").strip().upper()
            if not stock_code:
                stock_code = None
            
            try:
                limit = int(input("顯示筆數 (預設10): ") or "10")
                system.show_transactions(stock_code, limit)
            except ValueError:
                system.show_transactions(stock_code, 10)
        
        elif choice == "6":
            print("👋 感謝使用股票庫存管理系統！")
            break
        
        else:
            print("❌ 無效的選項，請重新選擇")


if __name__ == "__main__":
    main()
