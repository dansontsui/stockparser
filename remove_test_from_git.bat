@echo off
chcp 65001 >nul
echo 🗑️  從 Git 追蹤中移除 test 開頭的檔案
echo =======================================

echo 📁 檢查 test 開頭的檔案...
dir mystkdatav2\test* /b 2>nul
if errorlevel 1 (
    echo ✅ 沒有找到 test 開頭的檔案
    goto :end
)

echo.
echo 🗑️  從 Git 追蹤中移除...

REM 移除 test 開頭的 Python 檔案
for %%f in (mystkdatav2\test*.py) do (
    echo 移除: %%f
    git rm --cached "%%f" 2>nul
)

REM 移除 test 開頭的批次檔
for %%f in (mystkdatav2\test*.bat) do (
    echo 移除: %%f
    git rm --cached "%%f" 2>nul
)

REM 移除其他 test 開頭的檔案
for %%f in (mystkdatav2\test*) do (
    echo 移除: %%f
    git rm --cached "%%f" 2>nul
)

echo.
echo 📋 檢查 Git 狀態...
git status --porcelain | findstr "^D "

echo.
echo ✅ 完成！test 開頭的檔案已從 Git 追蹤中移除
echo 💡 .gitignore 已更新，未來的 test 檔案會自動被忽略

:end
pause
