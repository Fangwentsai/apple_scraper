#!/bin/bash
# Render 啟動腳本

echo "🚀 啟動 Apple 爬蟲服務..."

# 設定環境變數
export PYTHONPATH="${PYTHONPATH}:."

# 啟動服務
exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 120 app:app
