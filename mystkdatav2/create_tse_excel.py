#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用已獲取的證交所JSON資料創建Excel檔案
"""

import json
import pandas as pd
from datetime import datetime

def create_excel_from_json():
    """從JSON資料創建Excel檔案"""
    
    # 這是從證交所網站獲取的實際JSON資料
    json_data = {
        "date": "20250616~20250716",
        "tables": [{
            "title": "",
            "totalCount": 305,
            "fields": [
                "除權息日期", "代號", "名稱", "除權息前收盤價", "除權息參考價", 
                "權值", "息值", "權值+息值", "權/息", "漲停價", "跌停價", 
                "開始交易基準價", "減除股利參考價", "現金股利", "每仟股無償配股", 
                "現金增資股數", "現金增資認購價", "公開承銷股數", "員工認購股數", 
                "原股東認購股數", "按持股比例仟股認購"
            ],
            "data": [
                ["114/06/16", "00942B", "台新美A公司債20+ ", "13.58", "13.52", "0.000000", "0.064000", "0.064000", "除息", "9999.95", "0.01", "13.52", "13.52", "0.06400000", "0.00000000", "0", "0.00", "0", "0", "0", "0.00000000"],
                ["114/06/16", "00980B", "台新特選IG債10+ ", "9.03", "8.98", "0.000000", "0.053000", "0.053000", "除息", "9999.95", "0.01", "8.98", "8.98", "0.05300000", "0.00000000", "0", "0.00", "0", "0", "0", "0.00000000"],
                ["114/06/16", "3324", "雙鴻 ", "705.00", "695.00", "0.000000", "9.998651", "9.998651", "除息", "764.00", "626.00", "695.00", "695.00", "9.99865134", "0.00000000", "0", "0.00", "0", "0", "0", "0.00000000"],
                ["114/06/17", "00937B", "群益ESG投等債20+ ", "13.94", "13.86", "0.000000", "0.077000", "0.077000", "除息", "9999.95", "0.01", "13.86", "13.86", "0.07700000", "0.00000000", "0", "0.00", "0", "0", "0", "0.00000000"],
                ["114/07/16", "00937B", "群益ESG投等債20+ ", "13.81", "13.74", "0.000000", "0.072000", "0.072000", "除息", "9999.95", "0.01", "13.74", "13.74", "0.07200000", "0.00000000", "0", "0.00", "0", "0", "0", "0.00000000"]
            ]
        }],
        "stat": "ok"
    }
    
    print("🏦 從證交所JSON資料創建Excel檔案")
    print("=" * 60)
    
    # 提取資料
    if 'tables' in json_data and len(json_data['tables']) > 0:
        table = json_data['tables'][0]
        fields = table['fields']
        data = table['data']
        
        print(f"📊 資料資訊:")
        print(f"  查詢期間: {json_data.get('date', 'N/A')}")
        print(f"  總筆數: {table.get('totalCount', len(data))}")
        print(f"  欄位數: {len(fields)}")
        print(f"  實際資料筆數: {len(data)}")
        
        # 顯示欄位
        print(f"\n📋 欄位名稱:")
        for i, field in enumerate(fields):
            print(f"  {i+1:2d}. {field}")
        
        # 創建DataFrame
        df = pd.DataFrame(data, columns=fields)
        
        print(f"\n📈 DataFrame 資訊:")
        print(f"  形狀: {df.shape}")
        
        # 顯示前幾行
        print(f"\n📊 前5行資料預覽:")
        print(df.head().to_string(index=False))
        
        # 生成檔案名稱
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        excel_file = f'證交所除息資料_114_06_16_07_16_{timestamp}.xlsx'
        
        try:
            # 儲存為Excel
            with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
                # 主要資料工作表
                df.to_excel(writer, sheet_name='除息資料', index=False)
                
                # 摘要資訊工作表
                summary_data = {
                    '項目': [
                        '查詢期間',
                        '資料筆數',
                        '欄位數量',
                        '產生時間',
                        '資料來源',
                        '總筆數(原始)'
                    ],
                    '內容': [
                        json_data.get('date', 'N/A'),
                        len(df),
                        len(df.columns),
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "台灣證券交易所 (櫃買中心)",
                        table.get('totalCount', len(data))
                    ]
                }
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='摘要資訊', index=False)
                
                # 欄位說明工作表
                fields_data = {
                    '序號': range(1, len(fields) + 1),
                    '欄位名稱': fields,
                    '資料類型': [str(df[field].dtype) for field in fields],
                    '非空值數量': [df[field].count() for field in fields],
                    '範例值': [str(df[field].iloc[0]) if len(df) > 0 else '' for field in fields]
                }
                fields_df = pd.DataFrame(fields_data)
                fields_df.to_excel(writer, sheet_name='欄位說明', index=False)
            
            print(f"\n✅ Excel檔案已儲存: {excel_file}")
            print(f"📊 包含 {len(df)} 筆資料，{len(df.columns)} 個欄位")
            print(f"📁 工作表: 除息資料、摘要資訊、欄位說明")
            
            # 顯示統計資訊
            print(f"\n📈 資料統計:")
            print(f"  總記錄數: {len(df):,}")
            print(f"  日期範圍: {df['除權息日期'].min()} ~ {df['除權息日期'].max()}")
            
            # 統計除息股票
            dividend_stocks = df[df['息值'].astype(float) > 0]
            print(f"  有配息股票: {len(dividend_stocks)} 檔")
            
            if len(dividend_stocks) > 0:
                print(f"  配息範圍: {dividend_stocks['息值'].astype(float).min():.6f} ~ {dividend_stocks['息值'].astype(float).max():.6f} 元")
            
            # 顯示一些有配息的股票範例
            print(f"\n💰 配息股票範例:")
            for _, row in dividend_stocks.head(10).iterrows():
                print(f"  {row['代號']} ({row['名稱'].strip()}): {float(row['息值']):.6f} 元")
            
            return excel_file
            
        except Exception as e:
            print(f"❌ 儲存Excel失敗: {e}")
            return None
    
    else:
        print("❌ JSON資料格式錯誤")
        return None

if __name__ == "__main__":
    create_excel_from_json()
