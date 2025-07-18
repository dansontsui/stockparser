# 📊 股票配息自動追蹤系統

一個完整的股票配息自動追蹤和管理系統，支援歷史回朔計算和每日自動更新功能。

## 🎯 主要功能

### 📈 歷史配息追蹤
- **智能回朔計算**：根據實際配息日期計算當時的庫存持有量
- **避免重複計算**：每筆配息只記錄一次，避免重複計算
- **多市場支援**：支援 TSE (證交所) 和 TPEx (櫃買中心) 資料
- **範圍追蹤**：可指定年份範圍進行批量處理

### 🤖 每日自動更新
- **自動檢查**：每日自動檢查新的配息記錄
- **智能更新**：只處理新增的配息，避免重複更新
- **多種排程**：支援 Python 排程器和 Windows 工作排程
- **詳細日誌**：記錄所有執行過程和結果

### 💾 資料管理
- **Excel 格式**：配息資料保存為 Excel 格式，包含多個工作表
- **個人資料庫**：維護個人配息收益資料庫
- **原始資料備份**：保留 TSE 和 TPEx 原始資料

## 📁 檔案結構

```
mystkdatav2/
├── historical_dividend_tracker.py    # 主要配息追蹤程式
├── daily_dividend_updater.py         # 每日自動更新器
├── dividend_data_manager.py          # 配息資料管理工具
├── setup_daily_updater.py           # 安裝設定工具
├── setup_windows_task.py            # Windows 工作排程設定
├── test_daily_updater.py            # 測試工具
├── inventory.xlsx                    # 股票庫存檔案
├── dividend_database.xlsx           # 個人配息資料庫
├── dividend_records_YYYY.xlsx       # 年度配息資料
├── daily_dividend_update.log        # 執行日誌
├── remove_and_reimport.log       	 # 清除某支股票 並匯入元大excel
├── safe_reorganize.py       	 	# 重整庫存
└── *.bat                            # 便利啟動腳本
```

## 🚀 快速開始

### 1. 環境設定

```bash
# 安裝必要套件和設定
python setup_daily_updater.py
```

### 2. 首次使用

```bash
# 測試系統功能
python test_daily_updater.py

# 手動執行一次更新
python daily_dividend_updater.py --manual
```

### 3. 設定自動更新

**方式一：Python 排程器** (需要保持程式執行)
```bash
# 每日 09:00 自動更新
python daily_dividend_updater.py --schedule

# 自訂時間
python daily_dividend_updater.py --schedule 10:30
```

**方式二：Windows 工作排程** (推薦)
```bash
# 設定 Windows 工作排程
python setup_windows_task.py
```

## 📋 詳細使用說明

### 歷史配息追蹤

#### 執行主程式
```bash
python historical_dividend_tracker.py
```

**選單選項：**
1. **單月配息追蹤**：追蹤指定月份的配息
2. **範圍配息追蹤**：追蹤指定年份範圍的配息
3. **顯示配息摘要**：查看配息統計資料

#### 範圍追蹤範例
```bash
# 追蹤 2024 年至今的所有配息
輸入起始年月: 2024-01
```

### 每日自動更新

#### 命令列使用
```bash
# 手動更新
python daily_dividend_updater.py --manual

# 啟動排程器 (預設 09:00)
python daily_dividend_updater.py --schedule

# 啟動排程器 (自訂時間)
python daily_dividend_updater.py --schedule 10:30

# 查看日誌
python daily_dividend_updater.py --logs

# 查看最近 30 天日誌
python daily_dividend_updater.py --logs 30
```

#### 互動式選單
```bash
python daily_dividend_updater.py
```

### 便利批次檔

| 檔案名稱 | 功能 |
|---------|------|
| `manual_update.bat` | 手動執行配息更新 |
| `start_daily_updater.bat` | 啟動每日自動更新 (09:00) |
| `start_daily_updater_custom.bat` | 啟動每日自動更新 (自訂時間) |
| `view_logs.bat` | 查看更新日誌 |
| `quick_setup.bat` | 快速設定選單 |
| `install_and_start.bat` | 安裝並啟動 |
| `updateInventory.bat` | 手動新增買賣庫存 |


## 🔧 進階功能

### 資料管理工具
```bash
python dividend_data_manager.py
```

**功能包括：**
- 下載指定年份配息資料
- 批量下載多年資料
- 列出已保存的檔案
- 分析配息資料統計

### Windows 工作排程管理
```bash
python setup_windows_task.py
```

**管理指令：**
```bash
# 查看工作排程
schtasks /query /tn DividendUpdater

# 手動執行
schtasks /run /tn DividendUpdater

# 停用工作排程
schtasks /change /tn DividendUpdater /disable

# 啟用工作排程
schtasks /change /tn DividendUpdater /enable

# 刪除工作排程
schtasks /delete /tn DividendUpdater /f
```

## 📊 資料格式

### 庫存檔案 (inventory.xlsx)
- **工作表：交易歷史**
- **必要欄位：**
  - 交易日期 (YYYY-MM-DD)
  - 股票代碼
  - 股票名稱
  - 交易類型 (買入/賣出)
  - 數量
  - 價格

### 配息資料庫 (dividend_database.xlsx)
- **工作表：配息記錄**
- **欄位包括：**
  - 年月、股票代碼、股票名稱
  - 持有股數、每股配息、總配息收益
  - 除息日期、檢查日期、資料來源、備註

### 年度配息資料 (dividend_records_YYYY.xlsx)
- **YYYY年配息記錄**：標準化合併資料
- **TPEx原始資料**：櫃買中心原始資料
- **TSE原始資料**：證交所原始資料

## 🔍 故障排除

### 常見問題

**1. ModuleNotFoundError: No module named 'schedule'**
```bash
python -m pip install schedule
```

**2. 找不到庫存檔案**
- 確認 `inventory.xlsx` 檔案存在
- 檢查檔案格式是否正確

**3. 網路連線問題**
- 檢查網路連線
- 查看日誌檔案了解詳細錯誤

**4. 配息資料為空**
- 確認股票代碼正確
- 檢查查詢日期範圍
- 查看日誌了解詳細情況

### 日誌檔案
- **位置**：`daily_dividend_update.log`
- **內容**：包含所有執行過程、錯誤訊息和結果統計
- **查看**：雙擊 `view_logs.bat` 或使用命令 `python daily_dividend_updater.py --logs`

## 💡 使用建議

### 最佳實踐
1. **首次使用**：先執行手動更新測試功能
2. **排程選擇**：建議使用 Windows 工作排程，更穩定可靠
3. **定期檢查**：定期查看日誌檔案確認執行狀況
4. **資料備份**：定期備份 `dividend_database.xlsx` 和 `inventory.xlsx`

### 效能優化
- 系統會自動避免重複處理相同的配息記錄
- 年初 (1-2月) 會額外檢查去年的配息資料
- 使用快取機制減少重複的網路請求

## 📞 技術支援

如果遇到問題，請：
1. 查看日誌檔案 (`daily_dividend_update.log`)
2. 執行測試工具 (`python test_daily_updater.py`)
3. 檢查必要檔案是否存在且格式正確

---

**🎉 享受自動化的配息追蹤體驗！**
