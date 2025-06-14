#!/bin/bash
# Render 建置腳本 - Python 3.8 穩定版

echo "🚀 開始 Render 建置..."

# 檢查 Python 版本
echo "🐍 Python 版本: $(python --version)"

# 更新 pip
pip install --upgrade pip

# 安裝套件
echo "📦 安裝套件..."
pip install -r requirements.txt

echo "✅ 建置完成！"
