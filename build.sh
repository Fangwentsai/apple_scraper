#!/bin/bash
# Render 建置腳本

echo "🚀 開始 Render 建置..."

# 更新 pip
pip install --upgrade pip

# 安裝套件
pip install -r requirements.txt

echo "✅ 建置完成！"
