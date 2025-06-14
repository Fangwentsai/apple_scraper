#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
套件相容性測試腳本
驗證所有依賴套件是否可以正常導入
"""

import sys
import importlib

def test_import(module_name, description=""):
    """測試模組導入"""
    try:
        importlib.import_module(module_name)
        print(f"✅ {module_name} - {description}")
        return True
    except ImportError as e:
        print(f"❌ {module_name} - {description}: {e}")
        return False
    except Exception as e:
        print(f"⚠️  {module_name} - {description}: {e}")
        return False

def main():
    """主測試函數"""
    print("🧪 套件相容性測試")
    print("=" * 50)
    
    # 測試核心套件
    tests = [
        ("flask", "Web 框架"),
        ("requests", "HTTP 請求"),
        ("gunicorn", "WSGI 伺服器"),
        ("dotenv", "環境變數"),
        ("schedule", "任務排程"),
        ("linebot", "Line Bot SDK"),
        ("firebase_admin", "Firebase 管理"),
        ("bs4", "BeautifulSoup HTML 解析"),
        ("lxml", "XML/HTML 處理"),
        ("dateutil", "日期處理"),
        ("greenlet", "協程支援"),
    ]
    
    success_count = 0
    total_count = len(tests)
    
    for module_name, description in tests:
        if test_import(module_name, description):
            success_count += 1
    
    print("\n" + "=" * 50)
    print(f"📊 測試結果: {success_count}/{total_count} 成功")
    
    if success_count == total_count:
        print("🎉 所有套件都可以正常導入！")
        return True
    else:
        print("⚠️  有些套件無法導入，請檢查安裝")
        return False

def test_specific_versions():
    """測試特定版本需求"""
    print("\n🔍 版本檢查")
    print("-" * 30)
    
    try:
        import aiohttp
        print(f"✅ aiohttp 版本: {aiohttp.__version__}")
        
        # 檢查是否是預期的版本
        if aiohttp.__version__ == "3.8.4":
            print("✅ aiohttp 版本符合 line-bot-sdk 需求")
        else:
            print(f"⚠️  aiohttp 版本 {aiohttp.__version__} 可能與 line-bot-sdk 不相容")
            
    except ImportError:
        print("❌ aiohttp 未安裝")
    
    try:
        import linebot
        print(f"✅ line-bot-sdk 可用")
    except ImportError:
        print("❌ line-bot-sdk 未安裝")

if __name__ == "__main__":
    print(f"🐍 Python 版本: {sys.version}")
    print()
    
    # 基本導入測試
    basic_success = main()
    
    # 版本檢查
    test_specific_versions()
    
    print("\n" + "=" * 50)
    if basic_success:
        print("✅ 套件相容性測試通過！可以部署到 Render")
        sys.exit(0)
    else:
        print("❌ 套件相容性測試失敗！請修復依賴問題")
        sys.exit(1) 