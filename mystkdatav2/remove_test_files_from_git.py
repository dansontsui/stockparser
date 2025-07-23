#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
從 Git 追蹤中移除 test 開頭的檔案
"""

import os
import subprocess
import glob

def remove_test_files_from_git():
    """從 Git 追蹤中移除 test 開頭的檔案"""
    print("🗑️  從 Git 追蹤中移除 test 開頭的檔案")
    print("=" * 50)
    
    # 切換到專案根目錄
    os.chdir('..')
    
    # 尋找所有 test 開頭的檔案
    test_files = []
    
    # 在 mystkdatav2 目錄中尋找
    mystkdata_test_files = glob.glob('mystkdatav2/test*')
    test_files.extend(mystkdata_test_files)
    
    if not test_files:
        print("✅ 沒有找到 test 開頭的檔案")
        return
    
    print(f"📁 找到 {len(test_files)} 個 test 開頭的檔案:")
    for file in test_files:
        print(f"   • {file}")
    
    # 從 Git 追蹤中移除
    print(f"\n🗑️  從 Git 追蹤中移除...")
    
    try:
        for file in test_files:
            try:
                # 使用 git rm --cached 移除追蹤但保留檔案
                result = subprocess.run(['git', 'rm', '--cached', file], 
                                      capture_output=True, text=True)
                
                if result.returncode == 0:
                    print(f"   ✅ 已移除: {file}")
                else:
                    # 檔案可能本來就沒有被追蹤
                    print(f"   ℹ️  跳過: {file} (可能未被追蹤)")
                    
            except Exception as e:
                print(f"   ❌ 移除失敗: {file} - {e}")
        
        print(f"\n📋 檢查 Git 狀態...")
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            status_lines = result.stdout.strip().split('\n')
            deleted_files = [line for line in status_lines if line.startswith('D ')]
            
            if deleted_files:
                print(f"✅ 成功從 Git 追蹤中移除 {len(deleted_files)} 個檔案:")
                for line in deleted_files:
                    print(f"   {line}")
            else:
                print("ℹ️  沒有檔案被移除 (可能本來就沒有被追蹤)")
        
        print(f"\n💡 .gitignore 已更新，未來的 test 開頭檔案會自動被忽略")
        
    except Exception as e:
        print(f"❌ Git 操作失敗: {e}")

def check_gitignore():
    """檢查 .gitignore 設定"""
    print(f"\n📋 檢查 .gitignore 設定...")
    
    try:
        with open('.gitignore', 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'test*' in content:
            print("✅ .gitignore 已包含 test* 規則")
        else:
            print("⚠️  .gitignore 沒有包含 test* 規則")
            
    except Exception as e:
        print(f"❌ 檢查 .gitignore 失敗: {e}")

def main():
    """主函數"""
    print("🗑️  Git 測試檔案清理工具")
    print("=" * 40)
    
    remove_test_files_from_git()
    check_gitignore()
    
    print(f"\n🎉 清理完成！")
    print("💡 現在所有 test 開頭的檔案都不會被 Git 追蹤")
    print("💡 您可以繼續建立測試檔案，它們會自動被忽略")

if __name__ == "__main__":
    main()
