#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Apple 整修品 Line Bot 服務
支援 Quick Reply 和 Flex Message 功能
"""

import os
import json
from flask import Flask, request, abort
from dotenv import load_dotenv

# 載入 .env 檔案
load_dotenv()
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    QuickReply, QuickReplyButton, MessageAction,
    FlexSendMessage, BubbleContainer, BoxComponent,
    TextComponent, ButtonComponent, URIAction,
    CarouselContainer, PostbackEvent, PostbackAction
)
from chatgpt_query import AppleRefurbishedQuery
from firebase_enhanced_requests import EnhancedFirebaseRequests
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import re

app = Flask(__name__)

# Line Bot 設定
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')

# 初始化 Line Bot API（允許在沒有環境變數時繼續運行）
line_bot_api = None
handler = None

if LINE_CHANNEL_ACCESS_TOKEN and LINE_CHANNEL_SECRET:
    try:
        line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
        handler = WebhookHandler(LINE_CHANNEL_SECRET)
        print("✅ Line Bot API 初始化成功")
    except Exception as e:
        print(f"❌ Line Bot API 初始化失敗: {e}")
        line_bot_api = None
        handler = None
else:
    print("⚠️  Line Bot 環境變數未設定，將使用測試模式")

# 初始化 Firebase
try:
    if not firebase_admin._apps:
        cred = credentials.Certificate('firebase-service-account.json')
        firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("✅ Firebase 初始化成功")
except Exception as e:
    print(f"❌ Firebase 初始化失敗: {e}")
    db = None

# 初始化查詢系統
query_system = AppleRefurbishedQuery()

# 初始化增強版 Firebase Requests
firebase_requests = EnhancedFirebaseRequests()

# 用戶狀態管理
user_states = {}

class LineBotService:
    def __init__(self):
        self.categories_map = {
            'mac': 'Mac',
            'ipad': 'iPad',
            'iphone': 'iPhone',
            'appletv': 'Apple TV',
            'accessories': '配件'
        }
        
        self.price_ranges = {
            'under_20k': {'label': '20,000以內', 'min': 0, 'max': 20000},
            'under_50k': {'label': '50,000以內', 'min': 20001, 'max': 50000},
            'over_50k': {'label': '50,000以上', 'min': 50001, 'max': 999999}
        }
    
    def create_category_quick_reply(self):
        """建立類別選擇 Quick Reply"""
        quick_reply_buttons = []
        
        for category_key, category_name in self.categories_map.items():
            quick_reply_buttons.append(
                QuickReplyButton(
                    action=MessageAction(
                        label=category_name,
                        text=f"查詢{category_name}整修品"
                    )
                )
            )
        
        # 新增其他選項
        quick_reply_buttons.extend([
            QuickReplyButton(
                action=MessageAction(label="最便宜", text="最便宜的產品")
            ),
            QuickReplyButton(
                action=MessageAction(label="最昂貴", text="最昂貴的產品")
            ),
            QuickReplyButton(
                action=MessageAction(label="全部產品", text="顯示所有產品")
            )
        ])
        
        return QuickReply(items=quick_reply_buttons)
    
    def create_price_query_welcome_message(self, display_name):
        """建立查價歡迎訊息"""
        return f"{display_name} 你好！我是福利品查價機器人，請幫我選擇你想尋找的產品"
    
    def create_category_selection_flex(self):
        """建立產品類別選擇 Flex Message"""
        bubble = BubbleContainer(
            body=BoxComponent(
                layout="vertical",
                contents=[
                    TextComponent(
                        text="🍎 選擇產品類別",
                        size="xl",
                        weight="bold",
                        color="#1DB446",
                        align="center"
                    ),
                    TextComponent(
                        text="請選擇您想查詢的產品類別",
                        size="md",
                        color="#666666",
                        align="center",
                        margin="md"
                    )
                ]
            ),
            footer=BoxComponent(
                layout="vertical",
                spacing="sm",
                contents=[
                    ButtonComponent(
                        style="primary",
                        color="#1DB446",
                        action=PostbackAction(
                            label="Mac",
                            data="category_mac"
                        )
                    ),
                    ButtonComponent(
                        style="primary", 
                        color="#1DB446",
                        action=PostbackAction(
                            label="iPad",
                            data="category_ipad"
                        )
                    ),
                    ButtonComponent(
                        style="primary",
                        color="#1DB446", 
                        action=PostbackAction(
                            label="iPhone",
                            data="category_iphone"
                        )
                    ),
                    ButtonComponent(
                        style="primary",
                        color="#1DB446",
                        action=PostbackAction(
                            label="Apple TV",
                            data="category_appletv"
                        )
                    ),
                    ButtonComponent(
                        style="primary",
                        color="#1DB446",
                        action=PostbackAction(
                            label="配件",
                            data="category_accessories"
                        )
                    )
                ]
            )
        )
        
        return FlexSendMessage(
            alt_text="請選擇產品類別",
            contents=bubble
        )
    
    def create_price_range_selection_flex(self, category):
        """建立價格區間選擇 Flex Message"""
        category_name = self.categories_map.get(category, category)
        
        bubble = BubbleContainer(
            body=BoxComponent(
                layout="vertical",
                contents=[
                    TextComponent(
                        text=f"💰 {category_name} 價格區間",
                        size="xl",
                        weight="bold",
                        color="#1DB446",
                        align="center"
                    ),
                    TextComponent(
                        text="請選擇您的預算範圍",
                        size="md",
                        color="#666666",
                        align="center",
                        margin="md"
                    )
                ]
            ),
            footer=BoxComponent(
                layout="vertical",
                spacing="sm",
                contents=[
                    ButtonComponent(
                        style="primary",
                        color="#1DB446",
                        action=PostbackAction(
                            label="NT$ 20,000 以內",
                            data=f"price_{category}_under_20k"
                        )
                    ),
                    ButtonComponent(
                        style="primary",
                        color="#1DB446",
                        action=PostbackAction(
                            label="NT$ 50,000 以內",
                            data=f"price_{category}_under_50k"
                        )
                    ),
                    ButtonComponent(
                        style="primary",
                        color="#1DB446",
                        action=PostbackAction(
                            label="NT$ 50,000 以上",
                            data=f"price_{category}_over_50k"
                        )
                    )
                ]
            )
        )
        
        return FlexSendMessage(
            alt_text="請選擇價格區間",
            contents=bubble
        )
    
    def create_product_carousel_with_notification(self, products, category, price_range):
        """建立產品輪播訊息（包含通知選項）"""
        if not products:
            return TextSendMessage(text="很抱歉，目前沒有符合條件的產品 😔")
        
        bubbles = []
        
        # 建立產品 bubbles（最多9個，為通知選項留空間）
        for product in products[:9]:
            bubble = self.create_square_product_bubble(product)
            bubbles.append(bubble)
        
        # 新增通知選項 bubble
        notification_bubble = BubbleContainer(
            body=BoxComponent(
                layout="vertical",
                spacing="sm",
                contents=[
                    TextComponent(
                        text="🔔",
                        size="xxl",
                        align="center",
                        color="#FF5551"
                    ),
                    TextComponent(
                        text="沒有中意想要的嗎？",
                        size="md",
                        weight="bold",
                        align="center",
                        wrap=True
                    ),
                    TextComponent(
                        text="等商品上架我們會主動通知你！",
                        size="sm",
                        align="center",
                        wrap=True,
                        color="#666666"
                    )
                ]
            ),
            footer=BoxComponent(
                layout="vertical",
                contents=[
                    ButtonComponent(
                        style="primary",
                        color="#FF5551",
                        action=PostbackAction(
                            label="設定通知",
                            data=f"notify_{category}_{price_range}"
                        )
                    )
                ]
            )
        )
        
        bubbles.append(notification_bubble)
        
        carousel = CarouselContainer(contents=bubbles)
        return FlexSendMessage(
            alt_text=f"找到 {len(products)} 個產品",
            contents=carousel
        )
    
    def create_square_product_bubble(self, product):
        """建立正方形產品 bubble"""
        title = product.get('產品標題', 'Apple 產品')
        price = product.get('產品售價', 'N/A')
        category = product.get('category', '').upper()
        url = product.get('產品URL', 'https://www.apple.com/tw/shop/refurbished')
        
        # 縮短標題
        if len(title) > 30:
            title = title[:27] + "..."
        
        bubble = BubbleContainer(
            size="kilo",  # 正方形尺寸
            body=BoxComponent(
                layout="vertical",
                spacing="sm",
                contents=[
                    TextComponent(
                        text=category,
                        size="xs",
                        color="#999999",
                        weight="bold",
                        align="center"
                    ),
                    TextComponent(
                        text=title,
                        size="sm",
                        weight="bold",
                        wrap=True,
                        align="center",
                        maxLines=2
                    ),
                    TextComponent(
                        text=price,
                        size="md",
                        weight="bold",
                        color="#FF5551",
                        align="center"
                    )
                ]
            ),
            footer=BoxComponent(
                layout="vertical",
                contents=[
                    ButtonComponent(
                        style="primary",
                        color="#1DB446",
                        action=URIAction(
                            label="查看詳情",
                            uri=url
                        )
                    )
                ]
            )
        )
        
        return bubble
    
    def save_user_request(self, user_id, product=None, price=None, category=None, notice=False):
        """儲存用戶請求到 Firebase（支援 category 欄位）"""
        if not firebase_requests:
            return False
        
        try:
            # 使用增強版 Firebase Requests 系統
            return firebase_requests.create_user_request(
                userid=user_id,
                product=product or category,  # product 和 category 可能相同
                price=price,
                category=category or product  # 確保 category 有值
            )
        except Exception as e:
            print(f"❌ 儲存用戶請求失敗: {e}")
            return False
    
    def parse_user_requirement(self, text):
        """解析用戶需求文字，提取產品和價格"""
        # 提取價格
        price_match = re.search(r'(\d+(?:,\d+)*)', text)
        price = int(price_match.group(1).replace(',', '')) if price_match else None
        
        # 提取產品關鍵字
        product_keywords = ['mac', 'ipad', 'iphone', 'airpods', 'homepod', 'apple tv', '配件']
        product = None
        
        text_lower = text.lower()
        for keyword in product_keywords:
            if keyword in text_lower:
                product = keyword
                break
        
        return product, price
    
    def check_and_notify_users(self):
        """檢查並通知符合條件的用戶"""
        if not db:
            return
        
        try:
            # 取得所有未通知的請求
            requests_ref = db.collection('requests').where('notice', '==', False)
            requests = requests_ref.stream()
            
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
                    self.send_product_notification(user_id, matching_products, product, max_price)
                    
                    # 更新通知狀態
                    request_doc.reference.update({'notice': True, 'updated_at': datetime.now()})
                    
        except Exception as e:
            print(f"❌ 檢查用戶通知失敗: {e}")
    
    def find_matching_products(self, product, max_price):
        """尋找符合條件的產品"""
        # 根據產品類別搜尋
        products = query_system.search_by_category(product)
        
        # 篩選價格符合的產品
        matching_products = []
        for prod in products:
            price = query_system.extract_price(prod.get('產品售價', ''))
            if price and price <= max_price:
                matching_products.append(prod)
        
        return matching_products[:5]  # 最多5個產品
    
    def send_product_notification(self, user_id, products, product_type, max_price):
        """發送產品通知給用戶"""
        try:
            message = f"🎉 好消息！我們找到了符合您需求的 {product_type.upper()} 產品（預算 NT${max_price:,} 以內）："
            
            line_bot_api.push_message(user_id, TextSendMessage(text=message))
            
            # 發送產品 Flex Message
            flex_message = self.create_product_flex_message(products, f"{product_type.upper()} 推薦")
            line_bot_api.push_message(user_id, flex_message)
            
        except Exception as e:
            print(f"❌ 發送通知失敗: {e}")
    
    def create_product_flex_message(self, products, title="Apple 整修品"):
        """建立產品 Flex Message"""
        if not products:
            return TextSendMessage(text="沒有找到符合條件的產品 😔")
        
        # 如果只有一個產品，建立單一 Bubble
        if len(products) == 1:
            bubble = self.create_product_bubble(products[0])
            return FlexSendMessage(
                alt_text=f"{title} - {products[0].get('產品標題', 'Apple 產品')}",
                contents=bubble
            )
        
        # 多個產品建立 Carousel
        bubbles = []
        for product in products[:10]:  # 限制最多 10 個產品
            bubble = self.create_product_bubble(product)
            bubbles.append(bubble)
        
        carousel = CarouselContainer(contents=bubbles)
        return FlexSendMessage(
            alt_text=f"{title} - 找到 {len(products)} 個產品",
            contents=carousel
        )
    
    def create_product_bubble(self, product):
        """建立單一產品 Bubble"""
        title = product.get('產品標題', 'Apple 產品')
        price = product.get('產品售價', 'N/A')
        category = product.get('category', '').upper()
        url = product.get('產品URL', 'https://www.apple.com/tw/shop/refurbished')
        
        # 縮短標題以適應 Flex Message
        if len(title) > 40:
            title = title[:37] + "..."
        
        # 檢查是否為通用類別頁面 URL
        is_generic_url = any(generic in url for generic in [
            '/shop/refurbished/ipad',
            '/shop/refurbished/airpods', 
            '/shop/refurbished/homepod',
            '/shop/refurbished/accessories',
            '/shop/refurbished/iphone',
            '/shop/refurbished/appletv'
        ])
        
        # 根據 URL 類型設定按鈕文字和動作
        if is_generic_url:
            button_text = f"瀏覽{category}整修品"
            # 可以考慮改為搜尋動作而非直接連結
            button_action = URIAction(label=button_text, uri=url)
        else:
            button_text = "查看產品詳情"
            button_action = URIAction(label=button_text, uri=url)
        
        bubble = BubbleContainer(
            hero=None,  # 可以加入產品圖片
            body=BoxComponent(
                layout="vertical",
                contents=[
                    TextComponent(
                        text=category,
                        size="sm",
                        color="#999999",
                        weight="bold"
                    ),
                    TextComponent(
                        text=title,
                        size="md",
                        weight="bold",
                        wrap=True,
                        margin="sm"
                    ),
                    TextComponent(
                        text=price,
                        size="xl",
                        weight="bold",
                        color="#FF5551",
                        margin="md"
                    )
                ]
            ),
            footer=BoxComponent(
                layout="vertical",
                contents=[
                    ButtonComponent(
                        style="primary",
                        color="#1DB446",
                        action=button_action
                    )
                ]
            )
        )
        
        return bubble
    
    def create_summary_flex_message(self):
        """建立產品總覽 Flex Message"""
        summary = query_system.get_summary()
        
        contents = [
            TextComponent(
                text="🍎 Apple 整修品總覽",
                size="xl",
                weight="bold",
                color="#1DB446"
            ),
            TextComponent(
                text=f"總產品數：{summary['total_products']} 個",
                size="md",
                margin="md"
            )
        ]
        
        # 新增各類別統計
        for category, count in summary['categories'].items():
            if count > 0:
                category_name = self.categories_map.get(category, category.upper())
                contents.append(
                    TextComponent(
                        text=f"{category_name}：{count} 個",
                        size="sm",
                        color="#666666",
                        margin="xs"
                    )
                )
        
        # 新增價格範圍
        contents.append(
            TextComponent(
                text=f"價格範圍：NT${summary['price_range']['min']:,} - NT${summary['price_range']['max']:,}",
                size="sm",
                color="#666666",
                margin="md"
            )
        )
        
        bubble = BubbleContainer(
            body=BoxComponent(
                layout="vertical",
                contents=contents
            ),
            footer=BoxComponent(
                layout="vertical",
                contents=[
                    ButtonComponent(
                        style="secondary",
                        action=MessageAction(
                            label="開始查詢",
                            text="我想查詢產品"
                        )
                    )
                ]
            )
        )
        
        return FlexSendMessage(
            alt_text="Apple 整修品總覽",
            contents=bubble
        )

# 建立 LineBotService 實例
bot_service = LineBotService()

# 啟動通知排程器
try:
    from notification_scheduler import NotificationScheduler
    notification_scheduler = NotificationScheduler()
    notification_scheduler.run_in_background()
except Exception as e:
    print(f"⚠️ 通知排程器啟動失敗: {e}")
    notification_scheduler = None

@app.route("/webhook", methods=['POST'])
def callback():
    """Line Bot Webhook"""
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    """處理文字訊息"""
    user_id = event.source.user_id
    message_text = event.message.text.strip()
    user_message = message_text.lower()
    
    try:
        # 取得用戶資訊
        profile = line_bot_api.get_profile(user_id)
        display_name = profile.display_name
    except:
        display_name = "朋友"
    
    # 檢查用戶狀態
    user_state = user_states.get(user_id, {})
    
    # 處理查價流程
    if message_text == "我要查價":
        # 步驟1: 歡迎訊息和類別選擇
        welcome_text = bot_service.create_price_query_welcome_message(display_name)
        category_flex = bot_service.create_category_selection_flex()
        
        # 記錄用戶開始查價流程
        user_states[user_id] = {'state': 'price_query_started'}
        bot_service.save_user_request(user_id)  # 記錄用戶ID到資料庫
        
        # 回覆歡迎訊息和類別選擇
        line_bot_api.reply_message(event.reply_token, [
            TextSendMessage(text=welcome_text),
            category_flex
        ])
        return
    
    # 處理通知設定後的用戶輸入
    elif user_state.get('state') == 'waiting_for_requirement':
        # 步驟5: 解析用戶需求
        product, price = bot_service.parse_user_requirement(message_text)
        category = user_state.get('category')  # 取得用戶之前選擇的類別
        
        if product and price and category:
            # 儲存用戶需求到資料庫（包含 category）
            bot_service.save_user_request(
                user_id=user_id, 
                product=product, 
                price=price, 
                category=category,
                notice=False
            )
            
            reply_text = f"✅ 已記錄您的需求：\n類別：{category.upper()}\n產品：{product.upper()}\n預算：NT${price:,}\n\n當有符合條件的產品時，我們會立即通知您！\n\n💡 如果該類別產品價格波動超過10%，我們也會在3天內主動通知您！"
            user_states[user_id] = {}  # 清除狀態
        else:
            reply_text = "請提供更詳細的資訊，例如：「我想要 MacBook Air 預算30000元」"
        
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
        return
    
    reply_messages = []
    
    # 歡迎訊息
    if any(keyword in user_message for keyword in ['hi', 'hello', '你好', '嗨', '開始']):
        reply_messages.append(
            TextSendMessage(
                text=f"🍎 歡迎使用 Apple 整修品查詢服務！{display_name}\n\n請選擇您想查詢的產品類別：\n\n💡 輸入「我要查價」開始智能查詢！",
                quick_reply=bot_service.create_category_quick_reply()
            )
        )
    
    # 總覽查詢
    elif any(keyword in user_message for keyword in ['總覽', '概覽', '統計', '全部']):
        reply_messages.append(bot_service.create_summary_flex_message())
    
    # 類別查詢
    elif 'mac' in user_message or 'Mac' in event.message.text:
        products = query_system.search_by_category('mac')
        reply_messages.append(
            bot_service.create_product_flex_message(products, "Mac 整修品")
        )
    
    elif 'ipad' in user_message or 'iPad' in event.message.text:
        products = query_system.search_by_category('ipad')
        reply_messages.append(
            bot_service.create_product_flex_message(products, "iPad 整修品")
        )
    
    elif 'airpods' in user_message or 'AirPods' in event.message.text:
        products = query_system.search_by_category('airpods')
        reply_messages.append(
            bot_service.create_product_flex_message(products, "AirPods 整修品")
        )
    
    elif 'homepod' in user_message or 'HomePod' in event.message.text:
        products = query_system.search_by_category('homepod')
        reply_messages.append(
            bot_service.create_product_flex_message(products, "HomePod 整修品")
        )
    
    elif '配件' in user_message or 'accessories' in user_message:
        products = query_system.search_by_category('accessories')
        reply_messages.append(
            bot_service.create_product_flex_message(products, "配件整修品")
        )
    
    # 價格查詢
    elif '便宜' in user_message or '最低' in user_message:
        products = query_system.get_cheapest_products(5)
        reply_messages.append(
            bot_service.create_product_flex_message(products, "最便宜的產品")
        )
    
    elif '昂貴' in user_message or '最高' in user_message or '貴' in user_message:
        products = query_system.get_most_expensive_products(5)
        reply_messages.append(
            bot_service.create_product_flex_message(products, "最昂貴的產品")
        )
    
    # 關鍵字搜尋
    elif any(keyword in user_message for keyword in ['macbook', 'imac', 'mini', 'pro', 'air']):
        # 提取關鍵字
        for keyword in ['macbook', 'imac', 'mini', 'pro', 'air']:
            if keyword in user_message:
                products = query_system.search_by_keyword(keyword)
                reply_messages.append(
                    bot_service.create_product_flex_message(products, f"{keyword.title()} 產品")
                )
                break
    
    # 查詢指令
    elif '查詢' in user_message or '搜尋' in user_message:
        reply_messages.append(
            TextSendMessage(
                text="請選擇查詢方式：\n\n💡 輸入「我要查價」開始智能查詢！",
                quick_reply=bot_service.create_category_quick_reply()
            )
        )
    
    # 幫助訊息
    elif '幫助' in user_message or 'help' in user_message or '說明' in user_message:
        help_text = """🍎 Apple 整修品查詢服務使用說明

