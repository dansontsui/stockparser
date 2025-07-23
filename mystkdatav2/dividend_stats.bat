@echo off
chcp 65001 >nul
echo 📊 配息統計分析工具
echo ===================
echo 針對 dividend_database.xlsx 生成統計報表
echo.
python dividend_statistics.py
pause
