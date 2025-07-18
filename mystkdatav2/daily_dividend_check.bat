@echo off
chcp 65001 > nul
echo Daily Dividend Checker
echo ========================
echo Time: %date% %time%
echo.

cd /d "%~dp0"

echo Starting dividend check...
python daily_dividend_checker.py --auto

echo.
echo Check completed!
echo Please check: dividend_database.xlsx
echo CSV report also generated
echo.
pause
