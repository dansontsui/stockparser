import yfinance as yf
import json
import pandas as pd
import logging
import subprocess
import requests
from bs4 import BeautifulSoup
from pytz import timezone
from pathlib import Path
from typing import Optional, Dict, Any
import os
from datetime import datetime

class Config:
    """配置管理類"""
    def __init__(self):
        self.base_path = Path("D:/danson_tsui/Documents/mystock")
        self.log_file = self.base_path / "app.log"
        self.db_file = self.base_path / "db.csv"
        self.history_file = self.base_path / "myhis1.csv"
        
        # 確保目錄存在
        self.base_path.mkdir(parents=True, exist_ok=True)

class Logger:
    """日誌管理類"""
    def __init__(self, config: Config):
        self.config = config
        self._setup_logging()
    
    def _setup_logging(self):
        logging.basicConfig(
            level=logging.INFO, 
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
        file_handler = logging.FileHandler(self.config.log_file)
        file_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        )
        logging.getLogger().addHandler(file_handler)

class DividendDataFetcher:
    """配息資料獲取類"""
    
    @staticmethod
    def get_00751b_dividend() -> Optional[pd.DataFrame]:
        """獲取00751B配息資料"""
        try:
            dd = pd.read_html('https://www.moneydj.com/ETF/X/Basic/Basic0005.xdjhtm?etfid=00751B.TW')
            df = dd[1]
            df.rename(columns={'除息日': 'Date', '配息總額': 'Dividends'}, inplace=True)
            df['Date'] = pd.to_datetime(df['Date'], format='%Y/%m/%d', errors='coerce')
            return df.head(1)
        except Exception as e:
            logging.error(f"獲取00751B配息資料失敗: {e}")
            return None

    @staticmethod
    def get_00937b_dividend() -> Optional[pd.DataFrame]:
        """獲取00937B配息資料"""
        try:
            url = 'https://www.capitalfund.com.tw/etf/product/detail/378/interest'
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            rows = soup.find_all('div', class_='tr')
            
            data = []
            for row in rows:
                cols = row.find_all('div', class_='td')
                cols = [col.text.strip() for col in cols]
                
                # 清理文字
                cleaned_cols = []
                for col in cols:
                    cleaned = col.replace('配息基準日', '').replace('除息交易日', '') \
                               .replace('配息發放日', '').replace('每單位分配金額(元)', '') \
                               .replace('除息日前一日之淨值', '').replace('年化配息率', '') \
                               .replace('配息頻率', '').strip()
                    cleaned_cols.append(cleaned)
                
                if len(cleaned_cols) >= 4:
                    data.append(cleaned_cols)
            
            df = pd.DataFrame(data, columns=[
                '配息基準日', 'Date', '配息發放日', 'Dividends', 
                '除息日前一日之淨值', '年化配息率', '配息頻率'
            ])
            
            df.dropna(axis=0, inplace=True)
            df['Date'] = pd.to_datetime(df['Date'], format='%Y/%m/%d', errors='coerce')
            return df.head(1)
            
        except Exception as e:
            logging.error(f"獲取00937B配息資料失敗: {e}")
            return None

    @staticmethod
    def get_yfinance_dividend(stock_code: str) -> Optional[pd.DataFrame]:
        """使用YFinance獲取配息資料"""
        try:
            dividends = yf.Ticker(stock_code).dividends
            logging.info(f"{stock_code}: {len(dividends)} 筆配息記錄")
            
            if len(dividends) == 0:
                return None
            
            df = pd.Series(dividends).reset_index()
            df['Date'] = pd.to_datetime(df['Date'].dt.strftime('%Y/%m/%d'))
            return df.tail(1)
            
        except Exception as e:
            logging.error(f"獲取{stock_code}配息資料失敗: {e}")
            return None

