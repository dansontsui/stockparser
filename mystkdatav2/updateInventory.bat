@echo off
echo 📊 股票庫存管理系統
echo ==================
echo 功能:
echo 1. 買入股票
echo 2. 賣出股票
echo 3. 調整庫存 (輸入目前總數量，自動計算差額)
echo 4. 查看庫存
echo 5. 查看交易歷史
echo.
echo � 新功能: 庫存調整
echo    直接輸入股票目前總數量
echo    系統會自動計算差額並新增買入/賣出記錄
echo    使用今天的日期，保持記錄完整
echo.
python stock_inventory_system.py

echo.
echo � 執行庫存重新整理和統計...
python update_and_stats.bat

pause
