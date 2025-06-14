#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Render 部署專用啟動檔案
整合 Line Bot、爬蟲、防休眠功能
"""

import os
import sys
import threading
import time
from flask import Flask

# 確保能找到其他模組
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def start_linebot_service():
    """啟動 Line Bot 服務"""
    try:
        from linebot_service import app as linebot_app
        print("🤖 Line Bot 服務已啟動")
        return linebot_app
    except Exception as e:
        print(f"❌ Line Bot 服務啟動失敗: {e}")
        # 建立基本的 Flask 應用作為備用
        app = Flask(__name__)
        
        @app.route('/')
        def home():
            return "Apple 整修品爬蟲系統運行中"
        
        @app.route('/health')
        def health():
            return {"status": "ok", "service": "apple_scraper"}
        
        return app

def start_scraper_scheduler():
    """啟動爬蟲排程器"""
    def run_scheduler():
        try:
            from render_keepalive import RenderKeepAlive
            keepalive = RenderKeepAlive()
            keepalive.start_scheduler()
            print("📅 爬蟲排程器已啟動")
        except Exception as e:
            print(f"❌ 爬蟲排程器啟動失敗: {e}")
    
    # 在背景執行緒中啟動排程器
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()

def main():
    """主程式"""
    print("🚀 Render 服務啟動中...")
    print("=" * 50)
    
    # 啟動爬蟲排程器
    start_scraper_scheduler()
    
    # 啟動 Line Bot 服務
    app = start_linebot_service()
    
    # 取得 PORT 環境變數（Render 會自動設定）
    port = int(os.environ.get('PORT', 5000))
    
    print(f"🌐 服務將在 Port {port} 啟動")
    print("✅ 所有服務已就緒")
    
    # 啟動 Flask 應用
    app.run(host='0.0.0.0', port=port, debug=False)

if __name__ == "__main__":
    main() 