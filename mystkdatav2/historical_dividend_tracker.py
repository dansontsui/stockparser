#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
回朔庫存歷史股息追蹤系統
能夠根據歷史交易記錄，計算指定時間點的庫存持有量，並計算對應的股息收益
"""

import pandas as pd
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import requests
import json


class HistoricalDividendTracker:
    """回朔庫存歷史股息追蹤系統"""
    
    def __init__(self, inventory_file: str = "stock_inventory.xlsx", 
                 dividend_db_file: str = "dividend_database.xlsx"):
        """
        初始化歷史股息追蹤系統
        
        Args:
            inventory_file: 庫存Excel檔案路徑
            dividend_db_file: 配息資料庫Excel檔案路徑
        """
        self.inventory_file = inventory_file
        self.dividend_db_file = dividend_db_file
        
        # TPEx API設定 (櫃買中心 - 興櫃、上櫃股票)
        self.tpex_url = "https://www.tpex.org.tw/web/stock/exright/dailyquo/exDailyQ_result.php"

        # TSE API設定 (證交所 - 上市股票)
        self.tse_url = "https://www.twse.com.tw/rwd/zh/exRight/TWT49U"
    
    def calculate_historical_holdings(self, target_date: str) -> Dict[str, int]:
        """
        計算指定日期的歷史庫存持有量

        Args:
            target_date: 目標日期，格式 "YYYY-MM-DD"

        Returns:
            字典，key為股票代碼，value為持有股數
        """
        if not os.path.exists(self.inventory_file):
            return {}

        try:
            # 讀取交易歷史
            df_transactions = pd.read_excel(self.inventory_file, sheet_name='交易歷史')

            # 轉換交易日期為datetime
            df_transactions['交易日期'] = pd.to_datetime(df_transactions['交易日期'])
            target_datetime = pd.to_datetime(target_date)

            # 篩選目標日期之前的交易
            df_before_target = df_transactions[df_transactions['交易日期'] <= target_datetime]

            # 計算每檔股票的持有量
            holdings = {}

            for stock_code in df_before_target['股票代碼'].unique():
                stock_transactions = df_before_target[df_before_target['股票代碼'] == stock_code]

                total_holdings = 0
                for _, transaction in stock_transactions.iterrows():
                    if transaction['交易類型'] == '買入':
                        total_holdings += transaction['數量']
                    elif transaction['交易類型'] == '賣出':
                        total_holdings -= transaction['數量']

                if total_holdings > 0:
                    holdings[stock_code] = total_holdings

            return holdings

        except Exception:
            return {}
    
    def convert_to_roc_date(self, date_str: str) -> str:
        """
        將西元年日期轉換為民國年格式
        
        Args:
            date_str: 西元年日期 "YYYY-MM-DD"
            
        Returns:
            民國年日期 "YYY/MM/DD"
        """
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            roc_year = date_obj.year - 1911
            return f"{roc_year:03d}/{date_obj.month:02d}/{date_obj.day:02d}"
        except Exception as e:
            print(f"❌ 日期轉換失敗: {e}")
            return ""
    
    def fetch_dividend_data_for_year(self, year: int) -> tuple:
        """
        獲取指定年份的配息資料，分別返回TPEx和TSE的資料

        Args:
            year: 西元年份，例如 2024

        Returns:
            (tpex_data, tse_data) 兩個DataFrame的元組
        """
        print(f"🔍 獲取 {year} 年的配息資料")

        # 設定查詢範圍為整年
        start_date = f"{year}-01-01"
        end_date = f"{year}-12-31"

        # 轉換為民國年格式
        start_roc = self.convert_to_roc_date(start_date)
        end_roc = self.convert_to_roc_date(end_date)

        print(f"📅 查詢期間: {start_roc} ~ {end_roc}")

        # 從TPEx獲取 (櫃買中心)
        tpex_data = self._fetch_from_tpex(start_roc, end_roc)
        if tpex_data is None or tpex_data.empty:
            tpex_data = pd.DataFrame()

        # 從TSE獲取 (證交所 - 0056等ETF在這裡)
        tse_data = self._fetch_from_tse(start_roc, end_roc)
        if tse_data is None or tse_data.empty:
            tse_data = pd.DataFrame()

        # 保存Excel格式資料
        self._save_combined_dividend_data(tpex_data, tse_data, year)

        print(f"📊 TPEx資料: {len(tpex_data)} 筆")
        print(f"📊 TSE資料: {len(tse_data)} 筆")

        return tpex_data, tse_data

    def _save_combined_dividend_data(self, tpex_data: pd.DataFrame, tse_data: pd.DataFrame, year: int):
        """
        保存合併的配息資料

        Args:
            tpex_data: TPEx配息資料
            tse_data: TSE配息資料
            year: 年份
        """
        try:
            # 合併所有資料
            all_data = []

            if not tpex_data.empty:
                tpex_copy = tpex_data.copy()
                tpex_copy['資料來源'] = 'TPEx(櫃買中心)'
                all_data.append(tpex_copy)

            if not tse_data.empty:
                tse_copy = tse_data.copy()
                tse_copy['資料來源'] = 'TSE(證交所)'
                all_data.append(tse_copy)

            if all_data:
                # 合併資料
                combined_df = pd.concat(all_data, ignore_index=True)

                # 統一欄位名稱
                combined_df = self._standardize_dividend_columns(combined_df)

                # 只保存Excel格式
                excel_filename = f'dividend_records_{year}.xlsx'
                with pd.ExcelWriter(excel_filename, engine='openpyxl') as writer:
                    combined_df.to_excel(writer, sheet_name=f'{year}年配息記錄', index=False)

                    # 如果有TPEx資料，單獨保存一個工作表
                    if not tpex_data.empty:
                        tpex_data.to_excel(writer, sheet_name='TPEx原始資料', index=False)

                    # 如果有TSE資料，單獨保存一個工作表
                    if not tse_data.empty:
                        tse_data.to_excel(writer, sheet_name='TSE原始資料', index=False)

                print(f"💾 配息資料已保存: {excel_filename}")

                # 顯示統計資訊
                print(f"📈 {year}年配息統計:")
                print(f"  總記錄數: {len(combined_df)} 筆")

                if '資料來源' in combined_df.columns:
                    source_stats = combined_df['資料來源'].value_counts()
                    for source, count in source_stats.items():
                        print(f"  {source}: {count} 筆")

        except Exception as e:
            print(f"❌ 保存合併配息資料失敗: {e}")

    def _standardize_dividend_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        標準化配息資料欄位名稱

        Args:
            df: 原始配息資料

        Returns:
            標準化後的配息資料
        """
        try:
            df_copy = df.copy()

            # 標準化股票代碼欄位
            if '代號' in df_copy.columns:
                df_copy['股票代碼'] = df_copy['代號']
            elif '股票代號' in df_copy.columns:
                df_copy['股票代碼'] = df_copy['股票代號']

            # 標準化股票名稱欄位
            if '名稱' in df_copy.columns:
                df_copy['股票名稱'] = df_copy['名稱']

            # 標準化日期欄位
            if '除權息日期' in df_copy.columns:
                df_copy['配息日期'] = df_copy['除權息日期']
            elif '資料日期' in df_copy.columns:
                df_copy['配息日期'] = df_copy['資料日期']

            # 添加下載時間戳記
            df_copy['下載時間'] = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')

            return df_copy

        except Exception as e:
            print(f"❌ 標準化欄位失敗: {e}")
            return df

    def _fetch_from_tpex(self, start_roc: str, end_roc: str) -> Optional[pd.DataFrame]:
        """從櫃買中心獲取配息資料"""
        url = f"{self.tpex_url}?l=zh-tw&d={start_roc}&ed={end_roc}"

        print(f"🔍 從櫃買中心獲取除息資料...")
        print(f"📅 查詢期間: {start_roc} ~ {end_roc}")
        print(f"🌐 URL: {url}")

        try:
            # 發送請求
            response = requests.get(url, timeout=30, verify=False)

            if response.status_code != 200:
                print(f"❌ 櫃買中心HTTP請求失敗: {response.status_code}")
                return None

            # 解析JSON
            json_data = response.json()

            # 遞迴搜尋 fields 和 data
            def search_fields_data(obj, path=""):
                if isinstance(obj, dict):
                    if 'fields' in obj and 'data' in obj:
                        return obj['fields'], obj['data']

                    for key, value in obj.items():
                        new_path = f"{path}.{key}" if path else key
                        result = search_fields_data(value, new_path)
                        if result[0] is not None:
                            return result

                elif isinstance(obj, list):
                    for i, item in enumerate(obj):
                        new_path = f"{path}[{i}]" if path else f"[{i}]"
                        result = search_fields_data(item, new_path)
                        if result[0] is not None:
                            return result

                return None, None

            fields, data = search_fields_data(json_data)

            if fields is None or data is None:
                print("❌ 櫃買中心未找到除息資料結構")
                return None

            # 創建DataFrame
            df = pd.DataFrame(data, columns=fields)
            df['資料來源'] = '櫃買中心'
            print(f"✅ 櫃買中心成功獲取 {len(df)} 筆除息資料")

            return df

        except Exception as e:
            print(f"❌ 櫃買中心獲取除息資料失敗: {e}")
            return None
    
    def _fetch_from_tse(self, start_roc: str, end_roc: str) -> Optional[pd.DataFrame]:
        """從證交所獲取配息資料"""
        # 轉換日期格式：民國年 114/06/16 -> 西元年 20250616
        def roc_to_ad_date(roc_date):
            try:
                year, month, day = roc_date.split('/')
                ad_year = int(year) + 1911
                return f"{ad_year}{month.zfill(2)}{day.zfill(2)}"
            except:
                return roc_date

        start_date_ad = roc_to_ad_date(start_roc)
        end_date_ad = roc_to_ad_date(end_roc)

        # 證交所API參數
        params = {
            'response': 'json',
            'startDate': start_date_ad,
            'endDate': end_date_ad
        }

        print(f"🔍 從證交所獲取除息資料...")
        print(f"📅 查詢期間: {start_roc} ~ {end_roc} (民國年)")
        print(f"📅 轉換期間: {start_date_ad} ~ {end_date_ad} (西元年)")
        print(f"🌐 URL: {self.tse_url}")

        try:
            # 發送請求
            response = requests.get(self.tse_url, params=params, timeout=30, verify=False)

            if response.status_code != 200:
                print(f"❌ 證交所HTTP請求失敗: {response.status_code}")
                return None

            # 解析JSON
            json_data = response.json()

            # 證交所的JSON結構
            if 'data' in json_data and json_data['data']:
                data = json_data['data']

                # 如果有欄位定義
                if 'fields' in json_data:
                    fields = json_data['fields']
                else:
                    # 使用預設欄位名稱
                    fields = ['除權息日期', '股票代號', '股票名稱', '除權息前收盤價',
                             '除權息參考價', '權值', '息值', '權值+息值', '權/息']

                # 創建DataFrame
                df = pd.DataFrame(data, columns=fields[:len(data[0])] if data else fields)
                df['資料來源'] = '證交所'
                print(f"✅ 證交所成功獲取 {len(df)} 筆除息資料")

                return df
            else:
                print("❌ 證交所回應中無除息資料")
                return None

        except Exception as e:
            print(f"❌ 證交所獲取除息資料失敗: {e}")
            print(f"   可能原因: API格式變更或網路問題")
            return None
    
    def calculate_dividend_income_from_sources(self, tpex_data: pd.DataFrame, tse_data: pd.DataFrame,
                                             holdings: Dict[str, int], target_year_month: str) -> List[Dict]:
        """
        從TPEx和TSE資料分別計算股息收益

        Args:
            tpex_data: TPEx配息資料DataFrame
            tse_data: TSE配息資料DataFrame
            holdings: 歷史庫存持有量字典
            target_year_month: 目標年月，格式 "YYYY-MM"

        Returns:
            配息收益記錄列表
        """
        print(f"💰 計算 {target_year_month} 的股息收益")

        dividend_records = []

        for stock_code, holding_quantity in holdings.items():
            # 先在TSE資料中查找 (0056等ETF通常在這裡)
            stock_dividends = self._find_stock_in_data(tse_data, stock_code)

            # 如果TSE沒找到，再在TPEx中查找
            if stock_dividends.empty:
                stock_dividends = self._find_stock_in_data(tpex_data, stock_code)

            # 只有找到配息記錄才繼續處理
            if stock_dividends.empty:
                continue

            # 處理找到的配息記錄
            for _, dividend_row in stock_dividends.iterrows():
                dividend_amount = self._extract_dividend_amount(dividend_row)

                # 只有配息金額 > 0 才處理和印出
                if dividend_amount > 0:
                    total_dividend = holding_quantity * dividend_amount

                    # 獲取股票名稱
                    stock_name = self._extract_stock_name(dividend_row, stock_code)

                    record = {
                        '年月': target_year_month,
                        '股票代碼': stock_code,
                        '股票名稱': stock_name,
                        '持有股數': holding_quantity,
                        '每股配息': dividend_amount,
                        '總配息收益': total_dividend,
                        '除息日期': dividend_row.get('除權息日期', ''),
                        '檢查日期': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        '資料來源': dividend_row.get('資料來源', ''),
                        '備註': f'歷史回朔計算'
                    }

                    dividend_records.append(record)
                    # 只有真正有配息的才印出
                    print(f"  💰 {stock_code} ({stock_name}): {holding_quantity} 股 × {dividend_amount} = {total_dividend:.2f} 元 [{dividend_row.get('資料來源', '')}]")

        return dividend_records

    def _find_stock_in_data(self, data: pd.DataFrame, stock_code: str) -> pd.DataFrame:
        """在指定資料中查找股票"""
        if data.empty:
            return pd.DataFrame()

        # 可能的股票代碼欄位名稱
        code_fields = ['代號', '股票代號', '股票代碼', 'code', 'symbol']

        for field in code_fields:
            if field in data.columns:
                matches = data[data[field] == stock_code]
                if not matches.empty:
                    return matches

        return pd.DataFrame()

    def _extract_stock_name(self, dividend_row: pd.Series, stock_code: str) -> str:
        """提取股票名稱"""
        name_fields = ['名稱', '股票名稱', 'name', 'stock_name']

        for field in name_fields:
            if field in dividend_row.index and pd.notna(dividend_row[field]):
                return dividend_row[field]

        return f'股票{stock_code}'  # 預設名稱
    
    def _extract_dividend_amount(self, dividend_row: pd.Series) -> float:
        """提取配息金額 - 參考 daily_dividend_checker.py 的邏輯"""
        dividend_amount = 0

        # 可能的配息欄位名稱 (按優先順序排列)
        possible_fields = [
            '息值',           # 櫃買中心主要使用
            '權值+息值',      # 證交所可能使用 (包含權值和息值)
            '現金股利',       # 通用欄位
            '配息金額',       # 通用欄位
            '股利',          # 簡化欄位
            '配息',          # 簡化欄位
            '現金配息'       # 完整描述
        ]

        for field in possible_fields:
            if field in dividend_row.index:
                field_value = dividend_row[field]

                # 檢查是否為空值
                if pd.isna(field_value) or field_value == '' or field_value is None:
                    continue

                try:
                    # 特殊處理 '權值+息值' 欄位
                    if field == '權值+息值':
                        # 先檢查是否有單獨的息值欄位且有值
                        if '息值' in dividend_row.index:
                            xi_value = dividend_row['息值']

                            if not pd.isna(xi_value) and xi_value != '' and xi_value is not None:
                                try:
                                    xi_amount = float(xi_value)
                                    if xi_amount > 0:
                                        dividend_amount = xi_amount
                                        break
                                    else:
                                        # 息值為0，使用權值+息值
                                        dividend_amount = float(field_value)
                                        break
                                except (ValueError, TypeError):
                                    # 息值解析失敗，使用權值+息值
                                    dividend_amount = float(field_value)
                                    break
                            else:
                                # 息值欄位為空，使用權值+息值
                                dividend_amount = float(field_value)
                                break
                        else:
                            # 無息值欄位，直接使用權值+息值
                            dividend_amount = float(field_value)
                            break
                    else:
                        # 一般欄位處理
                        dividend_amount = float(field_value)
                        break

                except (ValueError, TypeError):
                    continue

        return dividend_amount

    def save_to_dividend_database(self, dividend_records: List[Dict]) -> bool:
        """
        將配息記錄保存到dividend_database.xlsx

        Args:
            dividend_records: 配息記錄列表

        Returns:
            是否保存成功
        """
        if not dividend_records:
            print("❌ 沒有配息記錄需要保存")
            return False

        try:
            # 讀取現有的配息資料庫
            if os.path.exists(self.dividend_db_file):
                existing_df = pd.read_excel(self.dividend_db_file, sheet_name='配息記錄')
            else:
                # 建立新的DataFrame
                existing_df = pd.DataFrame(columns=[
                    '年月', '股票代碼', '股票名稱', '持有股數', '每股配息',
                    '總配息收益', '除息日期', '檢查日期', '資料來源', '備註'
                ])

            # 轉換新記錄為DataFrame
            new_df = pd.DataFrame(dividend_records)

            # 檢查重複記錄（避免重複插入相同年月的相同股票）
            duplicates_removed = 0
            for _, new_record in new_df.iterrows():
                duplicate_mask = (
                    (existing_df['年月'] == new_record['年月']) &
                    (existing_df['股票代碼'] == new_record['股票代碼']) &
                    (existing_df['備註'].str.contains('歷史回朔計算', na=False))
                )

                if duplicate_mask.any():
                    # 移除舊的歷史回朔記錄，保留新的
                    existing_df = existing_df[~duplicate_mask]
                    duplicates_removed += 1

            if duplicates_removed > 0:
                print(f"🔄 移除了 {duplicates_removed} 筆重複的歷史回朔記錄")

            # 合併資料
            combined_df = pd.concat([existing_df, new_df], ignore_index=True)

            # 按年月和股票代碼排序
            combined_df = combined_df.sort_values(['年月', '股票代碼'])

            # 保存到Excel
            with pd.ExcelWriter(self.dividend_db_file, engine='openpyxl') as writer:
                combined_df.to_excel(writer, sheet_name='配息記錄', index=False)

            print(f"✅ 成功保存 {len(dividend_records)} 筆配息記錄到 {self.dividend_db_file}")
            return True

        except Exception as e:
            print(f"❌ 保存配息記錄失敗: {e}")
            return False

    def track_historical_dividends_range(self, start_year_month: str) -> bool:
        """
        執行從起始年份到現在的完整歷史股息追蹤流程（按實際配息日期）

        Args:
            start_year_month: 起始年月，格式 "YYYY-MM"

        Returns:
            是否執行成功
        """
        print("🎯 開始執行歷史股息追蹤範圍（按實際配息日期）")
        print("=" * 60)
        print(f"📅 起始年月: {start_year_month}")

        try:
            # 解析起始年份
            start_year = int(start_year_month.split('-')[0])

            # 獲取當前年份
            current_year = datetime.now().year

            print(f"📅 處理年份範圍: {start_year} ~ {current_year}")

            # 生成所有需要處理的年份
            years_to_process = list(range(start_year, current_year + 1))

            print(f"📊 總共需要處理 {len(years_to_process)} 個年份")

            # 逐年處理
            successful_years = 0

            for i, year in enumerate(years_to_process, 1):
                print(f"\n{'='*50}")
                print(f"📅 處理第 {i}/{len(years_to_process)} 年: {year}")

                success = self.track_dividend_by_actual_dates(year)

                if success:
                    successful_years += 1
                    print(f"✅ {year} 年處理成功")
                else:
                    print(f"⚠️  {year} 年處理失敗或無配息記錄")

            print(f"\n{'='*60}")
            print("🎉 歷史股息追蹤範圍完成！")
            print(f"📊 成功處理: {successful_years}/{len(years_to_process)} 個年份")

            # 顯示最終統計
            self.show_dividend_summary()

            return successful_years > 0

        except Exception as e:
            print(f"❌ 執行歷史股息追蹤範圍失敗: {e}")
            return False

    def track_dividend_by_actual_dates(self, year: int) -> bool:
        """
        根據實際配息日期追蹤股息（避免重複計算）

        Args:
            year: 年份

        Returns:
            是否執行成功
        """
        try:
            print(f"🎯 追蹤 {year} 年的實際配息記錄")

            # 1. 獲取該年份的配息資料 (分別從TPEx和TSE)
            tpex_data, tse_data = self.fetch_dividend_data_for_year(year)

            if tpex_data.empty and tse_data.empty:
                print(f"⚠️  {year}: 沒有找到配息資料")
                return False

            # 2. 合併所有配息資料並解析實際配息日期
            all_dividend_records = []

            # 處理 TPEx 資料
            if not tpex_data.empty:
                tpex_records = self._process_dividend_data_by_date(tpex_data, 'TPEx')
                all_dividend_records.extend(tpex_records)

            # 處理 TSE 資料
            if not tse_data.empty:
                tse_records = self._process_dividend_data_by_date(tse_data, 'TSE')
                all_dividend_records.extend(tse_records)

            if not all_dividend_records:
                print(f"⚠️  {year}: 沒有有效的配息記錄")
                return False

            print(f"� {year}: 總共找到 {len(all_dividend_records)} 筆配息記錄")

            # 3. 保存到配息資料庫
            success = self.save_to_dividend_database(all_dividend_records)

            if success:
                total_dividend = sum(record['總配息收益'] for record in all_dividend_records)
                print(f"💰 {year}: 處理了 {len(all_dividend_records)} 筆配息記錄，總收益 {total_dividend:.2f} 元")
                return True
            else:
                return False

        except Exception as e:
            print(f"❌ {year} 年配息追蹤失敗: {e}")
            return False

    def _process_dividend_data_by_date(self, dividend_data: pd.DataFrame, source: str) -> List[Dict]:
        """
        根據實際配息日期處理配息資料

        Args:
            dividend_data: 配息資料DataFrame
            year: 年份
            source: 資料來源 (TPEx/TSE)

        Returns:
            配息記錄列表
        """
        dividend_records = []

        try:
            # 解析配息日期
            dividend_data_with_dates = self._parse_dividend_dates(dividend_data)

            if dividend_data_with_dates.empty:
                print(f"⚠️  {source}: 無法解析配息日期")
                return []

            # 按股票代碼分組處理
            for stock_code in dividend_data_with_dates['股票代碼'].unique():
                stock_dividends = dividend_data_with_dates[dividend_data_with_dates['股票代碼'] == stock_code]

                # 處理該股票的每筆配息記錄
                for _, dividend_row in stock_dividends.iterrows():
                    dividend_date = dividend_row['配息日期_datetime']

                    if pd.isna(dividend_date):
                        continue

                    # 先檢查配息金額，如果沒有配息就跳過
                    dividend_amount = self._extract_dividend_amount(dividend_row)
                    if dividend_amount <= 0:
                        continue

                    # 計算配息日期時的庫存持有量
                    target_date = dividend_date.strftime("%Y-%m-%d")
                    holdings = self.calculate_historical_holdings(target_date)

                    # 只有持有該股票且有配息金額才處理
                    if stock_code not in holdings:
                        continue

                    holding_quantity = holdings[stock_code]
                    total_dividend = holding_quantity * dividend_amount
                    stock_name = self._extract_stock_name(dividend_row, stock_code)

                    # 使用配息日期的年月作為記錄年月
                    record_year_month = dividend_date.strftime("%Y-%m")

                    record = {
                        '年月': record_year_month,
                        '股票代碼': stock_code,
                        '股票名稱': stock_name,
                        '持有股數': holding_quantity,
                        '每股配息': dividend_amount,
                        '總配息收益': total_dividend,
                        '除息日期': dividend_date.strftime("%Y-%m-%d"),
                        '檢查日期': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        '資料來源': source,
                        '備註': f'歷史回朔計算-實際配息日期'
                    }

                    dividend_records.append(record)
                    # 只有真正有配息且有持有記錄的才印出
                    print(f"  💰 {stock_code} ({stock_name}) [{target_date}]: {holding_quantity} 股 × {dividend_amount} = {total_dividend:.2f} 元")

            return dividend_records

        except Exception as e:
            print(f"❌ {source} 配息資料處理失敗: {e}")
            return []

    def _parse_dividend_dates(self, dividend_data: pd.DataFrame) -> pd.DataFrame:
        """
        解析配息日期

        Args:
            dividend_data: 配息資料DataFrame

        Returns:
            包含解析後日期的DataFrame
        """
        try:
            # 複製資料避免修改原始資料
            data = dividend_data.copy()

            # 統一股票代碼欄位名稱
            if '代號' in data.columns:
                data['股票代碼'] = data['代號']
            elif '股票代號' in data.columns:
                data['股票代碼'] = data['股票代號']

            # 尋找日期欄位 - 支援多種可能的欄位名稱
            date_field = None
            possible_date_fields = ['除權息日期', '除息日期', '配息日期', '資料日期', 'date', 'ex_date']

            for field in possible_date_fields:
                if field in data.columns:
                    date_field = field
                    break

            if date_field is None:
                print(f"⚠️  找不到日期欄位，可用欄位: {list(data.columns)}")
                return pd.DataFrame()

            # 處理民國年格式日期轉換
            def convert_roc_date(date_str):
                if pd.isna(date_str) or date_str == '':
                    return None
                try:
                    date_str = str(date_str)

                    # 處理 TPEx 格式: "113/06/17"
                    if '/' in date_str:
                        parts = date_str.split('/')
                        if len(parts) == 3:
                            roc_year = int(parts[0])
                            month_part = int(parts[1])
                            day_part = int(parts[2])
                            ad_year = roc_year + 1911
                            return datetime(ad_year, month_part, day_part)

                    # 處理 TSE 格式: "114年01月17日"
                    elif '年' in date_str and '月' in date_str and '日' in date_str:
                        # 移除 "年", "月", "日" 字符
                        date_str = date_str.replace('年', '/').replace('月', '/').replace('日', '')
                        parts = date_str.split('/')
                        if len(parts) == 3:
                            roc_year = int(parts[0])
                            month_part = int(parts[1])
                            day_part = int(parts[2])
                            ad_year = roc_year + 1911
                            return datetime(ad_year, month_part, day_part)

                except Exception as e:
                    print(f"    日期轉換失敗: {date_str} -> {e}")
                    pass
                return None

            # 轉換日期
            data['配息日期_datetime'] = data[date_field].apply(convert_roc_date)

            # 過濾有效日期的記錄
            valid_data = data[data['配息日期_datetime'].notna()]

            print(f"📅 成功解析 {len(valid_data)} 筆配息日期記錄")
            return valid_data

        except Exception as e:
            print(f"❌ 解析配息日期失敗: {e}")
            return pd.DataFrame()

    def track_single_month_dividends(self, year_month: str) -> bool:
        """
        執行單一月份的歷史股息追蹤（已棄用，改用按實際配息日期追蹤）

        Args:
            year_month: 年月，格式 "YYYY-MM"

        Returns:
            是否執行成功
        """
        print(f"⚠️  單月追蹤已改為按實際配息日期追蹤，避免重複計算")

        # 解析年份
        year = int(year_month.split('-')[0])

        # 改用按實際配息日期追蹤
        return self.track_dividend_by_actual_dates(year)

    def filter_dividend_by_month(self, dividend_data: pd.DataFrame, year: int, month: int) -> pd.DataFrame:
        """
        篩選指定年月的配息記錄

        Args:
            dividend_data: 配息資料DataFrame
            year: 年份
            month: 月份

        Returns:
            篩選後的配息資料
        """
        if dividend_data.empty:
            return pd.DataFrame()

        try:
            # 尋找日期欄位 - 支援多種可能的欄位名稱
            date_field = None
            possible_date_fields = ['除權息日期', '除息日期', '配息日期', '資料日期', 'date', 'ex_date']

            for field in possible_date_fields:
                if field in dividend_data.columns:
                    date_field = field
                    break

            if date_field is None:
                print(f"⚠️  配息資料中沒有找到日期欄位，可用欄位: {list(dividend_data.columns)}")
                # 如果沒有日期欄位，返回所有資料（假設都是該年的）
                print(f"📅 {year}-{month:02d}: 無日期篩選，返回所有 {len(dividend_data)} 筆配息記錄")
                return dividend_data

            print(f"📅 使用日期欄位: {date_field}")

            # 處理民國年格式 (例如: 113/06/17)
            def convert_roc_date(date_str):
                if pd.isna(date_str) or date_str == '':
                    return None
                try:
                    parts = str(date_str).split('/')
                    if len(parts) == 3:
                        roc_year = int(parts[0])
                        month_part = int(parts[1])
                        day_part = int(parts[2])
                        ad_year = roc_year + 1911
                        return datetime(ad_year, month_part, day_part)
                except:
                    pass
                return None

            # 轉換日期
            dividend_data = dividend_data.copy()
            dividend_data['除息日期_datetime'] = dividend_data[date_field].apply(convert_roc_date)

            # 篩選指定年月的記錄
            valid_dates = dividend_data['除息日期_datetime'].notna()

            if valid_dates.sum() == 0:
                print(f"⚠️  所有日期轉換失敗，返回所有 {len(dividend_data)} 筆記錄")
                return dividend_data

            filtered_data = dividend_data[
                valid_dates &
                (dividend_data['除息日期_datetime'].dt.year == year) &
                (dividend_data['除息日期_datetime'].dt.month == month)
            ]

            print(f"📅 {year}-{month:02d}: 找到 {len(filtered_data)} 筆該月份的配息記錄")
            return filtered_data

        except Exception as e:
            print(f"❌ 篩選配息記錄失敗: {e}")
            print(f"📅 {year}-{month:02d}: 篩選失敗，返回所有 {len(dividend_data)} 筆記錄")
            return dividend_data

    def show_dividend_summary(self):
        """顯示配息摘要統計"""
        try:
            if os.path.exists(self.dividend_db_file):
                df = pd.read_excel(self.dividend_db_file, sheet_name='配息記錄')

                if not df.empty:
                    # 篩選歷史回朔記錄
                    historical_records = df[df['備註'].str.contains('歷史回朔計算', na=False)]

                    if not historical_records.empty:
                        print(f"\n📊 歷史回朔配息摘要:")
                        print(f"📋 總記錄數: {len(historical_records)} 筆")

                        total_dividend = historical_records['總配息收益'].sum()
                        print(f"� 總配息收益: {total_dividend:.2f} 元")

                        # 按年月統計
                        monthly_stats = historical_records.groupby('年月')['總配息收益'].sum().sort_index()
                        print(f"\n📈 月度配息統計:")
                        for year_month, amount in monthly_stats.items():
                            print(f"  {year_month}: {amount:.2f} 元")
                    else:
                        print("\n📦 沒有找到歷史回朔配息記錄")
                else:
                    print("\n📦 配息資料庫為空")
            else:
                print("\n❌ 配息資料庫不存在")

        except Exception as e:
            print(f"❌ 顯示配息摘要失敗: {e}")

    def track_historical_dividends(self, start_year_month: str) -> bool:
        """
        執行歷史股息追蹤流程（兼容舊版本）
        現在會自動執行範圍追蹤

        Args:
            start_year_month: 起始年月，格式 "YYYY-MM"

        Returns:
            是否執行成功
        """
        return self.track_historical_dividends_range(start_year_month)