📱 支援查詢：
• Mac 整修品
• iPad 整修品  
• AirPods 整修品
• HomePod 整修品
• 配件整修品

🔍 查詢方式：
• 輸入產品類別名稱
• 輸入「最便宜」或「最昂貴」
• 輸入產品關鍵字（如：MacBook、iMac）
• 輸入「總覽」查看統計
• 輸入「我要查價」開始智能查詢

💡 小提示：
點擊下方快速選單可以快速查詢！"""
        
        reply_messages.append(
            TextSendMessage(
                text=help_text,
                quick_reply=bot_service.create_category_quick_reply()
            )
        )
    
    # 預設回應
    else:
        reply_messages.append(
            TextSendMessage(
                text="抱歉，我不太理解您的需求 😅\n\n請選擇以下選項或輸入「幫助」查看使用說明：\n\n💡 輸入「我要查價」開始智能查詢！",
                quick_reply=bot_service.create_category_quick_reply()
            )
        )
    
    # 發送回應
    if reply_messages:
        line_bot_api.reply_message(event.reply_token, reply_messages)

@handler.add(PostbackEvent)
def handle_postback(event):
    """處理 Postback 事件"""
    user_id = event.source.user_id
    postback_data = event.postback.data
    
    # 處理查價流程的類別選擇
    if postback_data.startswith('category_') and user_states.get(user_id, {}).get('state') == 'price_query_started':
        # 步驟2: 用戶選擇了產品類別，顯示價格區間選擇
        category = postback_data.replace('category_', '')
        user_states[user_id]['selected_category'] = category
        
        price_range_flex = bot_service.create_price_range_selection_flex(category)
        line_bot_api.reply_message(event.reply_token, price_range_flex)
        
    # 處理查價流程的價格區間選擇
    elif postback_data.startswith('price_'):
        # 步驟3: 用戶選擇了價格區間，顯示產品輪播
        parts = postback_data.split('_')
        if len(parts) >= 3:
            category = parts[1]
            price_range = parts[2]
            
            # 更新用戶狀態
            if user_id in user_states:
                user_states[user_id]['selected_price_range'] = price_range
            
            # 根據類別和價格範圍搜尋產品
            price_info = bot_service.price_ranges.get(price_range, {})
            min_price = price_info.get('min', 0)
            max_price = price_info.get('max', 999999)
            
            # 先按類別搜尋，再按價格篩選
            category_products = query_system.search_by_category(category)
            filtered_products = []
            
            for product in category_products:
                price = query_system.extract_price(product.get('產品售價', ''))
                if price and min_price <= price <= max_price:
                    filtered_products.append(product)
            
            # 建立產品輪播訊息（包含通知選項）
            carousel_message = bot_service.create_product_carousel_with_notification(
                filtered_products, category, price_range
            )
            line_bot_api.reply_message(event.reply_token, carousel_message)
    
    # 處理通知設定
    elif postback_data.startswith('notify_'):
        # 步驟4: 用戶點擊了通知設定
        parts = postback_data.split('_')
        if len(parts) >= 3:
            category = parts[1]
            price_range = parts[2]
            
            # 設定用戶狀態為等待需求輸入
            user_states[user_id] = {
                'state': 'waiting_for_requirement',
                'category': category,
                'price_range': price_range
            }
            
            reply_text = "請輸入你想要購買的產品以及可接受價格，我們會把您的需求加入排程，當有對應產品出現時我們會主動通知！\n\n例如：「我想要 MacBook Air 預算30000元」"
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
    
    # 原有的類別查詢（非查價流程）
    elif postback_data.startswith('category_'):
        category = postback_data.replace('category_', '')
        products = query_system.search_by_category(category)
        category_name = bot_service.categories_map.get(category, category.upper())
        
        reply_message = bot_service.create_product_flex_message(
            products, f"{category_name} 整修品"
        )
        line_bot_api.reply_message(event.reply_token, reply_message)

@app.route("/")
def home():
    """首頁"""
    return """
    <h1>🍎 Apple 整修品 Line Bot</h1>
    <p>Line Bot 服務正在運行中...</p>
    <p>請將此 URL 設定為 Line Bot 的 Webhook URL：</p>
    <code>{}/webhook</code>
    """.format(request.url_root.rstrip('/'))

@app.route("/health")
def health_check():
    """健康檢查"""
    return {"status": "ok", "products_loaded": len(query_system.all_products)}

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False) 