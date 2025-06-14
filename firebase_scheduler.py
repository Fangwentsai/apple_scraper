#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Firebase 定期備份排程系統
"""

import schedule
import time
import threading
from datetime import datetime
from firebase_backup import FirebaseBackup
import logging

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('firebase_backup.log'),
        logging.StreamHandler()
    ]
)

class FirebaseScheduler:
    def __init__(self, service_account_path: str = None):
        """初始化 Firebase 排程器"""
        self.firebase_backup = FirebaseBackup(service_account_path)
        self.is_running = False
        self.scheduler_thread = None
    
    def backup_job(self):
        """執行備份工作"""
        try:
            logging.info("🔄 開始定期備份...")
            
            if not self.firebase_backup.db:
                logging.error("❌ Firebase 未連接，跳過備份")
                return
            
            # 執行備份
            successful_backups, total_products = self.firebase_backup.backup_all_categories()
            
            logging.info(f"✅ 備份完成 - {successful_backups} 個類別，{total_products} 個產品")
            
            # 檢查價格變更
            price_changes = self.firebase_backup.get_price_change_history(5)
            if price_changes:
                logging.info(f"💰 發現 {len(price_changes)} 個價格變更")
                for change in price_changes:
                    logging.info(f"  {change.get('product_title', 'Unknown')}: {change.get('old_price', 'N/A')} → {change.get('new_price', 'N/A')}")
            
        except Exception as e:
            logging.error(f"❌ 備份過程中發生錯誤: {e}")
    
    def start_scheduler(self):
        """啟動排程器"""
        if self.is_running:
            logging.warning("⚠️ 排程器已在運行中")
            return
        
        # 設定排程
        schedule.clear()
        
        # 每天早上 9 點備份
        schedule.every().day.at("09:00").do(self.backup_job)
        
        # 每天晚上 9 點備份
        schedule.every().day.at("21:00").do(self.backup_job)
        
        # 每 6 小時備份一次（可選）
        # schedule.every(6).hours.do(self.backup_job)
        
        self.is_running = True
        
        def run_scheduler():
            logging.info("🚀 Firebase 備份排程器已啟動")
            logging.info("📅 排程設定:")
            logging.info("  - 每天 09:00 自動備份")
            logging.info("  - 每天 21:00 自動備份")
            
            while self.is_running:
                schedule.run_pending()
                time.sleep(60)  # 每分鐘檢查一次
        
        self.scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
        logging.info("✅ 排程器執行緒已啟動")
    
    def stop_scheduler(self):
        """停止排程器"""
        self.is_running = False
        schedule.clear()
        logging.info("🛑 Firebase 備份排程器已停止")
    
    def manual_backup(self):
        """手動執行備份"""
        logging.info("🔧 手動執行備份...")
        self.backup_job()
    
    def get_next_run_time(self):
        """獲取下次執行時間"""
        jobs = schedule.get_jobs()
        if jobs:
            next_run = min(job.next_run for job in jobs)
            return next_run.strftime("%Y-%m-%d %H:%M:%S")
        return "無排程"

def main():
    """主程式"""
    print("🔥 Firebase 定期備份系統")
    print("=" * 50)
    
    # 初始化排程器
    scheduler = FirebaseScheduler('firebase-service-account.json')
    
    if not scheduler.firebase_backup.db:
        print("❌ Firebase 連接失敗，請檢查設定")
        print("\n📋 設定步驟:")
        print("1. 在 Firebase Console 建立專案")
        print("2. 啟用 Firestore 資料庫")
        print("3. 建立服務帳戶並下載金鑰檔案")
        print("4. 將金鑰檔案命名為 'firebase-service-account.json'")
        print("5. 或設定環境變數 GOOGLE_APPLICATION_CREDENTIALS")
        return
    
    # 執行一次手動備份
    print("🔧 執行初始備份...")
    scheduler.manual_backup()
    
    # 啟動排程器
    scheduler.start_scheduler()
    
    print(f"\n⏰ 下次自動備份時間: {scheduler.get_next_run_time()}")
    print("\n指令:")
    print("  輸入 'backup' 手動執行備份")
    print("  輸入 'status' 查看狀態")
    print("  輸入 'quit' 退出程式")
    
    # 互動式命令列
    try:
        while True:
            command = input("\n> ").strip().lower()
            
            if command == 'backup':
                scheduler.manual_backup()
            
            elif command == 'status':
                print(f"📊 排程器狀態: {'運行中' if scheduler.is_running else '已停止'}")
                print(f"⏰ 下次執行時間: {scheduler.get_next_run_time()}")
                
                # 顯示統計
                stats = scheduler.firebase_backup.get_backup_statistics()
                if stats:
                    print(f"📈 總備份次數: {stats.get('total_backups', 0)}")
                    print(f"🕐 最後備份時間: {stats.get('last_backup', 'N/A')}")
            
            elif command == 'quit':
                break
            
            else:
                print("❓ 未知指令，請輸入 'backup', 'status' 或 'quit'")
    
    except KeyboardInterrupt:
        pass
    
    finally:
        scheduler.stop_scheduler()
        print("\n👋 程式已退出")

if __name__ == "__main__":
    main() 