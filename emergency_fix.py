#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
緊急修復腳本 - 切換到完全相容的版本
"""

import os
import shutil

def emergency_fix():
    """緊急修復"""
    print("🚨 執行緊急修復...")
    
    # 1. 備份現有檔案
    if os.path.exists('requirements.txt'):
        shutil.copy('requirements.txt', 'requirements.txt.broken')
        print("📋 已備份有問題的 requirements.txt")
    
    # 2. 使用安全版本
    if os.path.exists('requirements-safe.txt'):
        shutil.copy('requirements-safe.txt', 'requirements.txt')
        print("✅ 已切換到安全版本 requirements.txt")
    
    # 3. 檢查檔案
    files_to_check = [
        'runtime.txt',
        'simple_app.py', 
        'requirements.txt'
    ]
    
    print("\n📁 檢查必要檔案:")
    for file in files_to_check:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - 缺少")
    
    print("\n🔧 Render 設定建議:")
    print("Build Command: pip install -r requirements.txt")
    print("Start Command: python simple_app.py")
    
    print("\n✅ 緊急修復完成！")
    print("現在可以重新部署到 Render")

if __name__ == "__main__":
    emergency_fix() 