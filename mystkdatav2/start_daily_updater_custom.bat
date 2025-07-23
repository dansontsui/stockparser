@echo off
chcp 65001 >nul
echo 🚀 啟動每日配息自動更新器 (自訂時間)
echo =====================================
set /p update_time="請輸入每日更新時間 (格式: HH:MM，預設 09:00): "
if "%update_time%"=="" set update_time=09:00
echo 每日 %update_time% 自動更新配息資料
echo 按 Ctrl+C 停止服務
echo.
python daily_dividend_updater.py --schedule %update_time%
pause