#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
調試配息追蹤器統計功能
"""

import os
from historical_dividend_tracker import HistoricalDividendTracker

def debug_tracker_statistics():
    """調試追蹤器統計功能"""
    print("🔍 調試配息追蹤器統計功能")
    print("=" * 50)
    
    # 建立追蹤器
    tracker = HistoricalDividendTracker()
    
    # 檢查方法是否存在
    print("📋 檢查追蹤器方法:")
    methods = [
        'track_historical_dividends',
        'track_historical_dividends_range',
        'track_dividend_by_actual_dates'
    ]
    
    for method in methods:
        if hasattr(tracker, method):
            print(f"   ✅ {method}: 存在")
        else:
            print(f"   ❌ {method}: 不存在")
    
    # 檢查統計模組
    print(f"\n📊 檢查統計模組:")
    try:
        from dividend_statistics import DividendStatistics
        print("   ✅ dividend_statistics 模組: 可以導入")
        
        # 檢查統計類
        stats = DividendStatistics()
        if hasattr(stats, 'generate_all_statistics'):
            print("   ✅ generate_all_statistics 方法: 存在")
        else:
            print("   ❌ generate_all_statistics 方法: 不存在")
            
    except ImportError as e:
        print(f"   ❌ dividend_statistics 模組: 導入失敗 - {e}")
    except Exception as e:
        print(f"   ❌ 統計模組檢查失敗: {e}")
    
    # 檢查配息資料庫
    print(f"\n📁 檢查配息資料庫:")
    database_file = 'dividend_database.xlsx'
    
    if os.path.exists(database_file):
        print(f"   ✅ {database_file}: 存在")
        
        try:
            import pandas as pd
            df = pd.read_excel(database_file, sheet_name='配息記錄')
            print(f"   📊 配息記錄: {len(df)} 筆")
            
            if len(df) > 0:
                print("   ✅ 有配息資料可以統計")
            else:
                print("   ⚠️  配息資料為空")
                
        except Exception as e:
            print(f"   ❌ 讀取配息資料失敗: {e}")
    else:
        print(f"   ❌ {database_file}: 不存在")
    
    # 測試統計功能調用
    print(f"\n🧪 測試統計功能調用:")
    
    try:
        from dividend_statistics import DividendStatistics
        stats = DividendStatistics()
        
        print("   📊 嘗試生成統計報表...")
        success = stats.generate_all_statistics()
        
        if success:
            print("   ✅ 統計報表生成成功！")
        else:
            print("   ❌ 統計報表生成失敗！")
            
    except Exception as e:
        print(f"   ❌ 統計功能調用失敗: {e}")
        import traceback
        traceback.print_exc()

def test_manual_statistics():
    """手動測試統計功能"""
    print(f"\n🔧 手動測試統計功能")
    print("=" * 50)
    
    try:
        print("📊 導入統計模組...")
        from dividend_statistics import DividendStatistics
        
        print("📊 建立統計分析器...")
        stats = DividendStatistics()
        
        print("📊 執行統計分析...")
        success = stats.generate_all_statistics()
        
        if success:
            print("✅ 手動統計測試成功！")
            print("📁 請檢查 dividend_database.xlsx 是否有新的統計工作表")
        else:
            print("❌ 手動統計測試失敗！")
            
    except Exception as e:
        print(f"❌ 手動統計測試失敗: {e}")
        import traceback
        traceback.print_exc()

def main():
    """主函數"""
    print("🔍 配息追蹤器統計功能調試")
    print("=" * 40)
    
    debug_tracker_statistics()
    test_manual_statistics()
    
    print(f"\n💡 如果統計功能正常，但在追蹤器中沒有被調用，")
    print("可能的原因:")
    print("1. track_historical_dividends 方法返回 False")
    print("2. 統計模組導入失敗")
    print("3. 配息資料庫不存在或為空")
    print("4. 代碼修改沒有正確保存")

if __name__ == "__main__":
    main()
