@echo off
echo 🔄 庫存更新與統計整合工具
echo ===========================
echo 1. 執行庫存重新整理
echo 2. 生成統計報表
echo.

echo 🔄 步驟1: 執行庫存重新整理...
python safe_reorganize.py

echo.
echo 📊 步驟2: 生成配息統計報表...
python dividend_statistics.py

echo.
echo 🎉 庫存更新與統計完成！
echo 📁 請檢查以下檔案:
echo   • stock_inventory.xlsx (庫存資料)
echo   • dividend_database.xlsx (配息統計)
echo.
pause