def main():
    """主程序 - 命令列介面"""
    tracker = HistoricalDividendTracker()

    print("📈 回朔庫存歷史股息追蹤系統")
    print("=" * 50)

    while True:
        print("\n請選擇操作:")
        print("1. 執行歷史股息追蹤")
        print("2. 查看配息資料庫")
        print("3. 退出")

        choice = input("\n請輸入選項 (1-3): ").strip()

        if choice == "1":
            # 執行歷史股息追蹤
            print("\n📊 執行歷史股息追蹤")
            print("💡 系統會從起始年月開始，自動計算到現在的所有月份")
            start_year_month = input("請輸入起始年月 (格式: YYYY-MM，例如: 2024-01): ").strip()

            # 驗證輸入格式
            try:
                year, month = map(int, start_year_month.split('-'))
                if not (1 <= month <= 12):
                    raise ValueError("月份必須在1-12之間")
                if year < 2000 or year > datetime.now().year:
                    raise ValueError("年份範圍不合理")
            except ValueError as e:
                print(f"❌ 輸入格式錯誤: {e}")
                continue

            # 執行追蹤
            tracker.track_historical_dividends(start_year_month)

        elif choice == "2":
            # 查看配息資料庫
            print("\n📋 查看配息資料庫")
            if os.path.exists("dividend_database.xlsx"):
                try:
                    df = pd.read_excel("dividend_database.xlsx", sheet_name="配息記錄")
                    if df.empty:
                        print("📦 配息資料庫為空")
                    else:
                        print(f"📊 配息資料庫共有 {len(df)} 筆記錄")
                        print("\n最近10筆記錄:")
                        print(df.tail(10).to_string(index=False))

                        # 顯示統計資訊
                        total_dividend = df['總配息收益'].sum()
                        print(f"\n💰 總配息收益: {total_dividend:.2f} 元")

                        # 按年月統計
                        monthly_stats = df.groupby('年月')['總配息收益'].sum().sort_index()
                        print("\n📈 月度配息統計:")
                        for year_month, amount in monthly_stats.items():
                            print(f"  {year_month}: {amount:.2f} 元")

                except Exception as e:
                    print(f"❌ 讀取配息資料庫失敗: {e}")
            else:
                print("❌ 配息資料庫不存在")

        elif choice == "3":
            print("👋 感謝使用回朔庫存歷史股息追蹤系統！")
            break

        else:
            print("❌ 無效的選項，請重新選擇")


if __name__ == "__main__":
    main()
