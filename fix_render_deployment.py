#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Render 部署修復腳本
解決 Python 3.13 相容性問題和套件衝突
"""

import os
import shutil
from datetime import datetime

def backup_file(filename):
    """備份檔案"""
    if os.path.exists(filename):
        backup_name = f"{filename}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(filename, backup_name)
        print(f"✅ 備份 {filename} 到 {backup_name}")
        return backup_name
    return None

def create_render_requirements():
    """建立 Render 專用的 requirements.txt"""
    render_requirements = """# Render 部署專用 - 穩定版本套件
# 避免 Python 3.13 相容性問題

# 核心 Web 框架
flask==2.2.5
requests==2.28.2
gunicorn==20.1.0
python-dotenv==0.21.1

# 基本工具
schedule==1.2.0

# Line Bot 功能
line-bot-sdk==2.4.2

# Firebase 功能
firebase-admin==5.4.0

# 爬蟲功能 - 穩定版本
beautifulsoup4==4.12.2
lxml==4.9.3

# 日期處理
python-dateutil==2.8.2

# 修復相容性問題
greenlet==2.0.2

# 如果需要 aiohttp，使用穩定版本
aiohttp==3.8.6
"""
    
    # 備份原始檔案
    backup_file("requirements.txt")
    
    # 寫入新的 requirements.txt
    with open("requirements.txt", "w", encoding="utf-8") as f:
        f.write(render_requirements)
    
    print("✅ 建立 Render 專用 requirements.txt")

def create_render_runtime():
    """建立 Render 專用的 runtime.txt"""
    runtime_content = "python-3.11.7\n"
    
    # 備份原始檔案
    backup_file("runtime.txt")
    
    # 寫入新的 runtime.txt
    with open("runtime.txt", "w", encoding="utf-8") as f:
        f.write(runtime_content)
    
    print("✅ 設定 Python 版本為 3.11.7")

def create_render_build_script():
    """建立 Render 建置腳本"""
    build_script = """#!/bin/bash
# Render 建置腳本

echo "🚀 開始 Render 建置..."

# 更新 pip
pip install --upgrade pip

# 安裝套件
pip install -r requirements.txt

echo "✅ 建置完成！"
"""
    
    with open("build.sh", "w", encoding="utf-8") as f:
        f.write(build_script)
    
    # 設定執行權限
    os.chmod("build.sh", 0o755)
    
    print("✅ 建立 Render 建置腳本")

def create_render_start_script():
    """建立 Render 啟動腳本"""
    start_script = """#!/bin/bash
# Render 啟動腳本

echo "🚀 啟動 Apple 爬蟲服務..."

# 設定環境變數
export PYTHONPATH="${PYTHONPATH}:."

# 啟動服務
exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 120 app:app
"""
    
    with open("start.sh", "w", encoding="utf-8") as f:
        f.write(start_script)
    
    # 設定執行權限
    os.chmod("start.sh", 0o755)
    
    print("✅ 建立 Render 啟動腳本")

def main():
    """主函數"""
    print("🔧 Render 部署修復工具")
    print("=" * 50)
    
    try:
        # 1. 建立 Render 專用 requirements.txt
        create_render_requirements()
        
        # 2. 設定 Python 版本
        create_render_runtime()
        
        # 3. 建立建置腳本
        create_render_build_script()
        
        # 4. 建立啟動腳本
        create_render_start_script()
        
        print("\n🎉 Render 部署修復完成！")
        print("\n📋 接下來的步驟：")
        print("1. 提交這些變更到 GitHub")
        print("2. 在 Render 上重新部署")
        print("3. 檢查部署日誌確認成功")
        
        print("\n💡 Render 設定建議：")
        print("- Build Command: ./build.sh")
        print("- Start Command: ./start.sh")
        print("- Python Version: 3.11.7")
        
    except Exception as e:
        print(f"❌ 修復過程中發生錯誤: {e}")

if __name__ == "__main__":
    main() 