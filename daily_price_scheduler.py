#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日價格追蹤排程器
自動執行價格追蹤並發送降價通知
"""

import schedule
import time
import threading
from datetime import datetime, date
from price_tracker import PriceTracker
from linebot_service import bot_service, line_bot_api
from linebot.models import TextSendMessage, FlexSendMessage
from firebase_enhanced_requests import EnhancedFirebaseRequests
import firebase_admin
from firebase_admin import credentials, firestore

class DailyPriceScheduler:
    def __init__(self):
        """初始化每日價格排程器"""
        self.price_tracker = PriceTracker()
        self.firebase_requests = EnhancedFirebaseRequests()
        
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
    
    def daily_price_tracking(self):
        """執行每日價格追蹤"""
        try:
            print(f"🔍 開始執行每日價格追蹤... {datetime.now()}")
            
            # 執行價格追蹤
            tracking_result = self.price_tracker.track_daily_prices()
            
            # 檢查是否有價格變化
            if tracking_result['price_changes']:
                print(f"💰 發現 {len(tracking_result['price_changes'])} 個價格變化")
                
                # 發送降價通知
                self.send_price_drop_notifications(tracking_result['price_changes'])
                
                # 檢查並處理高波動性產品
                self.handle_price_volatility_notifications(tracking_result['price_changes'])
                
                # 更新用戶通知狀態
                self.update_user_notifications(tracking_result['price_changes'])
            
            # 檢查新產品
            if tracking_result['new_products']:
                print(f"🆕 發現 {len(tracking_result['new_products'])} 個新產品")
                self.send_new_product_notifications(tracking_result['new_products'])
            
            # 記錄執行日誌
            self.log_tracking_execution(tracking_result)
            
            print("✅ 每日價格追蹤完成")
            
        except Exception as e:
            print(f"❌ 每日價格追蹤失敗: {e}")
            self.log_error("daily_price_tracking", str(e))
    
    def send_price_drop_notifications(self, price_changes):
        """發送降價通知給相關用戶"""
        if not self.db:
            return
        
        try:
            # 只處理降價的產品
            price_drops = [change for change in price_changes if change['change_amount'] < 0]
            
            if not price_drops:
                return
            
            print(f"📧 準備發送 {len(price_drops)} 個降價通知...")
            
            # 取得所有未通知的用戶請求
            requests_ref = self.db.collection('requests').where('notice', '==', False)
            requests = requests_ref.stream()
            
            notification_count = 0
            
            for request_doc in requests:
                request_data = request_doc.to_dict()
                user_id = request_data.get('userid')
                requested_product = request_data.get('product')
                max_price = request_data.get('price')
                
                if not all([user_id, requested_product, max_price]):
                    continue
                
                # 檢查是否有符合條件的降價產品
                matching_drops = []
                for drop in price_drops:
                    if (drop['category'] == requested_product and 
                        drop['new_price'] <= max_price):
                        matching_drops.append(drop)
                
                if matching_drops:
                    # 發送降價通知
                    success = self.send_price_drop_message(user_id, matching_drops, requested_product, max_price)
                    
                    if success:
                        # 更新通知狀態
                        request_doc.reference.update({
                            'notice': True,
                            'updated_at': datetime.now(),
                            'notified_products': len(matching_drops),
                            'notification_type': 'price_drop'
                        })
                        notification_count += 1
                        print(f"✅ 已發送降價通知給用戶 {user_id}")
            
            print(f"📧 共發送 {notification_count} 個降價通知")
            
        except Exception as e:
            print(f"❌ 發送降價通知失敗: {e}")
    
    def send_price_drop_message(self, user_id, price_drops, product_type, max_price):
        """發送降價通知訊息"""
        try:
            # 建立降價通知訊息
            drop_info = []
            total_savings = 0
            
            for drop in price_drops:
                savings = abs(drop['change_amount'])
                total_savings += savings
                drop_info.append(f"• {drop['title'][:30]}...\n  原價 NT${drop['old_price']:,} → 現價 NT${drop['new_price']:,}\n  省下 NT${savings:,} ({abs(drop['change_percentage']):.1f}%)")
            
            message_text = f"🎉 好消息！您關注的 {product_type.upper()} 產品降價了！\n\n"
            message_text += f"💰 預算範圍：NT${max_price:,} 以內\n"
            message_text += f"📉 共 {len(price_drops)} 個產品降價，總共可省 NT${total_savings:,}\n\n"
            message_text += "\n\n".join(drop_info)
            message_text += "\n\n🛒 趕快把握機會購買吧！"
            
            # 發送文字訊息
            line_bot_api.push_message(user_id, TextSendMessage(text=message_text))
            
            # 建立產品資料用於 Flex Message
            products_for_flex = []
            for drop in price_drops:
                product_data = {
                    '產品標題': drop['title'],
                    '產品售價': f"NT${drop['new_price']:,}",
                    '產品URL': drop.get('url', 'https://www.apple.com/tw/shop/refurbished'),
                    'category': drop['category']
                }
                products_for_flex.append(product_data)
            
            # 發送產品 Flex Message
            flex_message = bot_service.create_product_flex_message(
                products_for_flex, 
                f"🔥 {product_type.upper()} 降價商品"
            )
            line_bot_api.push_message(user_id, flex_message)
            
            return True
            
        except Exception as e:
            print(f"❌ 發送降價訊息失敗: {e}")
            return False
    
    def send_new_product_notifications(self, new_products):
        """發送新產品通知"""
        if not self.db:
            return
        
        try:
            print(f"🆕 準備發送新產品通知...")
            
            # 按類別分組新產品
            products_by_category = {}
            for product in new_products:
                category = product['category']
                if category not in products_by_category:
                    products_by_category[category] = []
                products_by_category[category].append(product)
            
            # 取得所有未通知的用戶請求
            requests_ref = self.db.collection('requests').where('notice', '==', False)
            requests = requests_ref.stream()
            
            notification_count = 0
            
            for request_doc in requests:
                request_data = request_doc.to_dict()
                user_id = request_data.get('userid')
                requested_product = request_data.get('product')
                max_price = request_data.get('price')
                
                if not all([user_id, requested_product, max_price]):
                    continue
                
                # 檢查是否有符合條件的新產品
                if requested_product in products_by_category:
                    matching_products = []
                    for product in products_by_category[requested_product]:
                        if product['price'] and product['price'] <= max_price:
                            matching_products.append(product)
                    
                    if matching_products:
                        # 發送新產品通知
                        success = self.send_new_product_message(user_id, matching_products, requested_product, max_price)
                        
                        if success:
                            # 更新通知狀態
                            request_doc.reference.update({
                                'notice': True,
                                'updated_at': datetime.now(),
                                'notified_products': len(matching_products),
                                'notification_type': 'new_product'
                            })
                            notification_count += 1
                            print(f"✅ 已發送新產品通知給用戶 {user_id}")
            
            print(f"🆕 共發送 {notification_count} 個新產品通知")
            
        except Exception as e:
            print(f"❌ 發送新產品通知失敗: {e}")
    
    def send_new_product_message(self, user_id, new_products, product_type, max_price):
        """發送新產品通知訊息"""
        try:
            message_text = f"🆕 新品上架！發現符合您需求的 {product_type.upper()} 產品！\n\n"
            message_text += f"💰 預算範圍：NT${max_price:,} 以內\n"
            message_text += f"📦 共 {len(new_products)} 個新產品\n\n"
            
            for i, product in enumerate(new_products[:3], 1):  # 最多顯示3個
                message_text += f"{i}. {product['title'][:30]}...\n"
                message_text += f"   價格：{product['price_str']}\n\n"
            
            if len(new_products) > 3:
                message_text += f"... 還有 {len(new_products) - 3} 個產品\n\n"
            
            message_text += "🛒 趕快查看詳細資訊吧！"
            
            # 發送文字訊息
            line_bot_api.push_message(user_id, TextSendMessage(text=message_text))
            
            # 建立產品資料用於 Flex Message
            products_for_flex = []
            for product in new_products:
                product_data = {
                    '產品標題': product['title'],
                    '產品售價': product['price_str'],
                    '產品URL': product.get('url', 'https://www.apple.com/tw/shop/refurbished'),
                    'category': product['category']
                }
                products_for_flex.append(product_data)
            
            # 發送產品 Flex Message
            flex_message = bot_service.create_product_flex_message(
                products_for_flex, 
                f"🆕 {product_type.upper()} 新品上架"
            )
            line_bot_api.push_message(user_id, flex_message)
            
            return True
            
        except Exception as e:
            print(f"❌ 發送新產品訊息失敗: {e}")
            return False
    
    def handle_price_volatility_notifications(self, price_changes):
        """處理價格波動通知（變化超過10%）"""
        try:
            high_volatility_changes = []
            
            # 篩選出高波動性變化（超過10%）
            for change in price_changes:
                change_percentage = abs(change.get('change_percentage', 0))
                if change_percentage >= 10:
                    high_volatility_changes.append(change)
                    
                    # 記錄價格波動事件到 Firebase
                    self.firebase_requests.record_price_volatility_event(
                        category=change['category'],
                        product_title=change['title'],
                        old_price=change['old_price'],
                        new_price=change['new_price'],
                        change_percentage=change['change_percentage']
                    )
            
            if not high_volatility_changes:
                return
            
            print(f"⚡ 發現 {len(high_volatility_changes)} 個高波動性產品")
            
            # 按類別分組處理
            volatility_by_category = {}
            for change in high_volatility_changes:
                category = change['category']
                if category not in volatility_by_category:
                    volatility_by_category[category] = []
                volatility_by_category[category].append(change)
            
            # 為每個類別發送通知給最近3天內查詢過的用戶
            total_notifications = 0
            
            for category, changes in volatility_by_category.items():
                # 取得最近3天內查詢過該類別的用戶
                recent_users = self.firebase_requests.get_recent_category_users(category, 3)
                
                if not recent_users:
                    continue
                
                # 發送波動通知給這些用戶
                for user in recent_users:
                    success = self.send_volatility_notification(
                        user['userid'], 
                        category, 
                        changes
                    )
                    
                    if success:
                        # 更新用戶通知次數
                        self.firebase_requests.update_user_notification_count(user['doc_id'])
                        
                        # 記錄通知歷史
                        self.firebase_requests.record_notification_sent(
                            userid=user['userid'],
                            notification_type='price_volatility',
                            category=category,
                            content=f"發現 {len(changes)} 個 {category.upper()} 產品價格大幅波動"
                        )
                        
                        total_notifications += 1
                        print(f"📧 已發送波動通知給用戶 {user['userid']} ({category})")
            
            print(f"📊 總共發送了 {total_notifications} 個價格波動通知")
            
        except Exception as e:
            print(f"❌ 處理價格波動通知失敗: {e}")
    
    def send_volatility_notification(self, user_id: str, category: str, changes: List[Dict]) -> bool:
        """發送價格波動通知訊息"""
        try:
            # 分析波動情況
            price_drops = [c for c in changes if c['change_percentage'] < 0]
            price_increases = [c for c in changes if c['change_percentage'] > 0]
            
            # 建立通知訊息
            message_text = f"⚡ {category.upper()} 產品價格大幅波動警報！\n\n"
            message_text += f"📊 發現 {len(changes)} 個產品價格變化超過 10%\n\n"
            
            if price_drops:
                message_text += f"📉 大幅降價 ({len(price_drops)} 個):\n"
                for drop in price_drops[:3]:  # 最多顯示3個
                    savings = abs(drop['change_amount'])
                    message_text += f"• {drop['title'][:30]}...\n"
                    message_text += f"  降價 {abs(drop['change_percentage']):.1f}% (省 NT${savings:,})\n"
                    message_text += f"  現價 NT${drop['new_price']:,}\n\n"
                
                if len(price_drops) > 3:
                    message_text += f"... 還有 {len(price_drops) - 3} 個降價產品\n\n"
            
            if price_increases:
                message_text += f"📈 大幅漲價 ({len(price_increases)} 個):\n"
                for increase in price_increases[:2]:  # 最多顯示2個
                    message_text += f"• {increase['title'][:30]}...\n"
                    message_text += f"  漲價 {increase['change_percentage']:.1f}%\n"
                    message_text += f"  現價 NT${increase['new_price']:,}\n\n"
            
            message_text += "💡 這是因為您最近3天內查詢過此類別產品\n"
            message_text += "🛒 如有興趣請把握機會！"
            
            # 發送文字訊息
            line_bot_api.push_message(user_id, TextSendMessage(text=message_text))
            
            # 如果有降價產品，發送 Flex Message
            if price_drops:
                products_for_flex = []
                for drop in price_drops:
                    product_data = {
                        '產品標題': drop['title'],
                        '產品售價': f"NT${drop['new_price']:,}",
                        '產品URL': drop.get('url', 'https://www.apple.com/tw/shop/refurbished'),
                        'category': drop['category']
                    }
                    products_for_flex.append(product_data)
                
                flex_message = bot_service.create_product_flex_message(
                    products_for_flex, 
                    f"⚡ {category.upper()} 大幅降價商品"
                )
                line_bot_api.push_message(user_id, flex_message)
            
            return True
            
        except Exception as e:
            print(f"❌ 發送波動通知失敗: {e}")
            return False
    
    def update_user_notifications(self, price_changes):
        """更新用戶通知狀態"""
        # 這個方法已經在 send_price_drop_notifications 中處理了
        pass
    
    def log_tracking_execution(self, tracking_result):
        """記錄追蹤執行日誌"""
        if not self.db:
            return
        
        try:
            log_data = {
                'event_type': 'daily_price_tracking',
                'status': 'success',
                'timestamp': datetime.now(),
                'date': tracking_result['date'],
                'total_products': tracking_result['total_products'],
                'price_changes': len(tracking_result['price_changes']),
                'new_products': len(tracking_result['new_products']),
                'discontinued_products': len(tracking_result['discontinued_products']),
                'categories': {
                    category: data['product_count'] 
                    for category, data in tracking_result['categories'].items()
                }
            }
            
            self.db.collection('system_logs').add(log_data)
            print("📝 已記錄追蹤執行日誌")
            
        except Exception as e:
            print(f"❌ 記錄日誌失敗: {e}")
    
    def log_error(self, operation, error_message):
        """記錄錯誤日誌"""
        if not self.db:
            return
        
        try:
            error_log = {
                'event_type': 'system_error',
                'operation': operation,
                'error_message': error_message,
                'timestamp': datetime.now(),
                'status': 'error'
            }
            
            self.db.collection('system_logs').add(error_log)
            print(f"📝 已記錄錯誤日誌: {operation}")
            
        except Exception as e:
            print(f"❌ 記錄錯誤日誌失敗: {e}")
    
    def generate_daily_report(self):
        """生成每日價格報告"""
        try:
            print("📊 生成每日價格報告...")
            
            # 生成價格變化報告
            report = self.price_tracker.generate_price_report(1)  # 今日報告
            
            # 如果有管理員用戶ID，可以發送報告
            # admin_user_id = "YOUR_ADMIN_USER_ID"  # 設定管理員用戶ID
            # if admin_user_id:
            #     line_bot_api.push_message(admin_user_id, TextSendMessage(text=report))
            
            print("✅ 每日報告生成完成")
            print(report)
            
        except Exception as e:
            print(f"❌ 生成每日報告失敗: {e}")
    
    def start_scheduler(self):
        """啟動排程器"""
        print("🚀 啟動每日價格追蹤排程器...")
        
        # 每天早上 9:00 執行價格追蹤
        schedule.every().day.at("09:00").do(self.daily_price_tracking)
        
        # 每天晚上 21:00 執行價格追蹤
        schedule.every().day.at("21:00").do(self.daily_price_tracking)
        
        # 每天晚上 22:00 生成每日報告
        schedule.every().day.at("22:00").do(self.generate_daily_report)
        
        print("⏰ 排程設定完成：")
        print("   - 每天 09:00 執行價格追蹤")
        print("   - 每天 21:00 執行價格追蹤")
        print("   - 每天 22:00 生成每日報告")
        
        # 立即執行一次（測試用）
        print("🔄 立即執行一次價格追蹤...")
        self.daily_price_tracking()
        
        # 持續運行排程
        while True:
            schedule.run_pending()
            time.sleep(60)  # 每分鐘檢查一次排程
    
    def run_in_background(self):
        """在背景執行排程器"""
        scheduler_thread = threading.Thread(target=self.start_scheduler, daemon=True)
        scheduler_thread.start()
        print("🔄 每日價格追蹤排程器已在背景啟動")
        return scheduler_thread

def main():
    """主程式"""
    scheduler = DailyPriceScheduler()
    
    print("🍎 Apple 整修品每日價格追蹤排程器")
    print("=" * 50)
    
    try:
        scheduler.start_scheduler()
    except KeyboardInterrupt:
        print("\n👋 排程器已停止")

if __name__ == "__main__":
    main() 