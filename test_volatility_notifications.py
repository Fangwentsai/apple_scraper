#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試價格波動通知功能
"""

import json
from datetime import datetime, timedelta
from firebase_enhanced_requests import EnhancedFirebaseRequests
from daily_price_scheduler import DailyPriceScheduler

def create_test_data():
    """建立測試資料"""
    firebase_requests = EnhancedFirebaseRequests()
    
    print("🧪 建立測試用戶請求...")
    
    # 建立測試用戶請求（包含 category）
    test_users = [
        {
            'userid': 'test_user_mac_001',
            'product': 'macbook',
            'price': 35000,
            'category': 'mac'
        },
        {
            'userid': 'test_user_mac_002', 
            'product': 'imac',
            'price': 50000,
            'category': 'mac'
        },
        {
            'userid': 'test_user_ipad_001',
            'product': 'ipad',
            'price': 25000,
            'category': 'ipad'
        }
    ]
    
    for user in test_users:
        firebase_requests.create_user_request(
            userid=user['userid'],
            product=user['product'],
            price=user['price'],
            category=user['category']
        )
    
    print("✅ 測試用戶請求建立完成")

def create_test_price_changes():
    """建立測試價格變化資料"""
    print("🧪 建立測試價格變化資料...")
    
    # 模擬高波動性價格變化（超過10%）
    test_price_changes = [
        {
            'title': 'MacBook Air M2 8GB 256GB - 太空灰色 (整修品)',
            'category': 'mac',
            'old_price': 35000,
            'new_price': 28000,  # 降價20%
            'change_amount': -7000,
            'change_percentage': -20.0,
            'url': 'https://www.apple.com/tw/shop/product/FQKW3TA/A'
        },
        {
            'title': 'iMac 24吋 M1 8GB 256GB - 藍色 (整修品)',
            'category': 'mac',
            'old_price': 45000,
            'new_price': 38000,  # 降價15.6%
            'change_amount': -7000,
            'change_percentage': -15.6,
            'url': 'https://www.apple.com/tw/shop/product/MGPK3TA/A'
        },
        {
            'title': 'iPad Pro 11吋 M2 128GB Wi-Fi - 太空灰色 (整修品)',
            'category': 'ipad',
            'old_price': 25000,
            'new_price': 21000,  # 降價16%
            'change_amount': -4000,
            'change_percentage': -16.0,
            'url': 'https://www.apple.com/tw/shop/product/MNXE3TA/A'
        },
        {
            'title': 'MacBook Pro 13吋 M2 8GB 256GB - 太空灰色 (整修品)',
            'category': 'mac',
            'old_price': 40000,
            'new_price': 45000,  # 漲價12.5%
            'change_amount': 5000,
            'change_percentage': 12.5,
            'url': 'https://www.apple.com/tw/shop/product/MNEH3TA/A'
        }
    ]
    
    return test_price_changes

def test_volatility_detection():
    """測試價格波動偵測"""
    print("🧪 測試價格波動偵測功能...")
    
    scheduler = DailyPriceScheduler()
    test_changes = create_test_price_changes()
    
    # 測試價格波動處理
    scheduler.handle_price_volatility_notifications(test_changes)
    
    print("✅ 價格波動偵測測試完成")

def test_recent_users_query():
    """測試最近用戶查詢功能"""
    print("🧪 測試最近用戶查詢功能...")
    
    firebase_requests = EnhancedFirebaseRequests()
    
    # 查詢最近3天內查詢過 Mac 的用戶
    recent_mac_users = firebase_requests.get_recent_category_users('mac', 3)
    print(f"📊 最近3天內查詢 Mac 的用戶: {len(recent_mac_users)} 個")
    
    for user in recent_mac_users:
        print(f"  - 用戶ID: {user['userid']}")
        print(f"    類別: {user['category']}")
        print(f"    最後查詢: {user['last_query_date']}")
        print(f"    通知次數: {user['notification_count']}")
    
    # 查詢最近3天內查詢過 iPad 的用戶
    recent_ipad_users = firebase_requests.get_recent_category_users('ipad', 3)
    print(f"📊 最近3天內查詢 iPad 的用戶: {len(recent_ipad_users)} 個")
    
    print("✅ 最近用戶查詢測試完成")

def test_volatility_events():
    """測試價格波動事件記錄"""
    print("🧪 測試價格波動事件記錄...")
    
    firebase_requests = EnhancedFirebaseRequests()
    
    # 記錄測試波動事件
    event_id = firebase_requests.record_price_volatility_event(
        category='mac',
        product_title='測試產品 MacBook Air M2',
        old_price=35000,
        new_price=28000,
        change_percentage=-20.0
    )
    
    if event_id:
        print(f"✅ 波動事件記錄成功，ID: {event_id}")
        
        # 查詢高波動性產品
        volatile_products = firebase_requests.get_high_volatility_products(1)
        print(f"📊 找到 {len(volatile_products)} 個高波動性產品")
        
        for product in volatile_products:
            print(f"  - {product['product_title']}")
            print(f"    變化: {product['change_percentage']:.1f}%")
            print(f"    類別: {product['category']}")
    
    print("✅ 價格波動事件測試完成")

def test_notification_history():
    """測試通知歷史記錄"""
    print("🧪 測試通知歷史記錄...")
    
    firebase_requests = EnhancedFirebaseRequests()
    
    # 記錄測試通知
    firebase_requests.record_notification_sent(
        userid='test_user_mac_001',
        notification_type='price_volatility',
        category='mac',
        content='Mac 產品價格大幅波動通知'
    )
    
    # 查詢通知歷史
    history = firebase_requests.get_user_notification_history('test_user_mac_001', 7)
    print(f"📊 用戶通知歷史: {len(history)} 筆記錄")
    
    for record in history:
        print(f"  - 類型: {record.get('notification_type')}")
        print(f"    類別: {record.get('category')}")
        print(f"    時間: {record.get('timestamp')}")
    
    print("✅ 通知歷史測試完成")

def main():
    """主測試函數"""
    print("🚀 開始測試價格波動通知功能")
    print("=" * 60)
    
    try:
        # 1. 建立測試資料
        create_test_data()
        print()
        
        # 2. 測試最近用戶查詢
        test_recent_users_query()
        print()
        
        # 3. 測試價格波動事件記錄
        test_volatility_events()
        print()
        
        # 4. 測試通知歷史
        test_notification_history()
        print()
        
        # 5. 測試價格波動偵測（這會發送實際通知，請小心使用）
        print("⚠️  注意：以下測試會發送實際的 Line 通知")
        user_input = input("是否要測試實際通知發送？(y/N): ")
        
        if user_input.lower() == 'y':
            test_volatility_detection()
        else:
            print("⏭️  跳過實際通知測試")
        
        print("\n🎉 所有測試完成！")
        
    except Exception as e:
        print(f"❌ 測試過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 