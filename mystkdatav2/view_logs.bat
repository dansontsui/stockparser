@echo off
chcp 65001 >nul
echo 📋 查看更新日誌
echo ===============
python daily_dividend_updater.py --logs
pause
