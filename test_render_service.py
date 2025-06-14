#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試 Render 服務狀態
"""

import requests
import json
from datetime import datetime

RENDER_URL = "https://apple-scraper-1ntk.onrender.com"

def test_endpoint(url, description):
    """測試單一端點"""
    print(f"🔍 測試 {description}...")
    try:
        response = requests.get(url, timeout=30)
        print(f"   狀態碼: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"   回應: {json.dumps(data, ensure_ascii=False, indent=2)}")
            except:
                print(f"   回應: {response.text[:200]}...")
            print("   ✅ 成功")
        else:
            print(f"   ❌ 失敗: {response.text[:100]}")
        
    except requests.exceptions.Timeout:
        print("   ⏰ 請求超時 (可能服務正在啟動)")
    except requests.exceptions.ConnectionError:
        print("   🔌 連線錯誤 (服務可能未運行)")
    except Exception as e:
        print(f"   ❌ 錯誤: {e}")
    
    print()

def main():
    """主測試程式"""
    print("🚀 測試 Render 服務狀態")
    print("=" * 50)
    print(f"服務網址: {RENDER_URL}")
    print(f"測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 測試各個端點
    endpoints = [
        (f"{RENDER_URL}/", "首頁"),
        (f"{RENDER_URL}/health", "健康檢查"),
        (f"{RENDER_URL}/webhook", "Line Bot Webhook (POST)"),
    ]
    
    for url, desc in endpoints:
        test_endpoint(url, desc)
    
    print("📋 測試完成")
    print("\n💡 如果服務未回應:")
    print("1. 檢查 Render 控制台的部署狀態")
    print("2. 查看部署日誌是否有錯誤")
    print("3. 確認環境變數設定正確")
    print("4. 等待服務完全啟動 (首次可能需要幾分鐘)")

if __name__ == "__main__":
    main() 