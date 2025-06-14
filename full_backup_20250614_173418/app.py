#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Render 部署專用 - 超級簡化版本
完全避免套件相容性問題
"""

import os
import sys
import json
from datetime import datetime

# 只使用 Python 標準庫和最基本的套件
try:
    from flask import Flask, jsonify, request
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    print("⚠️  Flask 未安裝，使用基本 HTTP 伺服器")

# 建立 Flask 應用
if FLASK_AVAILABLE:
    app = Flask(__name__)
else:
    # 如果 Flask 不可用，建立一個假的 app 物件
    class FakeApp:
        def route(self, *args, **kwargs):
            def decorator(f):
                return f
            return decorator
        
        def run(self, **kwargs):
            print("❌ Flask 不可用，無法啟動服務")
    
    app = FakeApp()

def load_simple_data():
    """載入簡單的產品資料"""
    try:
        data_dir = 'data'
        if os.path.exists(data_dir):
            for filename in os.listdir(data_dir):
                if filename.endswith('.json'):
                    with open(os.path.join(data_dir, filename), 'r', encoding='utf-8') as f:
                        return json.load(f)
    except Exception as e:
        print(f"載入資料失敗: {e}")
    
    # 回傳假資料
    return {
        "mac": [
            {
                "title": "Mac mini Apple M2 晶片配備 8 核心 CPU 與 10 核心 GPU (整修品)",
                "price": "NT$17,900",
                "original_price": "NT$19,900",
                "savings": "NT$2,000",
                "url": "https://www.apple.com/tw/shop/product/MMFJ3TA/A"
            }
        ]
    }

# 載入資料
PRODUCT_DATA = load_simple_data()

@app.route('/')
def home():
    """首頁 - 基本資訊"""
    if not FLASK_AVAILABLE:
        return "Flask 不可用"
    
    return jsonify({
        "status": "running",
        "service": "Apple 整修品爬蟲系統 (簡化版)",
        "message": "服務運行正常",
        "timestamp": datetime.now().isoformat(),
        "python_version": sys.version,
        "features": {
            "basic_api": True,
            "line_bot": False,
            "firebase": False,
            "advanced_scraping": False
        }
    })

@app.route('/health')
def health():
    """健康檢查"""
    if not FLASK_AVAILABLE:
        return "健康檢查失敗 - Flask 不可用"
    
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "system": {
            "python_version": sys.version,
            "platform": sys.platform,
            "flask_available": FLASK_AVAILABLE
        }
    })

@app.route('/products')
def products():
    """產品列表"""
    if not FLASK_AVAILABLE:
        return "產品 API 不可用"
    
    return jsonify({
        "status": "success",
        "data": PRODUCT_DATA,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/webhook', methods=['POST'])
def webhook():
    """簡化的 Webhook"""
    if not FLASK_AVAILABLE:
        return "Webhook 不可用"
    
    return jsonify({
        "status": "received",
        "message": "Webhook 已接收 (簡化版)",
        "timestamp": datetime.now().isoformat()
    })

def main():
    """主函數"""
    print("🚀 啟動 Apple 整修品爬蟲系統 (簡化版)")
    print(f"🐍 Python 版本: {sys.version}")
    print(f"📦 Flask 可用: {FLASK_AVAILABLE}")
    
    if not FLASK_AVAILABLE:
        print("❌ Flask 不可用，請檢查安裝")
        return
    
    # 取得 PORT 環境變數
    port = int(os.environ.get('PORT', 5000))
    
    print(f"🌐 服務將在 Port {port} 啟動")
    
    try:
        # 啟動 Flask 應用
        app.run(host='0.0.0.0', port=port, debug=False)
    except Exception as e:
        print(f"❌ 啟動失敗: {e}")

if __name__ == '__main__':
    main() 