class DividendCalculator:
    """配息計算類"""
    
    def __init__(self, config: Config):
        self.config = config
        self.df = None
        self.df_history = None
        self.result = None
        
    def load_data(self) -> bool:
        """載入資料"""
        try:
            # 檢查檔案是否存在
            if not self.config.db_file.exists():
                logging.error(f"資料檔案不存在: {self.config.db_file}")
                return False
                
            if not self.config.history_file.exists():
                logging.warning(f"歷史檔案不存在，將建立新檔案: {self.config.history_file}")
                # 建立空的歷史檔案
                empty_df = pd.DataFrame(columns=['id', 'update_date', 'div', 'count', 'Interest'])
                empty_df.to_csv(self.config.history_file, index_label='idx')
            
            self.df = pd.read_csv(self.config.db_file, index_col=None)
            self.df = self.df.reset_index(drop=True)
            self.df['date'] = pd.to_datetime(self.df['date'])
            
            self.df_history = pd.read_csv(self.config.history_file, index_col='idx')
            self.df_history['update_date'] = pd.to_datetime(self.df_history['update_date'])
            
            self.result = self.df.groupby('id').agg({'count': 'sum', 'price': 'mean'})
            
            logging.info(f"載入資料成功: {len(self.df)} 筆交易記錄, {len(self.df_history)} 筆配息記錄")
            return True
            
        except Exception as e:
            logging.error(f"載入資料失敗: {e}")
            return False
    
    def calculate_profit(self, last_date: datetime, div_date: datetime, 
                        dividend: float, stock_id: str) -> bool:
        """計算配息收益"""
        if last_date < div_date:
            count = self.result['count'][stock_id]
            interest = float(dividend) * count * 1000
            
            logging.info(f"股票ID: {stock_id}")
            logging.info(f"持有數量: {count}")
            logging.info(f"配息: {dividend}")
            logging.info(f"利息收入: {interest}")
            
            new_data = {
                'id': stock_id,
                'update_date': div_date,
                'div': dividend,
                'count': count,
                'Interest': interest
            }
            
            self.df_history.loc[len(self.df_history)] = new_data
            return True
        return False
    
    def check_date_exists(self, update_date: datetime) -> bool:
        """檢查日期是否已存在"""
        return update_date in self.df_history['update_date'].values
    
    def save_history(self) -> bool:
        """儲存歷史記錄"""
        try:
            self.df_history.to_csv(self.config.history_file)
            logging.info("歷史記錄儲存成功")
            return True
        except Exception as e:
            logging.error(f"儲存歷史記錄失敗: {e}")
            return False

class DividendTracker:
    """主要的配息追蹤類"""
    
    def __init__(self):
        self.config = Config()
        self.logger = Logger(self.config)
        self.fetcher = DividendDataFetcher()
        self.calculator = DividendCalculator(self.config)
        
    def run(self):
        """執行主要邏輯"""
        logging.info("開始執行配息追蹤程式")
        
        if not self.calculator.load_data():
            logging.error("載入資料失敗，程式結束")
            return
        
        updated = False
        
        for stock_id in self.calculator.result.index:
            stock_code = f"00{stock_id}.TWO"
            logging.info(f"-------------處理 {stock_code}-------------")
            
            # 獲取配息資料
            dividend_data = self._get_dividend_data(stock_id)
            
            if dividend_data is None or len(dividend_data) == 0:
                logging.info('無配息資料需要更新')
                continue
            
            dividend_data = dividend_data.reset_index(drop=True)
            
            # 檢查資料年份
            if dividend_data['Date'][0].year < 2023:
                logging.warning('配息資料年份過舊')
                continue
            
            # 獲取最後交易日期
            last_trade_date = self._get_last_trade_date(stock_id)
            
            # 檢查是否已存在該配息記錄
            if self.calculator.check_date_exists(dividend_data['Date'][0]):
                logging.info('配息記錄已存在，跳過')
                continue
            
            # 計算配息收益
            if self.calculator.calculate_profit(
                last_trade_date, 
                dividend_data['Date'][0],
                dividend_data['Dividends'][0], 
                stock_id
            ):
                updated = True
                logging.info('配息記錄已更新')
            else:
                logging.info('無需更新配息記錄')
        
        # 儲存結果
        if updated:
            if self.calculator.save_history():
                self._open_result_file()
        
        logging.info("配息追蹤程式執行完成")
    
    def _get_dividend_data(self, stock_id: str) -> Optional[pd.DataFrame]:
        """根據股票ID獲取配息資料"""
        if stock_id == '751B':
            return self.fetcher.get_00751b_dividend()
        elif stock_id == '937B':
            return self.fetcher.get_00937b_dividend()
        else:
            stock_code = f"00{stock_id}.TWO"
            return self.fetcher.get_yfinance_dividend(stock_code)
    
    def _get_last_trade_date(self, stock_id: str) -> datetime:
        """獲取最後交易日期"""
        filtered_data = self.calculator.df[self.calculator.df['id'] == stock_id]
        latest_data = filtered_data.sort_values('date').tail(1)
        return latest_data['date'].iloc[0]
    
    def _open_result_file(self):
        """開啟結果檔案"""
        try:
            subprocess.run(['start', str(self.config.history_file)], shell=True)
        except Exception as e:
            logging.error(f"開啟檔案失敗: {e}")

def main():
    """主函數"""
    tracker = DividendTracker()
    tracker.run()

if __name__ == "__main__":
    main()