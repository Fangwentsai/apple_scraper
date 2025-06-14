#!/bin/bash
# 超級簡化建置腳本

echo "🚀 開始建置..."
echo "🐍 Python 版本: $(python --version)"

# 只安裝最基本的套件
pip install flask==2.2.5 gunicorn==20.1.0

echo "✅ 建置完成！"
