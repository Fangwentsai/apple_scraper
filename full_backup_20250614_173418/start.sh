#!/bin/bash
# 超級簡化啟動腳本

echo "🚀 啟動服務..."

# 直接啟動，不要複雜的設定
exec gunicorn --bind 0.0.0.0:$PORT app:app
