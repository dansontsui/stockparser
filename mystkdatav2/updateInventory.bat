@echo off
chcp 65001 >nul
echo 📊 股票庫存管理系統
echo ==================
echo 功能:
echo 1. 買入股票
echo 2. 賣出股票
echo 3. 調整庫存 (輸入目前總數量，自動計算差額)
echo 4. 查看庫存
echo 5. 查看交易歷史
echo.
echo 💡 新功能: 智能庫存調整
echo    • 輸入股票代號後立即顯示現有庫存資訊
echo    • 顯示持有股數、平均成本、總成本
echo    • 顯示最近3筆交易記錄作為參考
echo    • 直接輸入目標總數量，自動計算差額
echo    • 系統會自動新增買入/賣出記錄並更新庫存
echo.
python stock_inventory_system.py

echo.
echo 🔄 執行庫存重新整理和統計...
python update_and_stats.bat

pause
