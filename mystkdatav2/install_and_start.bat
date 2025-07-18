@echo off
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
pause