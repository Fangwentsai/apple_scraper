#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
環境變數設定助手 - 幫助快速建立 .env 檔案
"""

import os
import sys

def create_env_file():
    """建立 .env 檔案"""
    print("🔧 Apple 整修品爬蟲系統 - 環境變數設定助手")
    print("=" * 60)
    
    # 檢查是否已存在 .env 檔案
    if os.path.exists('.env'):
        response = input("⚠️ .env 檔案已存在，是否覆蓋？(y/N): ").strip().lower()
        if response != 'y':
            print("❌ 取消設定")
            return
    
    print("\n📝 請填入以下資訊（可以先跳過，之後再編輯 .env 檔案）")
    print("💡 提示：直接按 Enter 可跳過該項目\n")
    
    # 收集用戶輸入
    env_vars = {}
    
    # Line Bot 設定
    print("🤖 Line Bot 設定:")
    env_vars['LINE_CHANNEL_ACCESS_TOKEN'] = input("  Line Bot Channel Access Token: ").strip()
    env_vars['LINE_CHANNEL_SECRET'] = input("  Line Bot Channel Secret: ").strip()
    env_vars['LINE_WEBHOOK_URL'] = input("  Webhook URL (例如: https://your-app.onrender.com/webhook): ").strip()
    
    # OpenAI 設定
    print("\n🧠 OpenAI/ChatGPT 設定:")
    env_vars['OPENAI_API_KEY'] = input("  OpenAI API Key: ").strip()
    model = input("  模型 (預設: gpt-3.5-turbo): ").strip()
    env_vars['OPENAI_MODEL'] = model if model else 'gpt-3.5-turbo'
    
    # Firebase 設定
    print("\n🔥 Firebase 設定:")
    firebase_path = input("  Firebase 服務帳戶金鑰檔案路徑 (預設: firebase-service-account.json): ").strip()
    env_vars['GOOGLE_APPLICATION_CREDENTIALS'] = firebase_path if firebase_path else 'firebase-service-account.json'
    env_vars['FIREBASE_PROJECT_ID'] = input("  Firebase 專案 ID: ").strip()
    
    # Render 設定
    print("\n🚀 Render 部署設定:")
    app_url = input("  Render App URL (例如: https://your-app.onrender.com): ").strip()
    env_vars['RENDER_APP_URL'] = app_url if app_url else 'http://localhost:5000'
    
    enable_scraping = input("  啟用自動爬取？(Y/n): ").strip().lower()
    env_vars['ENABLE_SCRAPING'] = 'false' if enable_scraping == 'n' else 'true'
    
    interval = input("  爬取間隔（分鐘，預設: 5）: ").strip()
    env_vars['SCRAPE_INTERVAL_MINUTES'] = interval if interval else '5'
    
    # 建立 .env 檔案內容
    env_content = """# =============================================================================
# Apple 整修品爬蟲系統 - 環境變數設定檔
# =============================================================================
# 由 setup_env.py 自動產生
# 注意：不要將此檔案提交到 Git！

# =============================================================================
# Line Bot 設定
# =============================================================================
LINE_CHANNEL_ACCESS_TOKEN={LINE_CHANNEL_ACCESS_TOKEN}
LINE_CHANNEL_SECRET={LINE_CHANNEL_SECRET}
LINE_WEBHOOK_URL={LINE_WEBHOOK_URL}

# =============================================================================
# OpenAI/ChatGPT 設定
# =============================================================================
OPENAI_API_KEY={OPENAI_API_KEY}
OPENAI_MODEL={OPENAI_MODEL}
OPENAI_MAX_TOKENS=1000
OPENAI_TEMPERATURE=0.7

# =============================================================================
# Firebase 設定
# =============================================================================
GOOGLE_APPLICATION_CREDENTIALS={GOOGLE_APPLICATION_CREDENTIALS}
FIREBASE_PROJECT_ID={FIREBASE_PROJECT_ID}

# =============================================================================
# Render 部署設定
# =============================================================================
RENDER_APP_URL={RENDER_APP_URL}
ENABLE_SCRAPING={ENABLE_SCRAPING}
SCRAPE_INTERVAL_MINUTES={SCRAPE_INTERVAL_MINUTES}

# =============================================================================
# 爬蟲進階設定
# =============================================================================
USER_AGENT=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36
DELAY_BETWEEN_REQUESTS=3
MAX_RETRIES=3

# =============================================================================
# 其他設定
# =============================================================================
TZ=Asia/Taipei
LOG_LEVEL=INFO
VERBOSE_LOGGING=false
""".format(**env_vars)
    
    # 寫入 .env 檔案
    try:
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        print("\n✅ .env 檔案建立成功！")
        print("\n📋 設定摘要:")
        print(f"  Line Bot: {'✅ 已設定' if env_vars['LINE_CHANNEL_ACCESS_TOKEN'] else '❌ 未設定'}")
        print(f"  OpenAI: {'✅ 已設定' if env_vars['OPENAI_API_KEY'] else '❌ 未設定'}")
        print(f"  Firebase: {'✅ 已設定' if env_vars['FIREBASE_PROJECT_ID'] else '❌ 未設定'}")
        print(f"  Render URL: {env_vars['RENDER_APP_URL']}")
        print(f"  自動爬取: {env_vars['ENABLE_SCRAPING']}")
        
        print("\n💡 後續步驟:")
        print("1. 編輯 .env 檔案補充遺漏的 API 金鑰")
        print("2. 確保 Firebase 服務帳戶金鑰檔案存在")
        print("3. 執行 python config_loader.py 測試設定")
        print("4. 執行 python apple_scraper_with_firebase.py 測試爬蟲")
        
    except Exception as e:
        print(f"❌ 建立 .env 檔案失敗: {e}")

def show_example():
    """顯示範例 .env 檔案"""
    print("📄 範例 .env 檔案內容:")
    print("=" * 60)
    
    example_content = """# Line Bot 設定
LINE_CHANNEL_ACCESS_TOKEN=你的Line Bot Token
LINE_CHANNEL_SECRET=你的Line Bot Secret
LINE_WEBHOOK_URL=https://your-app.onrender.com/webhook

# OpenAI 設定
OPENAI_API_KEY=sk-proj-你的OpenAI API Key
OPENAI_MODEL=gpt-3.5-turbo

# Firebase 設定
GOOGLE_APPLICATION_CREDENTIALS=firebase-service-account.json
FIREBASE_PROJECT_ID=your-firebase-project-id

# Render 設定
RENDER_APP_URL=https://your-app.onrender.com
ENABLE_SCRAPING=true
SCRAPE_INTERVAL_MINUTES=5"""
    
    print(example_content)
    print("\n💡 複製上述內容到 .env 檔案並填入你的實際值")

def main():
    """主程式"""
    if len(sys.argv) > 1 and sys.argv[1] == 'example':
        show_example()
        return
    
    try:
        create_env_file()
    except KeyboardInterrupt:
        print("\n\n👋 設定已取消")
    except Exception as e:
        print(f"\n❌ 發生錯誤: {e}")

if __name__ == "__main__":
    main() 