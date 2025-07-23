@echo off
chcp 65001 >nul
echo 📊 庫存檢查與重新整理工具
echo ===========================
echo 檢查可用的庫存檔案並重新整理
echo.
python check_and_reorganize_inventory.py
pause
