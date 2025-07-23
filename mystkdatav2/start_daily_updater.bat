@echo off
chcp 65001 >nul
echo 🚀 啟動每日配息自動更新器
echo ============================
echo 每日 09:00 自動更新配息資料
echo 按 Ctrl+C 停止服務
echo.
python daily_dividend_updater.py --schedule
pause
