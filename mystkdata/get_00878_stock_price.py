#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自動獲取00878近一個月股價並存入SQLite資料庫
"""

import requests
import sqlite3
import pandas as pd
import json
import time
import random
from datetime import datetime, timedelta
from io import StringIO
import logging

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('00878_stock_price.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 設定多個User-Agent
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1'
]

class Stock00878Fetcher:
    def __init__(self, db_file='stock_data.db'):
        self.db_file = db_file
        self.stock_code = '00878'
        self.stock_name = '國泰永續高股息'
        self._init_database()
    
    def _init_database(self):
        """初始化資料庫，建立股價資料表"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS stock_prices (
                        date TEXT,
                        stock_code TEXT,
                        stock_name TEXT,
                        trade_volume INTEGER,
                        trade_value INTEGER,
                        open_price REAL,
                        high_price REAL,
                        low_price REAL,
                        close_price REAL,
                        price_change REAL,
                        transaction_count INTEGER,
                        created_date TEXT,
                        PRIMARY KEY (date, stock_code)
                    )
                ''')
                logger.info("資料庫初始化完成")
        except Exception as e:
            logger.error(f"資料庫初始化失敗: {e}")
            raise
    
    def _get_date_range(self, days=30):
        """取得日期範圍 (近30天)"""
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        return start_date, end_date
    
    def _fetch_monthly_data(self, year_month):
        """獲取指定年月的股價資料"""
        url = f'https://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&date={year_month}&stockNo={self.stock_code}'
        
        headers = {
            'User-Agent': random.choice(USER_AGENTS)
        }
        
        retries = 0
        max_retries = 3
        
        while retries < max_retries:
            try:
                time.sleep(random.uniform(2, 5))  # 延迟2到5秒
                response = requests.get(url, headers=headers, timeout=30)
                response.raise_for_status()
                
                data = response.json()
                
                if data.get('stat') == 'OK' and data.get('data'):
                    df = pd.DataFrame(data['data'], columns=data['fields'])
                    logger.info(f"成功獲取 {year_month} 的資料，共 {len(df)} 筆")
                    return df
                else:
                    logger.warning(f"API回應無資料: {data.get('stat', 'Unknown')}")
                    return pd.DataFrame()
                    
            except requests.exceptions.RequestException as e:
                retries += 1
                logger.warning(f"請求失敗 (第{retries}次重試): {e}")
                if retries < max_retries:
                    time.sleep(5)
                    headers['User-Agent'] = random.choice(USER_AGENTS)
                else:
                    logger.error(f"獲取 {year_month} 資料失敗，已重試 {max_retries} 次")
                    return pd.DataFrame()
            except Exception as e:
                logger.error(f"處理 {year_month} 資料時發生錯誤: {e}")
                return pd.DataFrame()
        
        return pd.DataFrame()
    
    def _process_data(self, df):
        """處理和清理股價資料"""
        if df.empty:
            return df
        
        try:
            # 重新命名欄位
            column_mapping = {
                '日期': 'date',
                '成交股數': 'trade_volume',
                '成交金額': 'trade_value', 
                '開盤價': 'open_price',
                '最高價': 'high_price',
                '最低價': 'low_price',
                '收盤價': 'close_price',
                '漲跌價差': 'price_change',
                '成交筆數': 'transaction_count'
            }
            
            df = df.rename(columns=column_mapping)
            
            # 轉換日期格式 (民國年轉西元年)
            df['date'] = df['date'].apply(self._convert_roc_to_ad)
            
            # 清理數值欄位 (移除逗號並轉換為數值)
            numeric_columns = ['trade_volume', 'trade_value', 'open_price', 'high_price', 
                             'low_price', 'close_price', 'price_change', 'transaction_count']
            
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = df[col].astype(str).str.replace(',', '').str.replace('--', '0')
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # 添加股票代號和名稱
            df['stock_code'] = self.stock_code
            df['stock_name'] = self.stock_name
            df['created_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            logger.info(f"資料處理完成，共 {len(df)} 筆")
            return df
            
        except Exception as e:
            logger.error(f"資料處理失敗: {e}")
            return pd.DataFrame()
    
    def _convert_roc_to_ad(self, roc_date):
        """轉換民國年日期為西元年日期"""
        try:
            # 格式: 113/07/15 -> 2024-07-15
            parts = roc_date.split('/')
            year = int(parts[0]) + 1911
            month = int(parts[1])
            day = int(parts[2])
            return f"{year:04d}-{month:02d}-{day:02d}"
        except:
            return roc_date
    
    def _save_to_database(self, df):
        """將資料存入SQLite資料庫"""
        if df.empty:
            logger.warning("無資料可存入資料庫")
            return 0
        
        try:
            with sqlite3.connect(self.db_file) as conn:
                # 使用 INSERT OR REPLACE 避免重複資料
                df.to_sql('stock_prices', conn, if_exists='append', index=False, method='multi')
                
                # 移除重複資料
                conn.execute('''
                    DELETE FROM stock_prices 
                    WHERE rowid NOT IN (
                        SELECT MIN(rowid) 
                        FROM stock_prices 
                        GROUP BY date, stock_code
                    )
                ''')
                
                saved_count = len(df)
                logger.info(f"成功存入 {saved_count} 筆資料到資料庫")
                return saved_count
                
        except Exception as e:
            logger.error(f"存入資料庫失敗: {e}")
            return 0
    
    def fetch_recent_data(self, days=30):
        """獲取近期股價資料"""
        logger.info(f"開始獲取 {self.stock_code} 近 {days} 天的股價資料")
        
        start_date, end_date = self._get_date_range(days)
        logger.info(f"日期範圍: {start_date} 到 {end_date}")
        
        # 取得需要查詢的年月列表
        year_months = self._get_year_months(start_date, end_date)
        
        all_data = []
        
        for year_month in year_months:
            logger.info(f"正在獲取 {year_month} 的資料...")
            df = self._fetch_monthly_data(year_month)
            
            if not df.empty:
                processed_df = self._process_data(df)
                if not processed_df.empty:
                    # 篩選日期範圍內的資料
                    processed_df = processed_df[
                        (processed_df['date'] >= start_date.strftime('%Y-%m-%d')) &
                        (processed_df['date'] <= end_date.strftime('%Y-%m-%d'))
                    ]
                    all_data.append(processed_df)
        
        if all_data:
            final_df = pd.concat(all_data, ignore_index=True)
            final_df = final_df.sort_values('date')
            
            saved_count = self._save_to_database(final_df)
            logger.info(f"總共處理 {len(final_df)} 筆資料，成功存入 {saved_count} 筆")
            
            return final_df
        else:
            logger.warning("未獲取到任何資料")
            return pd.DataFrame()
    
    def _get_year_months(self, start_date, end_date):
        """取得日期範圍內的年月列表"""
        year_months = []
        current = start_date.replace(day=1)
        
        while current <= end_date:
            year_months.append(current.strftime('%Y%m01'))
            # 移到下個月
            if current.month == 12:
                current = current.replace(year=current.year + 1, month=1)
            else:
                current = current.replace(month=current.month + 1)
        
        return year_months
    
    def view_recent_data(self, limit=10):
        """查看最近的股價資料"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                query = '''
                    SELECT date, stock_code, stock_name, open_price, high_price, 
                           low_price, close_price, trade_volume, price_change
                    FROM stock_prices 
                    WHERE stock_code = ?
                    ORDER BY date DESC 
                    LIMIT ?
                '''
                df = pd.read_sql_query(query, conn, params=[self.stock_code, limit])
                
                if not df.empty:
                    print(f"\n=== {self.stock_code} 最近 {limit} 天股價資料 ===")
                    print(df.to_string(index=False))
                    return df
                else:
                    print(f"資料庫中無 {self.stock_code} 的資料")
                    return pd.DataFrame()
                    
        except Exception as e:
            logger.error(f"查詢資料失敗: {e}")
            return pd.DataFrame()

def main():
    """主程式"""
    try:
        fetcher = Stock00878Fetcher()
        
        # 獲取近30天的股價資料
        df = fetcher.fetch_recent_data(days=30)
        
        if not df.empty:
            print(f"\n成功獲取並存入 {len(df)} 筆 00878 股價資料")
            
            # 顯示最近10天的資料
            fetcher.view_recent_data(limit=10)
        else:
            print("未能獲取到股價資料")
            
    except Exception as e:
        logger.error(f"程式執行失敗: {e}")
        print(f"程式執行失敗: {e}")

if __name__ == "__main__":
    main()
