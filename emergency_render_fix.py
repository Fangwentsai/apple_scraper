#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
緊急 Render 修復腳本
提供多個 Python 版本和套件組合選項
"""

import os
import shutil
from datetime import datetime

def backup_files():
    """備份重要檔案"""
    files_to_backup = ['requirements.txt', 'runtime.txt']
    backup_dir = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(backup_dir, exist_ok=True)
    
    for file in files_to_backup:
        if os.path.exists(file):
            shutil.copy2(file, os.path.join(backup_dir, file))
    
    print(f"✅ 檔案已備份到 {backup_dir}")
    return backup_dir

def create_python39_setup():
    """建立 Python 3.9 設定"""
    runtime_content = "python-3.9.18\n"
    
    requirements_content = """# Python 3.9 超穩定版本
flask==2.2.5
requests==2.28.2
gunicorn==20.1.0
python-dotenv==0.21.1
schedule==1.2.0
line-bot-sdk==2.4.2
firebase-admin==5.4.0
beautifulsoup4==4.12.2
lxml==4.9.1
python-dateutil==2.8.2
greenlet==1.1.2
"""
    
    with open('runtime.txt', 'w') as f:
        f.write(runtime_content)
    
    with open('requirements.txt', 'w') as f:
        f.write(requirements_content)
    
    print("✅ Python 3.9 設定已建立")

def create_python38_setup():
    """建立 Python 3.8 設定（最穩定）"""
    runtime_content = "python-3.8.18\n"
    
    requirements_content = """# Python 3.8 最穩定版本
flask==2.2.5
requests==2.28.2
gunicorn==20.1.0
python-dotenv==0.21.1
schedule==1.2.0
line-bot-sdk==2.4.2
firebase-admin==5.4.0
beautifulsoup4==4.12.2
lxml==4.8.0
python-dateutil==2.8.2
greenlet==1.1.0
"""
    
    with open('runtime.txt', 'w') as f:
        f.write(runtime_content)
    
    with open('requirements.txt', 'w') as f:
        f.write(requirements_content)
    
    print("✅ Python 3.8 設定已建立")

def create_minimal_setup():
    """建立最小化設定（無 Line Bot）"""
    runtime_content = "python-3.9.18\n"
    
    requirements_content = """# 最小化版本 - 純 Python 套件
flask==2.2.5
requests==2.28.2
gunicorn==20.1.0
python-dotenv==0.21.1
schedule==1.2.0
firebase-admin==5.4.0
beautifulsoup4==4.12.2
python-dateutil==2.8.2
"""
    
    with open('runtime.txt', 'w') as f:
        f.write(runtime_content)
    
    with open('requirements.txt', 'w') as f:
        f.write(requirements_content)
    
    print("✅ 最小化設定已建立（暫時移除 Line Bot 功能）")

def main():
    """主函數"""
    print("🚨 Render 緊急修復工具")
    print("=" * 50)
    
    # 備份檔案
    backup_dir = backup_files()
    
    print("\n選擇修復方案：")
    print("1. Python 3.9 + 穩定套件版本")
    print("2. Python 3.8 + 最穩定套件版本")
    print("3. 最小化版本（暫時移除 Line Bot）")
    print("4. 恢復備份")
    
    choice = input("\n請選擇 (1-4): ").strip()
    
    if choice == "1":
        create_python39_setup()
        print("\n🎯 建議的 Render 設定：")
        print("- Python Version: 3.9.18")
        print("- Build Command: pip install -r requirements.txt")
        print("- Start Command: gunicorn --bind 0.0.0.0:$PORT app:app")
        
    elif choice == "2":
        create_python38_setup()
        print("\n🎯 建議的 Render 設定：")
        print("- Python Version: 3.8.18")
        print("- Build Command: pip install -r requirements.txt")
        print("- Start Command: gunicorn --bind 0.0.0.0:$PORT app:app")
        
    elif choice == "3":
        create_minimal_setup()
        print("\n⚠️  注意：Line Bot 功能已暫時移除")
        print("🎯 建議的 Render 設定：")
        print("- Python Version: 3.9.18")
        print("- Build Command: pip install -r requirements.txt")
        print("- Start Command: gunicorn --bind 0.0.0.0:$PORT app:app")
        
    elif choice == "4":
        # 恢復備份
        for file in ['requirements.txt', 'runtime.txt']:
            backup_file = os.path.join(backup_dir, file)
            if os.path.exists(backup_file):
                shutil.copy2(backup_file, file)
        print("✅ 已恢復備份檔案")
        
    else:
        print("❌ 無效選擇")
        return
    
    print(f"\n📁 備份檔案位置: {backup_dir}")
    print("\n🚀 接下來的步驟：")
    print("1. git add .")
    print("2. git commit -m '🔧 緊急修復 Render 部署問題'")
    print("3. git push")
    print("4. 在 Render Dashboard 觸發重新部署")

if __name__ == "__main__":
    main() 