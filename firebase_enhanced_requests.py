#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增強版 Firebase Requests 管理系統
支援 category 欄位和價格波動通知功能
"""

import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json

class EnhancedFirebaseRequests:
    def __init__(self):
        """初始化 Firebase 連接"""
        try:
            if not firebase_admin._apps:
                cred = credentials.Certificate('firebase-service-account.json')
                firebase_admin.initialize_app(cred)
            self.db = firestore.client()
            print("✅ Firebase 初始化成功")
        except Exception as e:
            print(f"❌ Firebase 初始化失敗: {e}")
            self.db = None
    
    def create_user_request(self, userid: str, product: str, price: int, category: str) -> bool:
        """建立用戶請求記錄（新增 category 欄位）"""
        if not self.db:
            return False
        
        try:
            request_data = {
                'userid': userid,
                'product': product,
                'price': price,
                'category': category,  # 新增類別欄位
                'notice': False,
                'created_at': datetime.now(),
                'updated_at': datetime.now(),
                'last_query_date': datetime.now().date().isoformat(),  # 記錄最後查詢日期
                'notification_count': 0,  # 通知次數
                'active': True  # 是否啟用
            }
            
            # 檢查是否已存在相同的請求
            existing_query = self.db.collection('requests').where('userid', '==', userid)\
                                   .where('category', '==', category)\
                                   .where('active', '==', True).limit(1)
            
            existing_docs = list(existing_query.stream())
            
            if existing_docs:
                # 更新現有請求
                doc_ref = existing_docs[0].reference
                doc_ref.update({
                    'product': product,
                    'price': price,
                    'updated_at': datetime.now(),
                    'last_query_date': datetime.now().date().isoformat()
                })
                print(f"✅ 更新用戶 {userid} 的 {category} 類別請求")
            else:
                # 建立新請求
                self.db.collection('requests').add(request_data)
                print(f"✅ 建立用戶 {userid} 的 {category} 類別請求")
            
            return True
            
        except Exception as e:
            print(f"❌ 建立用戶請求失敗: {e}")
            return False
    
    def get_recent_category_users(self, category: str, days: int = 3) -> List[Dict]:
        """取得最近N天內查詢過特定類別的用戶"""
        if not self.db:
            return []
        
        try:
            # 計算N天前的日期
            cutoff_date = (datetime.now() - timedelta(days=days)).date().isoformat()
            
            # 查詢最近N天內查詢過該類別的用戶
            query = self.db.collection('requests')\
                          .where('category', '==', category)\
                          .where('last_query_date', '>=', cutoff_date)\
                          .where('active', '==', True)
            
            users = []
            for doc in query.stream():
                data = doc.to_dict()
                users.append({
                    'doc_id': doc.id,
                    'userid': data.get('userid'),
                    'category': data.get('category'),
                    'last_query_date': data.get('last_query_date'),
                    'notification_count': data.get('notification_count', 0)
                })
            
            print(f"📊 找到 {len(users)} 個用戶最近 {days} 天內查詢過 {category} 類別")
            return users
            
        except Exception as e:
            print(f"❌ 取得最近類別用戶失敗: {e}")
            return []
    
    def update_user_notification_count(self, doc_id: str) -> bool:
        """更新用戶通知次數"""
        if not self.db:
            return False
        
        try:
            doc_ref = self.db.collection('requests').document(doc_id)
            doc_ref.update({
                'notification_count': firestore.Increment(1),
                'last_notification_date': datetime.now()
            })
            return True
            
        except Exception as e:
            print(f"❌ 更新通知次數失敗: {e}")
            return False
    
    def record_price_volatility_event(self, category: str, product_title: str, 
                                    old_price: int, new_price: int, 
                                    change_percentage: float) -> bool:
        """記錄價格波動事件"""
        if not self.db:
            return False
        
        try:
            volatility_data = {
                'category': category,
                'product_title': product_title,
                'old_price': old_price,
                'new_price': new_price,
                'change_amount': new_price - old_price,
                'change_percentage': change_percentage,
                'event_type': 'price_drop' if change_percentage < 0 else 'price_increase',
                'severity': 'high' if abs(change_percentage) >= 10 else 'medium',
                'timestamp': datetime.now(),
                'date': datetime.now().date().isoformat(),
                'notified_users': 0  # 將記錄通知了多少用戶
            }
            
            doc_ref = self.db.collection('price_volatility_events').add(volatility_data)
            print(f"📊 記錄價格波動事件: {product_title} 變化 {change_percentage:.1f}%")
            
            return doc_ref[1].id  # 返回文件ID
            
        except Exception as e:
            print(f"❌ 記錄價格波動事件失敗: {e}")
            return False
    
    def get_high_volatility_products(self, days: int = 1) -> List[Dict]:
        """取得高波動性產品（變化超過10%）"""
        if not self.db:
            return []
        
        try:
            # 計算查詢日期範圍
            start_date = (datetime.now() - timedelta(days=days)).date().isoformat()
            
            # 查詢高波動性事件
            query = self.db.collection('price_volatility_events')\
                          .where('date', '>=', start_date)\
                          .where('severity', '==', 'high')\
                          .order_by('timestamp', direction=firestore.Query.DESCENDING)
            
            events = []
            for doc in query.stream():
                data = doc.to_dict()
                events.append({
                    'doc_id': doc.id,
                    'category': data.get('category'),
                    'product_title': data.get('product_title'),
                    'old_price': data.get('old_price'),
                    'new_price': data.get('new_price'),
                    'change_percentage': data.get('change_percentage'),
                    'event_type': data.get('event_type'),
                    'timestamp': data.get('timestamp'),
                    'notified_users': data.get('notified_users', 0)
                })
            
            print(f"📊 找到 {len(events)} 個高波動性產品事件")
            return events
            
        except Exception as e:
            print(f"❌ 取得高波動性產品失敗: {e}")
            return []
    
    def update_volatility_notification_count(self, event_doc_id: str, user_count: int) -> bool:
        """更新波動事件的通知用戶數量"""
        if not self.db:
            return False
        
        try:
            doc_ref = self.db.collection('price_volatility_events').document(event_doc_id)
            doc_ref.update({
                'notified_users': user_count,
                'notification_completed': True,
                'notification_completed_at': datetime.now()
            })
            return True
            
        except Exception as e:
            print(f"❌ 更新波動通知計數失敗: {e}")
            return False
    
    def get_user_notification_history(self, userid: str, days: int = 7) -> List[Dict]:
        """取得用戶通知歷史"""
        if not self.db:
            return []
        
        try:
            start_date = datetime.now() - timedelta(days=days)
            
            # 查詢用戶的通知歷史
            query = self.db.collection('notification_history')\
                          .where('userid', '==', userid)\
                          .where('timestamp', '>=', start_date)\
                          .order_by('timestamp', direction=firestore.Query.DESCENDING)
            
            history = []
            for doc in query.stream():
                data = doc.to_dict()
                history.append(data)
            
            return history
            
        except Exception as e:
            print(f"❌ 取得用戶通知歷史失敗: {e}")
            return []
    
    def record_notification_sent(self, userid: str, notification_type: str, 
                               category: str, content: str) -> bool:
        """記錄已發送的通知"""
        if not self.db:
            return False
        
        try:
            notification_data = {
                'userid': userid,
                'notification_type': notification_type,  # 'price_drop', 'price_volatility', 'new_product'
                'category': category,
                'content': content,
                'timestamp': datetime.now(),
                'date': datetime.now().date().isoformat()
            }
            
            self.db.collection('notification_history').add(notification_data)
            return True
            
        except Exception as e:
            print(f"❌ 記錄通知歷史失敗: {e}")
            return False
    
    def cleanup_old_requests(self, days: int = 30) -> int:
        """清理舊的請求記錄"""
        if not self.db:
            return 0
        
        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).date().isoformat()
            
            # 查詢舊的請求
            query = self.db.collection('requests')\
                          .where('last_query_date', '<', cutoff_date)\
                          .where('active', '==', True)
            
            deleted_count = 0
            batch = self.db.batch()
            
            for doc in query.stream():
                batch.update(doc.reference, {'active': False, 'deactivated_at': datetime.now()})
                deleted_count += 1
                
                # 每100個文件提交一次
                if deleted_count % 100 == 0:
                    batch.commit()
                    batch = self.db.batch()
            
            # 提交剩餘的更新
            if deleted_count % 100 != 0:
                batch.commit()
            
            print(f"🧹 清理了 {deleted_count} 個舊的請求記錄")
            return deleted_count
            
        except Exception as e:
            print(f"❌ 清理舊請求失敗: {e}")
            return 0

def main():
    """測試程式"""
    firebase_requests = EnhancedFirebaseRequests()
    
    print("🧪 測試增強版 Firebase Requests 系統")
    print("=" * 50)
    
    # 測試建立用戶請求
    print("\n1. 測試建立用戶請求...")
    firebase_requests.create_user_request(
        userid="test_user_001",
        product="mac",
        price=30000,
        category="mac"
    )
    
    # 測試取得最近類別用戶
    print("\n2. 測試取得最近類別用戶...")
    recent_users = firebase_requests.get_recent_category_users("mac", 3)
    print(f"找到 {len(recent_users)} 個最近查詢 Mac 的用戶")
    
    # 測試記錄價格波動事件
    print("\n3. 測試記錄價格波動事件...")
    firebase_requests.record_price_volatility_event(
        category="mac",
        product_title="MacBook Air M2 8GB 256GB - 太空灰色 (整修品)",
        old_price=30000,
        new_price=25000,
        change_percentage=-16.67
    )
    
    # 測試取得高波動性產品
    print("\n4. 測試取得高波動性產品...")
    volatile_products = firebase_requests.get_high_volatility_products(1)
    print(f"找到 {len(volatile_products)} 個高波動性產品")
    
    print("\n✅ 測試完成！")

if __name__ == "__main__":
    main() 