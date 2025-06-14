#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Render 部署問題快速修復腳本
"""

import os
import shutil

def fix_requirements():
    """修復 requirements.txt"""
    print("🔧 修復 requirements.txt...")
    
    # 備份原檔案
    if os.path.exists('requirements.txt'):
        shutil.copy('requirements.txt', 'requirements.txt.backup')
        print("📋 已備份原 requirements.txt")
    
    # 使用最小化版本
    if os.path.exists('requirements-minimal.txt'):
        shutil.copy('requirements-minimal.txt', 'requirements.txt')
        print("✅ 已使用最小化 requirements.txt")
    else:
        # 建立基本版本
        basic_requirements = """flask==2.3.3
requests==2.31.0
gunicorn==20.1.0
python-dotenv==1.0.0
line-bot-sdk==3.5.0
schedule==1.2.0"""
        
        with open('requirements.txt', 'w') as f:
            f.write(basic_requirements)
        print("✅ 已建立基本 requirements.txt")

def check_files():
    """檢查必要檔案"""
    print("\n📁 檢查必要檔案...")
    
    required_files = [
        'runtime.txt',
        'start_render.py',
        'requirements.txt'
    ]
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - 缺少")
    
    # 檢查資料目錄
    if os.path.exists('data'):
        json_files = [f for f in os.listdir('data') if f.endswith('.json')]
        print(f"📊 資料檔案: {len(json_files)} 個")
    else:
        print("❌ data 目錄不存在")

def show_render_settings():
    """顯示 Render 設定建議"""
    print("\n🚀 Render 設定建議:")
    print("=" * 50)
    print("Language: Python 3")
    print("Branch: main")
    print("Region: Singapore (Southeast Asia)")
    print("Root Directory: (留空)")
    print()
    print("Build Command:")
    print("pip install -r requirements.txt")
    print()
    print("Start Command:")
    print("python start_render.py")
    print()
    print("Environment Variables:")
    print("TZ=Asia/Taipei")
    print("LOG_LEVEL=INFO")
    print("ENABLE_SCRAPING=true")
    print("(其他 API 金鑰請手動設定)")

def main():
    """主程式"""
    print("🛠️ Render 部署問題快速修復")
    print("=" * 40)
    
    try:
        fix_requirements()
        check_files()
        show_render_settings()
        
        print("\n✅ 修復完成！")
        print("\n📝 後續步驟:")
        print("1. git add .")
        print("2. git commit -m '修復 Render 部署問題'")
        print("3. git push")
        print("4. 在 Render 重新部署")
        
    except Exception as e:
        print(f"❌ 修復失敗: {e}")

if __name__ == "__main__":
    main() 