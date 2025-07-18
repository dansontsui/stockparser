#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows 服務版本的每日配息更新器
"""

import time
import threading
from datetime import datetime, timedelta
from daily_dividend_updater import DailyDividendUpdater

class WindowsServiceUpdater:
    """Windows 服務版本的配息更新器"""
    
    def __init__(self, update_time: str = "09:00"):
        self.updater = DailyDividendUpdater()
        self.update_time = update_time
        self.running = False
        self.thread = None
        
        # 解析更新時間
        try:
            time_parts = update_time.split(':')
            self.update_hour = int(time_parts[0])
            self.update_minute = int(time_parts[1])
        except:
            self.update_hour = 9
            self.update_minute = 0
            self.update_time = "09:00"
    
    def should_update_now(self):
        """檢查是否應該現在更新"""
        now = datetime.now()
        
        # 檢查是否到了更新時間
        if now.hour == self.update_hour and now.minute == self.update_minute:
            return True
        
        return False
    
    def has_updated_today(self):
        """檢查今天是否已經更新過"""
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            
            # 檢查日誌檔案
            if hasattr(self.updater, 'log_file'):
                with open(self.updater.log_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # 檢查今天是否有 "🚀 開始每日配息更新" 的記錄
                return f"[{today}" in content and "🚀 開始每日配息更新" in content
        except:
            pass
        
        return False
    
    def service_loop(self):
        """服務主循環"""
        self.updater.log_message(f"🔄 Windows服務啟動，每日 {self.update_time} 自動更新")
        
        while self.running:
            try:
                # 檢查是否需要更新
                if self.should_update_now() and not self.has_updated_today():
                    self.updater.log_message("⏰ 到達更新時間，開始執行每日更新")
                    self.updater.daily_update()
                
                # 每分鐘檢查一次
                time.sleep(60)
                
            except Exception as e:
                self.updater.log_message(f"❌ 服務循環錯誤: {e}")
                time.sleep(300)  # 錯誤時等待5分鐘
    
    def start_service(self):
        """啟動服務"""
        if self.running:
            self.updater.log_message("⚠️  服務已在執行中")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self.service_loop, daemon=True)
        self.thread.start()
        
        self.updater.log_message("✅ Windows服務已啟動")
    
    def stop_service(self):
        """停止服務"""
        if not self.running:
            self.updater.log_message("⚠️  服務未在執行")
            return
        
        self.running = False
        if self.thread:
            self.thread.join(timeout=10)
        
        self.updater.log_message("⏹️  Windows服務已停止")
    
    def run_forever(self):
        """永久執行服務"""
        self.start_service()
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.updater.log_message("⏹️  收到停止信號")
            self.stop_service()

def main():
    """主函數"""
    import sys
    
    # 預設更新時間
    update_time = "09:00"
    
    # 檢查命令列參數
    if len(sys.argv) > 1:
        update_time = sys.argv[1]
    
    print(f"🚀 啟動Windows服務版配息更新器")
    print(f"⏰ 每日更新時間: {update_time}")
    print("按 Ctrl+C 停止服務")
    
    service = WindowsServiceUpdater(update_time)
    service.run_forever()

if __name__ == "__main__":
    main()
