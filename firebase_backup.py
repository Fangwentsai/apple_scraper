#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Firebase 備份系統 - 儲存 Apple 整修品資料並追蹤價格變更
"""

import json
import os
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
from typing import Dict, List, Any

class FirebaseBackup:
    def __init__(self, service_account_path: str = None):
        """
        初始化 Firebase 連接
        
        Args:
            service_account_path: Firebase 服務帳戶 JSON 檔案路徑
        """
        self.db = None
        self.initialize_firebase(service_account_path)
    
    def initialize_firebase(self, service_account_path: str = None):
        """初始化 Firebase"""
        try:
            # 檢查是否已經初始化
            if firebase_admin._apps:
                self.db = firestore.client()
                print("✅ Firebase 已連接")
                return
            
            # 使用服務帳戶金鑰
            if service_account_path and os.path.exists(service_account_path):
                cred = credentials.Certificate(service_account_path)
                firebase_admin.initialize_app(cred)
                print(f"✅ 使用服務帳戶金鑰初始化 Firebase: {service_account_path}")
            
            # 使用環境變數
            elif os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
                cred = credentials.ApplicationDefault()
                firebase_admin.initialize_app(cred)
                print("✅ 使用環境變數初始化 Firebase")
            
            # 使用預設憑證
            else:
                try:
                    cred = credentials.ApplicationDefault()
                    firebase_admin.initialize_app(cred)
                    print("✅ 使用預設憑證初始化 Firebase")
                except Exception as e:
                    print(f"❌ Firebase 初始化失敗: {e}")
                    print("請設定 Firebase 服務帳戶金鑰或環境變數")
                    return
            
            self.db = firestore.client()
            print("🔥 Firebase Firestore 連接成功")
            
        except Exception as e:
            print(f"❌ Firebase 初始化錯誤: {e}")
            self.db = None
    
    def backup_category_data(self, category: str, data: List[Dict], check_price_changes: bool = True):
        """
        備份單一類別資料到 Firebase
        
        Args:
            category: 產品類別 (mac, ipad, airpods, etc.)
            data: 產品資料列表
            check_price_changes: 是否檢查價格變更
        """
        if not self.db:
            print("❌ Firebase 未連接")
            return False
        
        try:
            timestamp = datetime.now().isoformat()
            
            # 備份當前資料
            collection_name = f"apple_refurbished_{category}"
            
            for product in data:
                product_id = f"{category}_{product.get('序號', 'unknown')}"
                
                # 準備要儲存的資料
                backup_data = {
                    **product,
                    'category': category,
                    'last_updated': timestamp,
                    'backup_timestamp': timestamp
                }
                
                # 檢查價格變更
                if check_price_changes:
                    price_changed = self.check_price_change(product_id, product.get('產品售價'))
                    if price_changed:
                        self.log_price_change(product_id, product, timestamp)
                
                # 儲存到 Firebase
                doc_ref = self.db.collection(collection_name).document(product_id)
                doc_ref.set(backup_data, merge=True)
            
            print(f"✅ {category} 類別 {len(data)} 個產品已備份到 Firebase")
            
            # 記錄備份歷史
            self.log_backup_history(category, len(data), timestamp)
            
            return True
            
        except Exception as e:
            print(f"❌ 備份 {category} 時發生錯誤: {e}")
            return False
    
    def check_price_change(self, product_id: str, current_price: str) -> bool:
        """檢查產品價格是否有變更"""
        try:
            # 從所有類別中尋找產品
            collections = ['apple_refurbished_mac', 'apple_refurbished_ipad', 
                          'apple_refurbished_airpods', 'apple_refurbished_homepod',
                          'apple_refurbished_accessories', 'apple_refurbished_iphone',
                          'apple_refurbished_appletv']
            
            for collection_name in collections:
                doc_ref = self.db.collection(collection_name).document(product_id)
                doc = doc_ref.get()
                
                if doc.exists:
                    old_price = doc.to_dict().get('產品售價')
                    if old_price and old_price != current_price:
                        print(f"💰 價格變更發現: {product_id}")
                        print(f"   舊價格: {old_price}")
                        print(f"   新價格: {current_price}")
                        return True
            
            return False
            
        except Exception as e:
            print(f"⚠️ 檢查價格變更時發生錯誤: {e}")
            return False
    
    def log_price_change(self, product_id: str, product_data: Dict, timestamp: str):
        """記錄價格變更歷史"""
        try:
            price_change_data = {
                'product_id': product_id,
                'product_title': product_data.get('產品標題'),
                'old_price': None,  # 會在 check_price_change 中設定
                'new_price': product_data.get('產品售價'),
                'change_timestamp': timestamp,
                'product_url': product_data.get('產品URL')
            }
            
            # 儲存價格變更記錄
            self.db.collection('price_changes').add(price_change_data)
            print(f"📝 價格變更已記錄: {product_id}")
            
        except Exception as e:
            print(f"❌ 記錄價格變更時發生錯誤: {e}")
    
    def log_backup_history(self, category: str, product_count: int, timestamp: str):
        """記錄備份歷史"""
        try:
            backup_record = {
                'category': category,
                'product_count': product_count,
                'backup_timestamp': timestamp,
                'status': 'success'
            }
            
            self.db.collection('backup_history').add(backup_record)
            
        except Exception as e:
            print(f"⚠️ 記錄備份歷史時發生錯誤: {e}")
    
    def backup_all_categories(self):
        """備份所有類別的資料"""
        categories = {
            'mac': 'data/apple_refurbished_mac.json',
            'ipad': 'data/apple_refurbished_ipad.json',
            'iphone': 'data/apple_refurbished_iphone.json',
            'airpods': 'data/apple_refurbished_airpods.json',
            'homepod': 'data/apple_refurbished_homepod.json',
            'appletv': 'data/apple_refurbished_appletv.json',
            'accessories': 'data/apple_refurbished_accessories.json'
        }
        
        total_products = 0
        successful_backups = 0
        
        print("🔄 開始備份所有類別到 Firebase...")
        
        for category, file_path in categories.items():
            try:
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    if data:  # 只備份有資料的類別
                        success = self.backup_category_data(category, data)
                        if success:
                            successful_backups += 1
                            total_products += len(data)
                        print(f"✅ {category}: {len(data)} 個產品")
                    else:
                        print(f"⚠️ {category}: 無資料")
                else:
                    print(f"❌ {category}: 檔案不存在 ({file_path})")
                    
            except Exception as e:
                print(f"❌ 處理 {category} 時發生錯誤: {e}")
        
        print(f"\n🎉 備份完成！")
        print(f"📊 成功備份 {successful_backups}/{len(categories)} 個類別")
        print(f"📦 總計 {total_products} 個產品已備份到 Firebase")
        
        return successful_backups, total_products
    
    def get_price_change_history(self, limit: int = 50) -> List[Dict]:
        """獲取價格變更歷史"""
        try:
            if not self.db:
                return []
            
            # 按時間倒序獲取價格變更記錄
            docs = self.db.collection('price_changes')\
                          .order_by('change_timestamp', direction=firestore.Query.DESCENDING)\
                          .limit(limit)\
                          .stream()
            
            changes = []
            for doc in docs:
                changes.append(doc.to_dict())
            
            return changes
            
        except Exception as e:
            print(f"❌ 獲取價格變更歷史時發生錯誤: {e}")
            return []
    
    def get_backup_statistics(self) -> Dict:
        """獲取備份統計資訊"""
        try:
            if not self.db:
                return {}
            
            stats = {
                'total_backups': 0,
                'categories': {},
                'last_backup': None
            }
            
            # 獲取備份歷史統計
            docs = self.db.collection('backup_history')\
                          .order_by('backup_timestamp', direction=firestore.Query.DESCENDING)\
                          .limit(100)\
                          .stream()
            
            for doc in docs:
                data = doc.to_dict()
                category = data.get('category')
                
                if category not in stats['categories']:
                    stats['categories'][category] = {
                        'backup_count': 0,
                        'total_products': 0,
                        'last_backup': None
                    }
                
                stats['categories'][category]['backup_count'] += 1
                stats['categories'][category]['total_products'] = data.get('product_count', 0)
                
                if not stats['categories'][category]['last_backup']:
                    stats['categories'][category]['last_backup'] = data.get('backup_timestamp')
                
                if not stats['last_backup']:
                    stats['last_backup'] = data.get('backup_timestamp')
                
                stats['total_backups'] += 1
            
            return stats
            
        except Exception as e:
            print(f"❌ 獲取備份統計時發生錯誤: {e}")
            return {}

def main():
    """主程式 - 示範如何使用 Firebase 備份"""
    print("🔥 Firebase 備份系統")
    print("=" * 50)
    
    # 初始化 Firebase 備份系統
    # 請將 'path/to/your/service-account-key.json' 替換為你的 Firebase 服務帳戶金鑰路徑
    firebase_backup = FirebaseBackup('firebase-service-account.json')
    
    if not firebase_backup.db:
        print("❌ Firebase 連接失敗，請檢查設定")
        return
    
    # 備份所有類別
    successful_backups, total_products = firebase_backup.backup_all_categories()
    
    # 顯示統計資訊
    print("\n📊 備份統計:")
    stats = firebase_backup.get_backup_statistics()
    if stats:
        print(f"總備份次數: {stats.get('total_backups', 0)}")
        print(f"最後備份時間: {stats.get('last_backup', 'N/A')}")
        
        for category, info in stats.get('categories', {}).items():
            print(f"  {category}: {info.get('total_products', 0)} 個產品")
    
    # 顯示最近的價格變更
    print("\n💰 最近價格變更:")
    price_changes = firebase_backup.get_price_change_history(10)
    if price_changes:
        for change in price_changes[:5]:  # 顯示最近 5 筆
            print(f"  {change.get('product_title', 'Unknown')}")
            print(f"    {change.get('old_price', 'N/A')} → {change.get('new_price', 'N/A')}")
            print(f"    時間: {change.get('change_timestamp', 'N/A')}")
    else:
        print("  目前無價格變更記錄")

if __name__ == "__main__":
    main() 