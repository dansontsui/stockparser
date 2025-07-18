@echo off
echo === 執行00878股價獲取程式 ===
echo.
echo 選擇執行版本:
echo 1. 簡單版 (simple_00878.py)
echo 2. 整合版 (get_00878_simple.py)
echo 3. 完整版 (get_00878_stock_price.py)
echo.
set /p choice="請選擇 (1-3): "

if "%choice%"=="1" (
    echo 執行簡單版...
    python simple_00878.py
) else if "%choice%"=="2" (
    echo 執行整合版...
    python get_00878_simple.py
) else if "%choice%"=="3" (
    echo 執行完整版...
    python get_00878_stock_price.py
) else (
    echo 預設執行整合版...
    python get_00878_simple.py
)

echo.
echo 程式執行完成
pause
