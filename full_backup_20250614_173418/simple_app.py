#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
超級簡化的 Flask 應用 - 避免所有相容性問題
"""

import os
import json
from datetime import datetime
from flask import Flask, jsonify, request

app = Flask(__name__)

# 載入產品資料
def load_product_data():
    """載入產品資料"""
    data = {}
    data_dir = 'data'
    
    if os.path.exists(data_dir):
        for filename in os.listdir(data_dir):
            if filename.endswith('.json'):
                try:
                    with open(os.path.join(data_dir, filename), 'r', encoding='utf-8') as f:
                        category = filename.replace('apple_refurbished_', '').replace('.json', '')
                        data[category] = json.load(f)
                except Exception as e:
                    print(f"載入 {filename} 失敗: {e}")
    
    return data

# 全域變數
PRODUCT_DATA = load_product_data()

@app.route('/')
def home():
    """首頁"""
    return jsonify({
        "status": "running",
        "service": "Apple 整修品爬蟲系統",
        "message": "服務運行正常",
        "timestamp": datetime.now().isoformat(),
        "categories": list(PRODUCT_DATA.keys()),
        "total_products": sum(len(products) for products in PRODUCT_DATA.values())
    })

@app.route('/health')
def health():
    """健康檢查"""
    return jsonify({
        "status": "healthy",
        "service": "apple_scraper",
        "timestamp": datetime.now().isoformat(),
        "data_loaded": len(PRODUCT_DATA) > 0,
        "categories": len(PRODUCT_DATA),
        "environment": {
            "python_version": os.sys.version,
            "flask_running": True
        }
    })

@app.route('/products')
def get_products():
    """取得所有產品"""
    return jsonify({
        "status": "success",
        "data": PRODUCT_DATA,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/products/<category>')
def get_category_products(category):
    """取得特定類別產品"""
    if category in PRODUCT_DATA:
        return jsonify({
            "status": "success",
            "category": category,
            "products": PRODUCT_DATA[category],
            "count": len(PRODUCT_DATA[category]),
            "timestamp": datetime.now().isoformat()
        })
    else:
        return jsonify({
            "status": "error",
            "message": f"類別 '{category}' 不存在",
            "available_categories": list(PRODUCT_DATA.keys())
        }), 404

@app.route('/webhook', methods=['POST'])
def webhook():
    """Line Bot Webhook (簡化版)"""
    return jsonify({
        "status": "received",
        "message": "Webhook 已接收，但 Line Bot 功能暫時停用",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/status')
def status():
    """系統狀態"""
    return jsonify({
        "service": "Apple 整修品爬蟲系統",
        "status": "online",
        "features": {
            "data_api": True,
            "health_check": True,
            "webhook": True,
            "line_bot": False,
            "firebase": False,
            "scraper": False
        },
        "data_summary": {
            category: len(products) 
            for category, products in PRODUCT_DATA.items()
        },
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    # 取得 PORT 環境變數
    port = int(os.environ.get('PORT', 5000))
    
    print("🚀 啟動 Apple 整修品爬蟲系統")
    print(f"📊 已載入 {len(PRODUCT_DATA)} 個產品類別")
    print(f"🌐 服務將在 Port {port} 啟動")
    
    # 啟動 Flask 應用
    app.run(host='0.0.0.0', port=port, debug=False) 