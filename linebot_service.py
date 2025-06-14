#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Apple 整修品 Line Bot 服務
支援 Quick Reply 和 Flex Message 功能
"""

import os
import json
from flask import Flask, request, abort
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

app = Flask(__name__)

# Line Bot 設定
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')

if not LINE_CHANNEL_ACCESS_TOKEN or not LINE_CHANNEL_SECRET:
    print("❌ 請設定 LINE_CHANNEL_ACCESS_TOKEN 和 LINE_CHANNEL_SECRET 環境變數")
    exit(1)

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# 初始化查詢系統
query_system = AppleRefurbishedQuery()

class LineBotService:
    def __init__(self):
        self.categories_map = {
            'mac': 'Mac',
            'ipad': 'iPad',
            'airpods': 'AirPods',
            'homepod': 'HomePod',
            'accessories': '配件',
            'iphone': 'iPhone',
            'appletv': 'Apple TV'
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
    user_message = event.message.text.lower()
    reply_messages = []
    
    # 歡迎訊息
    if any(keyword in user_message for keyword in ['hi', 'hello', '你好', '嗨', '開始']):
        reply_messages.append(
            TextSendMessage(
                text="🍎 歡迎使用 Apple 整修品查詢服務！\n\n請選擇您想查詢的產品類別：",
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
                text="請選擇查詢方式：",
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
                text="抱歉，我不太理解您的需求 😅\n\n請選擇以下選項或輸入「幫助」查看使用說明：",
                quick_reply=bot_service.create_category_quick_reply()
            )
        )
    
    # 發送回應
    if reply_messages:
        line_bot_api.reply_message(event.reply_token, reply_messages)

@handler.add(PostbackEvent)
def handle_postback(event):
    """處理 Postback 事件"""
    postback_data = event.postback.data
    
    # 根據 postback 資料處理不同動作
    if postback_data.startswith('category_'):
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