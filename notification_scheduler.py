#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Apple 整修品通知排程器
定期檢查用戶請求並發送通知
"""

import schedule
import time
import threading
from linebot_service import bot_service, line_bot_api
from chatgpt_query import AppleRefurbishedQuery
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import os

class NotificationScheduler:
    def __init__(self):
        """初始化通知排程器"""
        self.query_system = AppleRefurbishedQuery()
        
        # 初始化 Firebase
        try:
            if not firebase_admin._apps:
                cred = credentials.Certificate('firebase-service-account.json')
                firebase_admin.initialize_app(cred)
            self.db = firestore.client()
            print("✅ Firebase 初始化成功")
        except Exception as e:
            print(f"❌ Firebase 初始化失敗: {e}")
            self.db = None
    
    def check_and_notify_users(self):
        """檢查並通知符合條件的用戶"""
        if not self.db:
            print("❌ Firebase 未初始化，無法檢查用戶請求")
            return
        
        try:
            print(f"🔍 開始檢查用戶請求... {datetime.now()}")
            
            # 取得所有未通知的請求
            requests_ref = self.db.collection('requests').where('notice', '==', False)
            requests = requests_ref.stream()
            
            notification_count = 0
            
            for request_doc in requests:
                request_data = request_doc.to_dict()
                user_id = request_data.get('userid')
                product = request_data.get('product')
                max_price = request_data.get('price')
                
                if not all([user_id, product, max_price]):
                    continue
                
                # 查詢符合條件的產品
                matching_products = self.find_matching_products(product, max_price)
                
                if matching_products:
                    # 發送通知
                    success = self.send_product_notification(user_id, matching_products, product, max_price)
                    
                    if success:
                        # 更新通知狀態
                        request_doc.reference.update({
                            'notice': True, 
                            'updated_at': datetime.now(),
                            'notified_products': len(matching_products)
                        })
                        notification_count += 1
                        print(f"✅ 已通知用戶 {user_id} 關於 {product} 產品")
            
            if notification_count > 0:
                print(f"📧 共發送 {notification_count} 個通知")
            else:
                print("📭 沒有需要發送的通知")
                
        except Exception as e:
            print(f"❌ 檢查用戶通知失敗: {e}")
    
    def find_matching_products(self, product, max_price):
        """尋找符合條件的產品"""
        try:
            # 根據產品類別搜尋
            products = self.query_system.search_by_category(product)
            
            # 篩選價格符合的產品
            matching_products = []
            for prod in products:
                price = self.query_system.extract_price(prod.get('產品售價', ''))
                if price and price <= max_price:
                    matching_products.append(prod)
            
            return matching_products[:5]  # 最多5個產品
        except Exception as e:
            print(f"❌ 搜尋產品失敗: {e}")
            return []
    
    def send_product_notification(self, user_id, products, product_type, max_price):
        """發送產品通知給用戶"""
        try:
            # 發送文字通知
            message = f"🎉 好消息！我們找到了符合您需求的 {product_type.upper()} 產品（預算 NT${max_price:,} 以內）："
            line_bot_api.push_message(user_id, TextSendMessage(text=message))
            
            # 發送產品 Flex Message
            from linebot.models import TextSendMessage
            flex_message = bot_service.create_product_flex_message(products, f"{product_type.upper()} 推薦")
            line_bot_api.push_message(user_id, flex_message)
            
            return True
        except Exception as e:
            print(f"❌ 發送通知失敗: {e}")
            return False
    
    def start_scheduler(self):
        """啟動排程器"""
        print("🚀 啟動通知排程器...")
        
        # 每5分鐘檢查一次
        schedule.every(5).minutes.do(self.check_and_notify_users)
        
        # 每小時重新載入產品資料
        schedule.every().hour.do(self.reload_product_data)
        
        print("⏰ 排程設定完成：")
        print("   - 每5分鐘檢查用戶請求")
        print("   - 每小時重新載入產品資料")
        
        # 立即執行一次檢查
        self.check_and_notify_users()
        
        # 持續運行排程
        while True:
            schedule.run_pending()
            time.sleep(30)  # 每30秒檢查一次排程
    
    def reload_product_data(self):
        """重新載入產品資料"""
        try:
            print("🔄 重新載入產品資料...")
            self.query_system.load_all_data()
            print("✅ 產品資料重新載入完成")
        except Exception as e:
            print(f"❌ 重新載入產品資料失敗: {e}")
    
    def run_in_background(self):
        """在背景執行排程器"""
        scheduler_thread = threading.Thread(target=self.start_scheduler, daemon=True)
        scheduler_thread.start()
        print("🔄 通知排程器已在背景啟動")
        return scheduler_thread

def main():
    """主程式"""
    scheduler = NotificationScheduler()
    
    print("🍎 Apple 整修品通知排程器")
    print("=" * 50)
    
    try:
        scheduler.start_scheduler()
    except KeyboardInterrupt:
        print("\n👋 排程器已停止")

if __name__ == "__main__":
    main() 