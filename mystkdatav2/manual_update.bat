@echo off
chcp 65001 >nul
echo 🔧 手動執行配息更新
echo ===================
python daily_dividend_updater.py --manual
pause
