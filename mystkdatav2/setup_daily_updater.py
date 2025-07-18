#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
設定每日配息自動更新器
"""

import subprocess
import sys
import os
from pathlib import Path

def install_dependencies():
    """安裝必要的依賴套件"""
    print("📦 安裝必要的依賴套件...")
    print("=" * 40)
    
    packages = ['schedule', 'pandas', 'openpyxl', 'requests']
    
    for package in packages:
        try:
            __import__(package)
            print(f"✅ {package} 已安裝")
        except ImportError:
            print(f"⚠️  {package} 未安裝，開始安裝...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                print(f"✅ {package} 安裝成功")
            except subprocess.CalledProcessError as e:
                print(f"❌ {package} 安裝失敗: {e}")
                return False
    
    return True

def create_startup_scripts():
    """建立啟動腳本"""
    print(f"\n📝 建立啟動腳本...")
    print("=" * 30)
    
    current_dir = Path(__file__).parent.absolute()
    
    # 建立啟動腳本
    scripts = {
        'start_daily_updater_custom.bat': '''@echo off
echo 🚀 啟動每日配息自動更新器 (自訂時間)
echo =====================================
set /p update_time="請輸入每日更新時間 (格式: HH:MM，預設 09:00): "
if "%update_time%"=="" set update_time=09:00
echo 每日 %update_time% 自動更新配息資料
echo 按 Ctrl+C 停止服務
echo.
python daily_dividend_updater.py --schedule %update_time%
pause''',
        
        'install_and_start.bat': '''@echo off
echo 🔧 安裝並啟動每日配息自動更新器
echo ================================
echo 1. 安裝依賴套件...
python setup_daily_updater.py
echo.
echo 2. 測試更新器...
python test_daily_updater.py
echo.
echo 3. 啟動每日自動更新...
python daily_dividend_updater.py
pause''',
        
        'quick_setup.bat': '''@echo off
echo ⚡ 快速設定每日配息自動更新
echo ===========================
echo 選擇設定方式:
echo 1. Python排程器 (需要保持程式執行)
echo 2. Windows工作排程 (系統自動執行)
echo.
set /p choice="請選擇 (1 或 2): "

if "%choice%"=="1" (
    echo 啟動Python排程器...
    python daily_dividend_updater.py --schedule
) else if "%choice%"=="2" (
    echo 設定Windows工作排程...
    python setup_windows_task.py
) else (
    echo 無效的選擇
)
pause'''
    }
    
    for filename, content in scripts.items():
        script_path = current_dir / filename
        try:
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ 建立腳本: {filename}")
        except Exception as e:
            print(f"❌ 建立腳本失敗 {filename}: {e}")
    
    return True

def test_configuration():
    """測試配置"""
    print(f"\n🧪 測試配置...")
    print("=" * 20)
    
    try:
        # 檢查主要檔案是否存在
        required_files = [
            'historical_dividend_tracker.py',
            'daily_dividend_updater.py',
            'inventory.xlsx'
        ]
        
        for filename in required_files:
            if os.path.exists(filename):
                print(f"✅ {filename} 存在")
            else:
                print(f"❌ {filename} 不存在")
                return False
        
        # 測試導入
        try:
            from daily_dividend_updater import DailyDividendUpdater
            print("✅ DailyDividendUpdater 可以導入")
            
            # 建立測試實例
            updater = DailyDividendUpdater()
            print("✅ DailyDividendUpdater 可以實例化")
            
        except Exception as e:
            print(f"❌ DailyDividendUpdater 測試失敗: {e}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 配置測試失敗: {e}")
        return False

def show_usage_guide():
    """顯示使用指南"""
    print(f"\n{'='*60}")
    print("🚀 每日配息自動更新器 - 使用指南")
    print("=" * 60)
    
    print("\n📋 功能說明:")
    print("  • 每日自動檢查新的配息記錄")
    print("  • 自動更新個人配息資料庫 (dividend_database.xlsx)")
    print("  • 保存完整的配息原始資料 (dividend_records_YYYY.xlsx)")
    print("  • 記錄詳細的執行日誌")
    
    print("\n🚀 啟動方式:")
    print("  1. 手動更新:")
    print("     • 雙擊 manual_update.bat")
    print("     • 或執行: python daily_dividend_updater.py --manual")
    
    print("\n  2. Python排程器 (需要保持程式執行):")
    print("     • 雙擊 start_daily_updater.bat (每日09:00)")
    print("     • 雙擊 start_daily_updater_custom.bat (自訂時間)")
    print("     • 或執行: python daily_dividend_updater.py --schedule")
    
    print("\n  3. Windows工作排程 (系統自動執行):")
    print("     • 執行: python setup_windows_task.py")
    print("     • 設定後系統會自動在指定時間執行")
    
    print("\n  4. 互動式選單:")
    print("     • 執行: python daily_dividend_updater.py")
    
    print("\n📋 管理功能:")
    print("  • 查看日誌: 雙擊 view_logs.bat")
    print("  • 測試功能: python test_daily_updater.py")
    print("  • 快速設定: 雙擊 quick_setup.bat")
    
    print("\n💡 建議:")
    print("  • 首次使用建議先執行手動更新測試")
    print("  • 建議使用Windows工作排程，更穩定可靠")
    print("  • 定期檢查日誌檔案 (daily_dividend_update.log)")

def main():
    """主函數"""
    print("🔧 每日配息自動更新器 - 安裝設定")
    print("=" * 50)
    
    # 1. 安裝依賴套件
    if not install_dependencies():
        print("❌ 依賴套件安裝失敗，請檢查網路連線")
        return
    
    # 2. 建立啟動腳本
    if not create_startup_scripts():
        print("❌ 啟動腳本建立失敗")
        return
    
    # 3. 測試配置
    if not test_configuration():
        print("❌ 配置測試失敗，請檢查必要檔案")
        return
    
    print(f"\n✅ 每日配息自動更新器安裝完成！")
    
    # 4. 顯示使用指南
    show_usage_guide()
    
    # 5. 詢問是否立即測試
    print(f"\n{'='*50}")
    choice = input("是否要立即執行測試？(y/N): ").strip().lower()
    
    if choice in ['y', 'yes']:
        print("\n🧪 執行測試...")
        try:
            from test_daily_updater import test_daily_updater
            test_daily_updater()
        except Exception as e:
            print(f"❌ 測試執行失敗: {e}")

if __name__ == "__main__":
    main()
