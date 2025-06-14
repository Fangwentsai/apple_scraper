#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Apple 整修品爬蟲 + Firebase 備份整合系統
"""

import asyncio
import json
import os
from datetime import datetime
from apple_scraper import AppleRefurbishedScraper
from firebase_backup import FirebaseBackup

class AppleScraperWithFirebase:
    def __init__(self, firebase_service_account: str = None):
        """
        初始化爬蟲和 Firebase 備份系統
        
        Args:
            firebase_service_account: Firebase 服務帳戶金鑰檔案路徑
        """
        self.scraper = AppleRefurbishedScraper()
        self.firebase_backup = FirebaseBackup(firebase_service_account) if firebase_service_account else None
        
    async def scrape_and_backup(self, backup_to_firebase: bool = True):
        """
        執行爬蟲並備份到 Firebase
        
        Args:
            backup_to_firebase: 是否備份到 Firebase
        """
        print("🕷️ 開始爬取 Apple 整修品資料...")
        
        try:
            # 執行爬蟲
            products = await self.scraper.scrape_all_products()
            
            if not products:
                print("❌ 未爬取到任何產品資料")
                return False
            
            print(f"✅ 成功爬取 {len(products)} 個產品")
            
            # 儲存到本地 JSON 檔案
            self.save_to_local_files(products)
            
            # 備份到 Firebase
            if backup_to_firebase and self.firebase_backup and self.firebase_backup.db:
                print("🔄 開始備份到 Firebase...")
                await self.backup_to_firebase(products)
            elif backup_to_firebase:
                print("⚠️ Firebase 未設定，跳過雲端備份")
            
            return True
            
        except Exception as e:
            print(f"❌ 爬取過程中發生錯誤: {e}")
            return False
    
    def save_to_local_files(self, products: dict):
        """儲存產品資料到本地 JSON 檔案"""
        try:
            # 確保 data 目錄存在
            os.makedirs('data', exist_ok=True)
            
            # 儲存各類別資料
            categories = {
                'mac': 'data/apple_refurbished_mac.json',
                'ipad': 'data/apple_refurbished_ipad.json',
                'iphone': 'data/apple_refurbished_iphone.json',
                'airpods': 'data/apple_refurbished_airpods.json',
                'homepod': 'data/apple_refurbished_homepod.json',
                'appletv': 'data/apple_refurbished_appletv.json',
                'accessories': 'data/apple_refurbished_accessories.json'
            }
            
            total_saved = 0
            
            for category, file_path in categories.items():
                category_data = products.get(category, [])
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(category_data, f, ensure_ascii=False, indent=2)
                
                if category_data:
                    print(f"💾 {category}: {len(category_data)} 個產品已儲存到 {file_path}")
                    total_saved += len(category_data)
                else:
                    print(f"⚠️ {category}: 無資料")
            
            # 建立總結檔案
            summary = {
                "更新時間": datetime.now().isoformat(),
                "總產品數量": total_saved,
                "各類別統計": {}
            }
            
            for category, file_path in categories.items():
                category_data = products.get(category, [])
                summary["各類別統計"][category] = {
                    "產品數量": len(category_data),
                    "檔案路徑": file_path
                }
            
            with open('data/apple_refurbished_summary.json', 'w', encoding='utf-8') as f:
                json.dump(summary, f, ensure_ascii=False, indent=2)
            
            print(f"📊 總結檔案已更新 - 總計 {total_saved} 個產品")
            
        except Exception as e:
            print(f"❌ 儲存本地檔案時發生錯誤: {e}")
    
    async def backup_to_firebase(self, products: dict):
        """備份產品資料到 Firebase"""
        try:
            if not self.firebase_backup or not self.firebase_backup.db:
                print("❌ Firebase 未連接")
                return False
            
            successful_backups = 0
            total_products = 0
            
            for category, category_data in products.items():
                if category_data:  # 只備份有資料的類別
                    success = self.firebase_backup.backup_category_data(
                        category, 
                        category_data, 
                        check_price_changes=True
                    )
                    
                    if success:
                        successful_backups += 1
                        total_products += len(category_data)
                        print(f"☁️ {category}: {len(category_data)} 個產品已備份到 Firebase")
            
            print(f"🎉 Firebase 備份完成！")
            print(f"📊 成功備份 {successful_backups} 個類別，總計 {total_products} 個產品")
            
            # 檢查價格變更
            price_changes = self.firebase_backup.get_price_change_history(10)
            if price_changes:
                print(f"💰 發現 {len(price_changes)} 個價格變更:")
                for change in price_changes[:3]:  # 顯示最近 3 筆
                    print(f"  {change.get('product_title', 'Unknown')}")
                    print(f"    {change.get('old_price', 'N/A')} → {change.get('new_price', 'N/A')}")
            
            return True
            
        except Exception as e:
            print(f"❌ Firebase 備份時發生錯誤: {e}")
            return False
    
    def get_backup_status(self):
        """獲取備份狀態"""
        if not self.firebase_backup or not self.firebase_backup.db:
            return {"status": "Firebase 未連接"}
        
        try:
            stats = self.firebase_backup.get_backup_statistics()
            price_changes = self.firebase_backup.get_price_change_history(5)
            
            return {
                "status": "已連接",
                "total_backups": stats.get('total_backups', 0),
                "last_backup": stats.get('last_backup', 'N/A'),
                "categories": stats.get('categories', {}),
                "recent_price_changes": len(price_changes)
            }
            
        except Exception as e:
            return {"status": f"錯誤: {e}"}

async def main():
    """主程式"""
    print("🍎 Apple 整修品爬蟲 + Firebase 備份系統")
    print("=" * 60)
    
    # 檢查 Firebase 設定
    firebase_key_path = 'firebase-service-account.json'
    use_firebase = os.path.exists(firebase_key_path)
    
    if use_firebase:
        print(f"🔥 找到 Firebase 金鑰檔案: {firebase_key_path}")
    else:
        print("⚠️ 未找到 Firebase 金鑰檔案，將只儲存到本地")
        print("💡 如需 Firebase 備份，請參考 firebase_setup_guide.md")
    
    # 初始化系統
    scraper_system = AppleScraperWithFirebase(
        firebase_service_account=firebase_key_path if use_firebase else None
    )
    
    # 顯示 Firebase 狀態
    if use_firebase:
        status = scraper_system.get_backup_status()
        print(f"☁️ Firebase 狀態: {status['status']}")
        if status['status'] == '已連接':
            print(f"📊 歷史備份次數: {status['total_backups']}")
            print(f"🕐 最後備份時間: {status['last_backup']}")
    
    print("\n🚀 開始執行...")
    
    # 執行爬蟲和備份
    success = await scraper_system.scrape_and_backup(backup_to_firebase=use_firebase)
    
    if success:
        print("\n✅ 任務完成！")
        
        # 顯示最終狀態
        if use_firebase:
            final_status = scraper_system.get_backup_status()
            print(f"☁️ 最終備份狀態: {final_status['status']}")
            if final_status.get('recent_price_changes', 0) > 0:
                print(f"💰 發現 {final_status['recent_price_changes']} 個價格變更")
    else:
        print("\n❌ 任務失敗")
    
    print("\n📁 本地檔案位置:")
    print("  - data/apple_refurbished_*.json")
    print("  - data/apple_refurbished_summary.json")
    
    if use_firebase:
        print("\n☁️ Firebase 集合:")
        print("  - apple_refurbished_* (產品資料)")
        print("  - price_changes (價格變更記錄)")
        print("  - backup_history (備份歷史)")

if __name__ == "__main__":
    asyncio.run(main()) 