
import numpy as np
import pandas as pd
import io
import requests
import datetime as dt
import json
from typing import Optional, Tuple
import logging
import sqlite3

# 設定日誌 - 輸出到檔案
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('stock_dividend_update.log', encoding='utf-8'),
        logging.StreamHandler()  # 同時輸出到控制台
    ]
)
logger = logging.getLogger(__name__)

class StockDividendUpdater:
    def __init__(self, history_file: str = 'myhistory.csv', db_file: str = 'stock_data.db'):
        self.history_file = history_file
        self.db_file = db_file
        self.mystk_his = None
        self.twse_div_data = None
        self.otc_div_data = None
        self._init_database()
        
    def _init_database(self):
        """初始化資料庫"""
        with sqlite3.connect(self.db_file) as conn:
            # 建立上市股利資料表
            conn.execute('''
                CREATE TABLE IF NOT EXISTS twse_dividend (
                    date TEXT,
                    stock_code TEXT,
                    stock_name TEXT,
                    close_price REAL,
                    ref_price REAL,
                    dividend_value REAL,
                    high_limit REAL,
                    low_limit REAL,
                    open_ref REAL,
                    ex_dividend_ref REAL,
                    net_value REAL,
                    divide_ratio REAL,
                    created_date TEXT,
                    PRIMARY KEY (date, stock_code)
                )
            ''')
            
            # 建立上櫃股利資料表
            conn.execute('''
                CREATE TABLE IF NOT EXISTS otc_dividend (
                    ex_date TEXT,
                    stock_code TEXT,
                    stock_name TEXT,
                    close_price REAL,
                    ref_price REAL,
                    right_value REAL,
                    dividend_value REAL,
                    total_value REAL,
                    high_limit REAL,
                    low_limit REAL,
                    open_ref REAL,
                    ex_dividend_ref REAL,
                    cash_dividend REAL,
                    divide_ratio REAL,
                    created_date TEXT,
                    PRIMARY KEY (ex_date, stock_code)
                )
            ''')
        
    def load_data(self):
        """載入歷史資料"""
        try:
            self.mystk_his = pd.read_csv(self.history_file, index_col=0).reset_index(drop=True)
            logger.info(f"載入歷史資料: {len(self.mystk_his)} 筆")
        except FileNotFoundError:
            logger.error(f"找不到檔案: {self.history_file}")
            raise
            
    def get_dividend_data(self):
        """取得股利資料"""
        self.otc_div_data = self._get_otc_div_data()
        self.twse_div_data = self._get_twse_div_data()
        
    def _get_date_range(self, days: int = 30) -> Tuple[str, str]:
        """取得日期範圍"""
        today = dt.datetime.now().date()
        days_ago = today - dt.timedelta(days=days)
        return days_ago, today
        
    def _get_twse_div_data(self) -> pd.DataFrame:
        """取得上市股利資料"""
        start_date, end_date = self._get_date_range()
        start_datestr = start_date.strftime('%Y%m%d')
        end_datestr = end_date.strftime('%Y%m%d')
        
        url = f"https://www.twse.com.tw/rwd/zh/exRight/TWT49U?startDate={start_datestr}&endDate={end_datestr}&response=csv"
        
        try:
            res = requests.get(url, timeout=30)
            df = pd.read_csv(io.StringIO(res.text.replace("=", "")), header=1)
            df = df.dropna(thresh=5).dropna(how='all', axis=1)
            df = df[~df['資料日期'].isnull()]
            
            # 處理日期
            years = df['資料日期'].str.split('年').str[0].astype(int)
            years.loc[df['資料日期'].str.find('年') == -1] = np.nan
            years.loc[years > dt.datetime.now().year] = np.nan
            years.ffill(inplace=True)
            
            dates = years.astype(int).astype(str) + '/' + df['資料日期'].str.split('年').str[1].str.replace('月', '/').str.replace('日', '')
            df['date'] = dates
            
            # 轉換數值欄位
            float_cols = ['除權息前收盤價', '除權息參考價', '權值+息值', '漲停價格', '跌停價格', '開盤競價基準', '減除股利參考價', '最近一次申報每股 (單位)淨值']
            df[float_cols] = df[float_cols].astype(str).apply(lambda s: s.str.replace(',', '')).astype(float)
            df['twse_divide_ratio'] = df['除權息前收盤價'] / df['開盤競價基準']
            
            # 儲存到SQLite
            self._save_twse_to_db(df, end_date)
            return df
        
        except Exception as e:
            logger.error(f"取得上市股利資料失敗: {e}")
            return pd.DataFrame()

    def _save_twse_to_db(self, df: pd.DataFrame, end_date):
        """儲存上市股利資料到資料庫"""
        if df.empty:
            return
        
        with sqlite3.connect(self.db_file) as conn:
            for _, row in df.iterrows():
                conn.execute('''
                    INSERT OR REPLACE INTO twse_dividend 
                    (date, stock_code, stock_name, close_price, ref_price, dividend_value, 
                     high_limit, low_limit, open_ref, ex_dividend_ref, net_value, divide_ratio, created_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    row['date'], row['股票代號'], row['股票名稱'],
                    row['除權息前收盤價'], row['除權息參考價'], row['權值+息值'],
                    row['漲停價格'], row['跌停價格'], row['開盤競價基準'],
                    row['減除股利參考價'], row['最近一次申報每股 (單位)淨值'],
                    row['twse_divide_ratio'], str(end_date)
                ))
        logger.info(f"上市股利資料已儲存到資料庫: {len(df)} 筆")
            
    def _get_otc_div_data(self) -> pd.DataFrame:
        """取得上櫃股利資料"""
        start_date, end_date = self._get_date_range()
        
        # 轉換為民國年格式
        start_roc = f"{start_date.year-1911:02d}/{start_date.month:02d}/{start_date.day:02d}"
        end_roc = f"{end_date.year-1911:02d}/{end_date.month:02d}/{end_date.day:02d}"
        
        url = f'https://www.tpex.org.tw/web/stock/exright/dailyquo/exDailyQ_result.php?l=zh-tw&d={start_roc}&ed={end_roc}'
        
        try:
            res = requests.get(url, timeout=30)
            data = json.loads(res.text)['tables'][0]['data']
            
            df = pd.DataFrame(data)
            df.columns = ['除權息日期', '代號', '名稱', '除權息前收盤價', '除權息參考價', '權值', '息值', "權+息值", "權/息", "漲停價格", "跌停價格", "開盤競價基準", "減除股利參考價", "現金股利", "每千股無償配股", "現金增資股數", "現金增資認購價", "公開承銷股數", "員工認購股數", "原股東認購數", "按持股比例千股認購"]
            
            # 轉換數值欄位
            float_cols = ['除權息前收盤價', '除權息參考價', '權值', '息值', "權+息值", "漲停價格", "跌停價格", "開盤競價基準", "減除股利參考價", "現金股利", "每千股無償配股", "現金增資股數", "現金增資認購價", "公開承銷股數", "員工認購股數", "原股東認購數", "按持股比例千股認購"]
            df[float_cols] = df[float_cols].astype(str).apply(lambda s: s.str.replace(',', '')).astype(float)
            
            # 處理日期和股票代號
            df['stock_id'] = df['代號'] + ' ' + df['名稱']
            dates = df['除權息日期'].str.split('/')
            dates = (dates.str[0].astype(int) + 1911).astype(str) + '/' + dates.str[1] + '/' + dates.str[2]
            df['date'] = pd.to_datetime(dates)
            df['otc_divide_ratio'] = df['除權息前收盤價'] / df['開盤競價基準']
            
            # 儲存到SQLite
            self._save_otc_to_db(df, end_date)
            return df
        
        except Exception as e:
            logger.error(f"取得上櫃股利資料失敗: {e}")
            return pd.DataFrame()

    def _save_otc_to_db(self, df: pd.DataFrame, end_date):
        """儲存上櫃股利資料到資料庫"""
        if df.empty:
            return
        
        with sqlite3.connect(self.db_file) as conn:
            for _, row in df.iterrows():
                conn.execute('''
                    INSERT OR REPLACE INTO otc_dividend 
                    (ex_date, stock_code, stock_name, close_price, ref_price, right_value, 
                     dividend_value, total_value, high_limit, low_limit, open_ref, 
                     ex_dividend_ref, cash_dividend, divide_ratio, created_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    row['除權息日期'], row['代號'], row['名稱'],
                    row['除權息前收盤價'], row['除權息參考價'], row['權值'],
                    row['息值'], row['權+息值'], row['漲停價格'], row['跌停價格'],
                    row['開盤競價基準'], row['減除股利參考價'], row['現金股利'],
                    row['otc_divide_ratio'], str(end_date)
                ))
        logger.info(f"上櫃股利資料已儲存到資料庫: {len(df)} 筆")
    
    def _update_stock_interest(self, stkid: str, div_data: pd.DataFrame, div_col: str, date_col: str, code_col: str) -> None:
        """統一的股利更新邏輯"""
        # 檢查 stkid 是否為有效值
        if pd.isna(stkid) or stkid is None or not isinstance(stkid, str):
            logger.warning(f"跳過無效的股票代號: {stkid}")
            return
        
        clean_stkid = stkid.replace('X', '')
        stkinfo = div_data[div_data[code_col] == clean_stkid]
        
        if len(stkinfo) == 0:
            return
        
        mystk_his1 = self.mystk_his[self.mystk_his['stkid'] == stkid]
        if len(mystk_his1) == 0:
            return
        
        min_date = mystk_his1["date"].min()
        
        for idx in stkinfo.index:
            date_str = stkinfo[date_col][idx]
            div_value = stkinfo[div_col][idx]
            
            if pd.isna(div_value) or div_value == 0:
                continue
            
            year_month = '/'.join(date_str.split('/')[:2])
            
            # 日期比較
            if not self._is_valid_date(year_month, min_date):
                continue
            
            # 更新或新增記錄
            self._update_or_insert_record(mystk_his1, stkid, year_month, div_value)
    
    def _is_valid_date(self, target_date: str, min_date: str) -> bool:
        """檢查日期是否有效"""
        try:
            target_year = int(target_date.split('/')[0]) + 1911
            min_year = int(min_date.split('/')[0]) + 1911
            
            target_full = f"{target_year}/{target_date.split('/')[1]}"
            min_full = f"{min_year}/{min_date.split('/')[1]}"
            
            date_format = '%Y/%m'
            target_dt = dt.datetime.strptime(target_full, date_format)
            min_dt = dt.datetime.strptime(min_full, date_format)
            
            return target_dt >= min_dt
        except:
            return False
    
    def _update_or_insert_record(self, mystk_his1: pd.DataFrame, stkid: str, year_month: str, div_value: float) -> None:
        """更新或插入記錄"""
        existing_idx = mystk_his1.index[mystk_his1["date"] == year_month]
        
        if len(existing_idx) == 0:
            # 新增記錄
            cumulative_sum = mystk_his1['Qty'].sum()
            new_record = {
                'date': year_month, 
                'Qty': 0, 
                'stkid': stkid, 
                'stkdiv': div_value, 
                'Interest': div_value * cumulative_sum * 1000
            }
            self.mystk_his = pd.concat([self.mystk_his, pd.DataFrame([new_record])], ignore_index=True)
        else:
            # 更新現有記錄
            idx = existing_idx[0]
            cumulative_sum = mystk_his1.loc[:idx, 'Qty'].sum()
            self.mystk_his.loc[idx, 'stkdiv'] = div_value
            self.mystk_his.loc[idx, 'Interest'] = div_value * cumulative_sum * 1000
    
    def update_all_stocks(self):
        """更新所有股票的股利資料"""
        # 過濾掉無效的股票代號
        stock_ids = self.mystk_his['stkid'].dropna().unique()
        stock_ids = [sid for sid in stock_ids if isinstance(sid, str) and sid.strip()]
        
        for stkid in stock_ids:
            logger.info(f"處理股票: {stkid}")
            
            # 先嘗試上櫃資料
            self._update_stock_interest(
                stkid, self.otc_div_data, '息值', '除權息日期', '代號'
            )
            
            # 如果上櫃沒有資料，嘗試上市資料
            if len(self.otc_div_data[self.otc_div_data['代號'] == stkid.replace('X', '')]) == 0:
                self._update_stock_interest(
                    stkid, self.twse_div_data, '權值+息值', 'date', '股票代號'
                )
    
    def save_results(self):
        """儲存結果"""
        self.mystk_his.to_csv(self.history_file)
        
        # 產生Excel報表
        with pd.ExcelWriter('output.xlsx', engine='xlsxwriter') as writer:
            # 按日期和股票分組
            summary1 = self.mystk_his.groupby(['date', 'stkid']).agg({
                'Qty': 'sum', 'Interest': 'sum'
            })
            summary1.to_excel(writer, sheet_name='sumbydate_stkid')
            
            # 按股票分組
            summary2 = self.mystk_his.groupby(['stkid']).agg({
                'Qty': 'sum', 'Interest': 'sum'
            })
            summary2.to_excel(writer, sheet_name='sumbystkid')
            
            # 按日期分組
            summary3 = self.mystk_his.groupby(['date']).agg({
                'Interest': 'sum'
            })
            summary3.to_excel(writer, sheet_name='sumbydate')
        
        logger.info("結果已儲存")

    def print_latest_data(self):
        """從SQLite讀取並印出最新資料"""
        logger.info("開始讀取SQLite最新資料")
        try:
            with sqlite3.connect(self.db_file) as conn:
                # 印出最新的上市股利資料
                print("\n=== 最新上市股利資料 ===")
                logger.info("查詢上市股利資料")
                twse_query = '''
                    SELECT date, stock_code, stock_name, dividend_value, divide_ratio
                    FROM twse_dividend 
                    ORDER BY date DESC 
                    LIMIT 10
                '''
                twse_df = pd.read_sql_query(twse_query, conn)
                if not twse_df.empty:
                    print(twse_df.to_string(index=False))
                    logger.info(f"找到 {len(twse_df)} 筆上市股利資料")
                else:
                    print("無上市股利資料")
                    logger.warning("無上市股利資料")
                
                # 印出最新的上櫃股利資料
                print("\n=== 最新上櫃股利資料 ===")
                logger.info("查詢上櫃股利資料")
                otc_query = '''
                    SELECT ex_date, stock_code, stock_name, dividend_value, divide_ratio
                    FROM otc_dividend 
                    ORDER BY ex_date DESC 
                    LIMIT 10
                '''
                otc_df = pd.read_sql_query(otc_query, conn)
                if not otc_df.empty:
                    print(otc_df.to_string(index=False))
                    logger.info(f"找到 {len(otc_df)} 筆上櫃股利資料")
                else:
                    print("無上櫃股利資料")
                    logger.warning("無上櫃股利資料")
                
                # 印出資料庫統計資訊
                print("\n=== 資料庫統計 ===")
                logger.info("查詢資料庫統計資訊")
                stats_query = '''
                    SELECT 
                        '上市' as market,
                        COUNT(*) as total_records,
                        COUNT(DISTINCT stock_code) as unique_stocks,
                        MIN(date) as earliest_date,
                        MAX(date) as latest_date
                    FROM twse_dividend
                    UNION ALL
                    SELECT 
                        '上櫃' as market,
                        COUNT(*) as total_records,
                        COUNT(DISTINCT stock_code) as unique_stocks,
                        MIN(ex_date) as earliest_date,
                        MAX(ex_date) as latest_date
                    FROM otc_dividend
                '''
                stats_df = pd.read_sql_query(stats_query, conn)
                print(stats_df.to_string(index=False))
                logger.info("資料庫統計資訊查詢完成")
                
            logger.info("SQLite資料讀取完成")
            
        except Exception as e:
            logger.error(f"讀取SQLite資料失敗: {e}")

def main():
    """主程式"""
    updater = StockDividendUpdater()
    
    try:
        updater.load_data()
        updater.get_dividend_data()
        updater.update_all_stocks()
        updater.save_results()
        
        print(updater.mystk_his.head(20))
        
        updater.print_latest_data()
        
    except Exception as e:
        logger.error(f"程式執行失敗: {e}")
        raise

if __name__ == "__main__":
    main()





