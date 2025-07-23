@echo off
chcp 65001 >nul
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
pause