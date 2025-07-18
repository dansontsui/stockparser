#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
設定Windows工作排程器
"""

import os
import sys
import subprocess
from pathlib import Path

def create_task_xml(script_path: str, update_time: str = "09:00"):
    """建立工作排程XML檔案"""
    
    # 獲取當前使用者
    import getpass
    username = getpass.getuser()
    
    # 獲取Python執行檔路徑
    python_exe = sys.executable
    
    xml_content = f'''<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Date>2025-01-01T00:00:00</Date>
    <Author>{username}</Author>
    <Description>每日自動更新配息資料</Description>
  </RegistrationInfo>
  <Triggers>
    <CalendarTrigger>
      <StartBoundary>2025-01-01T{update_time}:00</StartBoundary>
      <Enabled>true</Enabled>
      <ScheduleByDay>
        <DaysInterval>1</DaysInterval>
      </ScheduleByDay>
    </CalendarTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <UserId>{username}</UserId>
      <LogonType>InteractiveToken</LogonType>
      <RunLevel>LeastPrivilege</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>true</RunOnlyIfNetworkAvailable>
    <IdleSettings>
      <StopOnIdleEnd>false</StopOnIdleEnd>
      <RestartOnIdle>false</RestartOnIdle>
    </IdleSettings>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>false</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <WakeToRun>false</WakeToRun>
    <ExecutionTimeLimit>PT1H</ExecutionTimeLimit>
    <Priority>7</Priority>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>{python_exe}</Command>
      <Arguments>"{script_path}" --manual</Arguments>
      <WorkingDirectory>{os.path.dirname(script_path)}</WorkingDirectory>
    </Exec>
  </Actions>
</Task>'''
    
    return xml_content

def setup_windows_task():
    """設定Windows工作排程"""
    print("⚙️  設定Windows工作排程器")
    print("=" * 50)
    
    # 獲取腳本路徑
    current_dir = Path(__file__).parent.absolute()
    updater_script = current_dir / "daily_dividend_updater.py"
    
    if not updater_script.exists():
        print(f"❌ 找不到更新腳本: {updater_script}")
        return False
    
    # 詢問更新時間
    update_time = input("請輸入每日更新時間 (格式: HH:MM，預設 09:00): ").strip()
    if not update_time:
        update_time = "09:00"
    
    try:
        # 驗證時間格式
        from datetime import datetime
        datetime.strptime(update_time, '%H:%M')
    except ValueError:
        print("❌ 時間格式錯誤，使用預設時間 09:00")
        update_time = "09:00"
    
    # 建立XML檔案
    xml_content = create_task_xml(str(updater_script), update_time)
    xml_file = current_dir / "dividend_updater_task.xml"
    
    try:
        with open(xml_file, 'w', encoding='utf-16') as f:
            f.write(xml_content)
        
        print(f"✅ 工作排程XML檔案已建立: {xml_file}")
        
        # 使用schtasks命令建立工作排程
        task_name = "DividendUpdater"
        
        print(f"📅 建立工作排程: {task_name}")
        
        # 刪除現有的工作排程（如果存在）
        try:
            subprocess.run([
                "schtasks", "/delete", "/tn", task_name, "/f"
            ], capture_output=True, check=False)
        except:
            pass
        
        # 建立新的工作排程
        result = subprocess.run([
            "schtasks", "/create", "/tn", task_name, "/xml", str(xml_file)
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Windows工作排程建立成功")
            print(f"⏰ 每日 {update_time} 自動執行配息更新")
            print(f"📋 工作排程名稱: {task_name}")
            
            # 顯示管理指令
            print(f"\n💡 管理指令:")
            print(f"  查看工作排程: schtasks /query /tn {task_name}")
            print(f"  手動執行: schtasks /run /tn {task_name}")
            print(f"  停用工作排程: schtasks /change /tn {task_name} /disable")
            print(f"  啟用工作排程: schtasks /change /tn {task_name} /enable")
            print(f"  刪除工作排程: schtasks /delete /tn {task_name} /f")
            
            return True
        else:
            print(f"❌ 建立工作排程失敗: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 設定工作排程失敗: {e}")
        return False

def remove_windows_task():
    """移除Windows工作排程"""
    print("🗑️  移除Windows工作排程")
    print("=" * 30)
    
    task_name = "DividendUpdater"
    
    try:
        result = subprocess.run([
            "schtasks", "/delete", "/tn", task_name, "/f"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ 工作排程 {task_name} 已移除")
            return True
        else:
            print(f"❌ 移除工作排程失敗: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 移除工作排程失敗: {e}")
        return False

def main():
    """主函數"""
    print("⚙️  Windows工作排程設定工具")
    print("=" * 40)
    print("1. 建立每日自動更新工作排程")
    print("2. 移除工作排程")
    print("3. 退出")
    
    choice = input("\n請選擇 (1-3): ").strip()
    
    if choice == '1':
        setup_windows_task()
    elif choice == '2':
        remove_windows_task()
    elif choice == '3':
        print("👋 再見！")
    else:
        print("❌ 無效的選擇")

if __name__ == "__main__":
    main()
