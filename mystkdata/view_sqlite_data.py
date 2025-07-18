import sqlite3
import pandas as pd
import logging

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('sqlite_viewer.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SQLiteViewer:
    def __init__(self, db_file: str = 'stock_data.db'):
        self.db_file = db_file
        
    def get_table_info(self):
        """取得資料庫中所有表格資訊"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                # 取得所有表格名稱
                tables_query = "SELECT name FROM sqlite_master WHERE type='table'"
                tables = pd.read_sql_query(tables_query, conn)
                
                print("=== 資料庫表格資訊 ===")
                for table_name in tables['name']:
                    print(f"\n表格: {table_name}")
                    
                    # 取得表格結構
                    schema_query = f"PRAGMA table_info({table_name})"
                    schema = pd.read_sql_query(schema_query, conn)
                    print("欄位結構:")
                    print(schema[['name', 'type', 'notnull', 'pk']].to_string(index=False))
                    
                    # 取得資料筆數
                    count_query = f"SELECT COUNT(*) as count FROM {table_name}"
                    count = pd.read_sql_query(count_query, conn)
                    print(f"資料筆數: {count['count'].iloc[0]}")
                    
        except Exception as e:
            logger.error(f"取得表格資訊失敗: {e}")
    
    def view_all_twse_data(self):
        """顯示所有上市股利資料"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                query = '''
                    SELECT * FROM twse_dividend 
                    ORDER BY date DESC, stock_code
                '''
                df = pd.read_sql_query(query, conn)
                
                print("\n=== 所有上市股利資料 ===")
                if not df.empty:
                    print(f"總筆數: {len(df)}")
                    print(df.to_string(index=False))
                    
                    # 統計資訊
                    print(f"\n統計資訊:")
                    print(f"股票數量: {df['stock_code'].nunique()}")
                    print(f"日期範圍: {df['date'].min()} ~ {df['date'].max()}")
                    print(f"平均股利: {df['dividend_value'].mean():.4f}")
                else:
                    print("無上市股利資料")
                    
        except Exception as e:
            logger.error(f"查詢上市資料失敗: {e}")
    
    def view_all_otc_data(self):
        """顯示所有上櫃股利資料"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                query = '''
                    SELECT * FROM otc_dividend 
                    ORDER BY ex_date DESC, stock_code
                '''
                df = pd.read_sql_query(query, conn)
                
                print("\n=== 所有上櫃股利資料 ===")
                if not df.empty:
                    print(f"總筆數: {len(df)}")
                    print(df.to_string(index=False))
                    
                    # 統計資訊
                    print(f"\n統計資訊:")
                    print(f"股票數量: {df['stock_code'].nunique()}")
                    print(f"日期範圍: {df['ex_date'].min()} ~ {df['ex_date'].max()}")
                    print(f"平均股利: {df['dividend_value'].mean():.4f}")
                else:
                    print("無上櫃股利資料")
                    
        except Exception as e:
            logger.error(f"查詢上櫃資料失敗: {e}")
    
    def search_by_stock_code(self, stock_code: str):
        """依股票代號查詢"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                # 查詢上市
                twse_query = '''
                    SELECT 'TWSE' as market, date as ex_date, stock_code, stock_name, 
                           dividend_value, divide_ratio
                    FROM twse_dividend 
                    WHERE stock_code = ?
                    ORDER BY date DESC
                '''
                twse_df = pd.read_sql_query(twse_query, conn, params=[stock_code])
                
                # 查詢上櫃
                otc_query = '''
                    SELECT 'OTC' as market, ex_date, stock_code, stock_name, 
                           dividend_value, divide_ratio
                    FROM otc_dividend 
                    WHERE stock_code = ?
                    ORDER BY ex_date DESC
                '''
                otc_df = pd.read_sql_query(otc_query, conn, params=[stock_code])
                
                print(f"\n=== 股票代號 {stock_code} 的股利資料 ===")
                
                if not twse_df.empty or not otc_df.empty:
                    combined_df = pd.concat([twse_df, otc_df], ignore_index=True)
                    combined_df = combined_df.sort_values('ex_date', ascending=False)
                    print(combined_df.to_string(index=False))
                else:
                    print(f"找不到股票代號 {stock_code} 的資料")
                    
        except Exception as e:
            logger.error(f"查詢股票代號失敗: {e}")
    
    def export_to_excel(self, filename: str = 'sqlite_data_export.xlsx'):
        """匯出所有資料到Excel"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                with pd.ExcelWriter(filename, engine='xlsxwriter') as writer:
                    # 匯出上市資料
                    twse_df = pd.read_sql_query('SELECT * FROM twse_dividend ORDER BY date DESC', conn)
                    if not twse_df.empty:
                        twse_df.to_excel(writer, sheet_name='上市股利', index=False)
                    
                    # 匯出上櫃資料
                    otc_df = pd.read_sql_query('SELECT * FROM otc_dividend ORDER BY ex_date DESC', conn)
                    if not otc_df.empty:
                        otc_df.to_excel(writer, sheet_name='上櫃股利', index=False)
                    
                    # 統計摘要
                    summary_data = []
                    if not twse_df.empty:
                        summary_data.append({
                            '市場': '上市',
                            '總筆數': len(twse_df),
                            '股票數量': twse_df['stock_code'].nunique(),
                            '平均股利': twse_df['dividend_value'].mean(),
                            '最早日期': twse_df['date'].min(),
                            '最晚日期': twse_df['date'].max()
                        })
                    
                    if not otc_df.empty:
                        summary_data.append({
                            '市場': '上櫃',
                            '總筆數': len(otc_df),
                            '股票數量': otc_df['stock_code'].nunique(),
                            '平均股利': otc_df['dividend_value'].mean(),
                            '最早日期': otc_df['ex_date'].min(),
                            '最晚日期': otc_df['ex_date'].max()
                        })
                    
                    if summary_data:
                        summary_df = pd.DataFrame(summary_data)
                        summary_df.to_excel(writer, sheet_name='統計摘要', index=False)
                
                print(f"資料已匯出到 {filename}")
                logger.info(f"資料匯出完成: {filename}")
                
        except Exception as e:
            logger.error(f"匯出資料失敗: {e}")

def main():
    """主程式"""
    viewer = SQLiteViewer()
    
    while True:
        print("\n=== SQLite 資料檢視器 ===")
        print("1. 顯示表格資訊")
        print("2. 顯示所有上市股利資料")
        print("3. 顯示所有上櫃股利資料")
        print("4. 依股票代號查詢")
        print("5. 匯出到Excel")
        print("0. 離開")
        
        choice = input("\n請選擇功能 (0-5): ").strip()
        
        if choice == '0':
            print("程式結束")
            break
        elif choice == '1':
            viewer.get_table_info()
        elif choice == '2':
            viewer.view_all_twse_data()
        elif choice == '3':
            viewer.view_all_otc_data()
        elif choice == '4':
            stock_code = input("請輸入股票代號: ").strip()
            if stock_code:
                viewer.search_by_stock_code(stock_code)
        elif choice == '5':
            filename = input("請輸入檔案名稱 (預設: sqlite_data_export.xlsx): ").strip()
            if not filename:
                filename = 'sqlite_data_export.xlsx'
            viewer.export_to_excel(filename)
        else:
            print("無效的選擇，請重新輸入")

if __name__ == "__main__":
    main()