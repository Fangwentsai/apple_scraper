#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
從頭開始重置腳本
完全重新設計 Render 部署
"""

import os
import shutil
from datetime import datetime

def backup_everything():
    """備份所有重要檔案"""
    backup_dir = f"full_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(backup_dir, exist_ok=True)
    
    important_files = [
        'requirements.txt', 'runtime.txt', 'build.sh', 'start.sh',
        'app.py', 'simple_app.py', 'linebot_service.py'
    ]
    
    for file in important_files:
        if os.path.exists(file):
            shutil.copy2(file, backup_dir)
    
    print(f"✅ 完整備份到 {backup_dir}")
    return backup_dir

def create_minimal_setup():
    """建立最小化設定"""
    
    # 1. 超級簡單的 runtime.txt
    with open('runtime.txt', 'w') as f:
        f.write('python-3.8.18\n')
    
    # 2. 超級簡單的 requirements.txt
    with open('requirements.txt', 'w') as f:
        f.write('flask==2.2.5\ngunicorn==20.1.0\n')
    
    # 3. 超級簡單的 app.py
    app_content = '''#!/usr/bin/env python3
from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        "status": "running",
        "message": "Hello from Render!",
        "service": "Apple Scraper (Minimal)"
    })

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
    
    with open('app.py', 'w') as f:
        f.write(app_content)
    
    # 4. 超級簡單的建置腳本
    with open('build.sh', 'w') as f:
        f.write('#!/bin/bash\necho "Building..."\npip install flask gunicorn\necho "Done!"\n')
    
    # 5. 超級簡單的啟動腳本
    with open('start.sh', 'w') as f:
        f.write('#!/bin/bash\necho "Starting..."\nexec gunicorn --bind 0.0.0.0:$PORT app:app\n')
    
    # 設定執行權限
    os.chmod('build.sh', 0o755)
    os.chmod('start.sh', 0o755)
    
    print("✅ 最小化設定已建立")

def create_render_yaml():
    """建立 render.yaml 設定檔"""
    render_config = '''services:
  - type: web
    name: apple-scraper
    env: python
    buildCommand: pip install flask gunicorn
    startCommand: gunicorn --bind 0.0.0.0:$PORT app:app
    envVars:
      - key: PYTHON_VERSION
        value: 3.8.18
'''
    
    with open('render.yaml', 'w') as f:
        f.write(render_config)
    
    print("✅ render.yaml 已建立")

def main():
    """主函數"""
    print("🔄 從頭開始重置 Render 部署")
    print("=" * 50)
    
    # 備份
    backup_dir = backup_everything()
    
    print("\n選擇重置方案：")
    print("1. 最小化設定（只有 Flask + Gunicorn）")
    print("2. 建立 render.yaml 設定檔")
    print("3. 完全重置（選項 1 + 2）")
    print("4. 取消")
    
    choice = input("\n請選擇 (1-4): ").strip()
    
    if choice == "1":
        create_minimal_setup()
        
    elif choice == "2":
        create_render_yaml()
        
    elif choice == "3":
        create_minimal_setup()
        create_render_yaml()
        
    elif choice == "4":
        print("❌ 已取消")
        return
        
    else:
        print("❌ 無效選擇")
        return
    
    print(f"\n📁 備份位置: {backup_dir}")
    print("\n🎯 Render 設定建議：")
    print("- Build Command: ./build.sh 或 pip install flask gunicorn")
    print("- Start Command: ./start.sh 或 gunicorn --bind 0.0.0.0:$PORT app:app")
    print("- Python Version: 3.8.18")
    
    print("\n🚀 接下來的步驟：")
    print("1. git add .")
    print("2. git commit -m '🔄 完全重置 - 最小化設定'")
    print("3. git push")
    print("4. 在 Render 重新部署")
    
    print("\n💡 如果還是失敗，問題就是 Render 本身了！")

if __name__ == "__main__":
    main() 