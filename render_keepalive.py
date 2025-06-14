#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Render 防休眠服務
每 5 分鐘自動發送請求防止服務休眠
可選擇性重新爬取 Apple 整修品資料
"""

import os
import time
import requests
import schedule
import threading
from datetime import datetime
import subprocess
import sys
from flask import Flask, jsonify

app = Flask(__name__)

class RenderKeepAlive:
    def __init__(self):
        self.app_url = os.getenv('RENDER_APP_URL', 'http://localhost:5000')
        self.scrape_interval_hours = int(os.getenv('SCRAPE_INTERVAL_HOURS', '6'))  # 預設 6 小時爬取一次
        self.enable_scraping = os.getenv('ENABLE_SCRAPING', 'true').lower() == 'true'
        self.last_scrape_time = None
        self.last_ping_time = None
        self.ping_count = 0
        self.scrape_count = 0
        
        print(f"🚀 Render 防休眠服務啟動")
        print(f"📍 應用程式 URL: {self.app_url}")
        print(f"⏰ 爬取間隔: {self.scrape_interval_hours} 小時")
        print(f"🔄 啟用自動爬取: {self.enable_scraping}")
    
    def ping_service(self):
        """發送 ping 請求防止休眠"""
        try:
            response = requests.get(f"{self.app_url}/health", timeout=30)
            self.last_ping_time = datetime.now()
            self.ping_count += 1
            
            if response.status_code == 200:
                print(f"✅ Ping 成功 #{self.ping_count} - {self.last_ping_time.strftime('%Y-%m-%d %H:%M:%S')}")
                return True
            else:
                print(f"⚠️ Ping 回應異常: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Ping 失敗: {e}")
            return False
    
    def run_scraper(self):
        """執行爬蟲程式並備份到 Firebase"""
        if not self.enable_scraping:
            print("🔒 自動爬取已停用")
            return False
        
        try:
            print("🕷️ 開始執行 Apple 整修品爬蟲 + Firebase 備份...")
            
            # 執行整合的爬蟲+Firebase備份程式
            result = subprocess.run([
                sys.executable, 'apple_scraper_with_firebase.py'
            ], capture_output=True, text=True, timeout=900)  # 15 分鐘超時（包含備份時間）
            
            if result.returncode == 0:
                self.last_scrape_time = datetime.now()
                self.scrape_count += 1
                print(f"✅ 爬蟲+備份執行成功 #{self.scrape_count} - {self.last_scrape_time.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"📊 執行輸出: {result.stdout[-300:]}")  # 顯示最後 300 字元
                
                # 檢查是否有 Firebase 備份成功的訊息
                if "Firebase 備份完成" in result.stdout:
                    print("☁️ Firebase 備份成功")
                elif "Firebase 未設定" in result.stdout:
                    print("⚠️ Firebase 未設定，僅完成本地儲存")
                
                return True
            else:
                print(f"❌ 爬蟲+備份執行失敗: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("⏰ 爬蟲+備份執行超時")
            return False
        except Exception as e:
            print(f"❌ 爬蟲+備份執行錯誤: {e}")
            return False
    
    def should_scrape(self):
        """檢查是否需要執行爬蟲"""
        if not self.enable_scraping:
            return False
        
        if self.last_scrape_time is None:
            return True
        
        time_diff = datetime.now() - self.last_scrape_time
        return time_diff.total_seconds() >= (self.scrape_interval_hours * 3600)
    
    def scheduled_tasks(self):
        """排程任務"""
        print("📅 設定排程任務...")
        
        # 每 5 分鐘執行爬蟲+備份
        if self.enable_scraping:
            schedule.every(5).minutes.do(self.run_scraper)
        else:
            # 如果不啟用爬取，則每 5 分鐘 ping 一次防休眠
            schedule.every(5).minutes.do(self.ping_service)
            
        # 啟動時立即執行一次爬蟲（如果啟用爬取）
        if self.enable_scraping:
            threading.Thread(target=self.run_scraper, daemon=True).start()
        
        print("✅ 排程任務設定完成")
    
    def run_scheduler(self):
        """執行排程器"""
        print("⏰ 排程器開始運行...")
        
        while True:
            try:
                schedule.run_pending()
                time.sleep(30)  # 每 30 秒檢查一次排程
            except KeyboardInterrupt:
                print("\n👋 收到中斷信號，正在停止服務...")
                break
            except Exception as e:
                print(f"❌ 排程器錯誤: {e}")
                time.sleep(60)  # 發生錯誤時等待 1 分鐘再繼續
    
    def get_status(self):
        """取得服務狀態"""
        return {
            "service": "Render KeepAlive",
            "status": "running",
            "app_url": self.app_url,
            "scraping_enabled": self.enable_scraping,
            "scrape_interval_hours": self.scrape_interval_hours,
            "last_ping_time": self.last_ping_time.isoformat() if self.last_ping_time else None,
            "last_scrape_time": self.last_scrape_time.isoformat() if self.last_scrape_time else None,
            "ping_count": self.ping_count,
            "scrape_count": self.scrape_count,
            "next_scrape_due": self.should_scrape()
        }

# 建立 KeepAlive 實例
keepalive = RenderKeepAlive()

@app.route('/')
def home():
    """首頁"""
    status = keepalive.get_status()
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>🍎 Apple 整修品爬蟲 - Render 防休眠服務</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
            .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            h1 {{ color: #1DB446; }}
            .status {{ background: #e8f5e8; padding: 15px; border-radius: 5px; margin: 20px 0; }}
            .info {{ background: #f0f8ff; padding: 15px; border-radius: 5px; margin: 20px 0; }}
            .warning {{ background: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0; }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background-color: #f2f2f2; }}
            .btn {{ display: inline-block; padding: 10px 20px; background: #1DB446; color: white; text-decoration: none; border-radius: 5px; margin: 5px; }}
            .btn:hover {{ background: #17a03a; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🍎 Apple 整修品爬蟲服務</h1>
            
            <div class="status">
                <h3>✅ 服務狀態：正常運行</h3>
                <p>Render 防休眠服務正在運行中，每 5 分鐘自動執行爬蟲並備份到 Firebase。</p>
            </div>
            
            <h3>📊 服務資訊</h3>
            <table>
                <tr><th>項目</th><th>值</th></tr>
                <tr><td>應用程式 URL</td><td>{status['app_url']}</td></tr>
                <tr><td>自動爬取</td><td>{'✅ 啟用' if status['scraping_enabled'] else '❌ 停用'}</td></tr>
                <tr><td>爬取間隔</td><td>{status['scrape_interval_hours']} 小時</td></tr>
                <tr><td>Ping 次數</td><td>{status['ping_count']}</td></tr>
                <tr><td>爬取次數</td><td>{status['scrape_count']}</td></tr>
                <tr><td>最後 Ping 時間</td><td>{status['last_ping_time'] or '尚未執行'}</td></tr>
                <tr><td>最後爬取時間</td><td>{status['last_scrape_time'] or '尚未執行'}</td></tr>
                <tr><td>需要爬取</td><td>{'✅ 是' if status['next_scrape_due'] else '❌ 否'}</td></tr>
            </table>
            
            <div class="info">
                <h3>🔗 相關連結</h3>
                <a href="/status" class="btn">查看詳細狀態</a>
                <a href="/health" class="btn">健康檢查</a>
                <a href="/trigger-scrape" class="btn">手動觸發爬取</a>
            </div>
            
            <div class="warning">
                <h3>⚠️ 注意事項</h3>
                <ul>
                    <li>此服務會每 5 分鐘自動 ping 防止 Render 免費版休眠</li>
                    <li>如果啟用自動爬取，會根據設定間隔重新爬取 Apple 整修品資料</li>
                    <li>可透過環境變數調整爬取間隔和啟用/停用自動爬取</li>
                </ul>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html

@app.route('/status')
def status():
    """狀態 API"""
    return jsonify(keepalive.get_status())

@app.route('/health')
def health():
    """健康檢查"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Apple Refurbished Scraper KeepAlive"
    })

@app.route('/trigger-scrape')
def trigger_scrape():
    """手動觸發爬取"""
    if not keepalive.enable_scraping:
        return jsonify({
            "success": False,
            "message": "自動爬取功能已停用"
        })
    
    # 在背景執行爬蟲
    threading.Thread(target=keepalive.run_scraper, daemon=True).start()
    
    return jsonify({
        "success": True,
        "message": "爬蟲已在背景開始執行",
        "timestamp": datetime.now().isoformat()
    })

def run_flask_app():
    """執行 Flask 應用程式"""
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)

def main():
    """主程式"""
    print("🚀 啟動 Render 防休眠服務...")
    
    # 設定排程任務
    keepalive.scheduled_tasks()
    
    # 在背景執行排程器
    scheduler_thread = threading.Thread(target=keepalive.run_scheduler, daemon=True)
    scheduler_thread.start()
    
    # 執行 Flask 應用程式
    try:
        run_flask_app()
    except KeyboardInterrupt:
        print("\n👋 服務已停止")

if __name__ == "__main__":
    main() 