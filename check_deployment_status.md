# Render 部署狀態檢查清單

## 🎯 當前設定（緊急修復版）

### Python 版本
- ✅ **Python 3.8.18** - 最穩定，避免所有相容性問題

### 套件版本
- ✅ **flask==2.2.5** - Web 框架
- ✅ **requests==2.28.2** - HTTP 請求
- ✅ **gunicorn==20.1.0** - WSGI 伺服器
- ✅ **line-bot-sdk==2.4.2** - Line Bot 功能
- ✅ **firebase-admin==5.4.0** - Firebase 整合
- ✅ **beautifulsoup4==4.12.2** - HTML 解析
- ✅ **lxml==4.8.0** - XML/HTML 處理（Python 3.8 相容）
- ✅ **greenlet==1.1.0** - 協程支援（Python 3.8 相容）

### Render 設定檢查清單

#### 1. 環境設定
- [ ] **Build Command**: `./build.sh`
- [ ] **Start Command**: `./start.sh`
- [ ] **Python Version**: 確認使用 3.8.18

#### 2. 環境變數
- [ ] `LINE_CHANNEL_ACCESS_TOKEN`
- [ ] `LINE_CHANNEL_SECRET`
- [ ] `FIREBASE_CREDENTIALS` (JSON 格式)
- [ ] 其他必要環境變數

#### 3. 部署檢查
- [ ] GitHub 連接正常
- [ ] 自動部署已啟用
- [ ] 最新 commit 已推送

## 🚀 部署步驟

### 1. 在 Render Dashboard
1. 進入你的服務設定
2. 更新 Build Command: `./build.sh`
3. 更新 Start Command: `./start.sh`
4. 確認 Python Version 設定
5. 點擊 "Manual Deploy"

### 2. 監控部署日誌
```
🚀 開始 Render 建置...
🐍 Python 版本: Python 3.8.18
📦 安裝套件...
✅ 建置完成！
```

### 3. 檢查服務狀態
- [ ] 建置成功（綠色）
- [ ] 服務運行中
- [ ] 沒有錯誤日誌

## 🔍 故障排除

### 如果還是失敗：

#### 選項 1: 最小化版本
```bash
echo "3" | python3 emergency_render_fix.py
```
暫時移除 Line Bot 功能，只保留核心服務

#### 選項 2: 回滾到備份
```bash
echo "4" | python3 emergency_render_fix.py
```
恢復之前的設定

#### 選項 3: 手動設定
直接在 Render Dashboard 設定：
- Build Command: `pip install flask requests gunicorn python-dotenv schedule firebase-admin beautifulsoup4`
- Start Command: `gunicorn --bind 0.0.0.0:$PORT app:app`

## 📊 預期結果

### 成功指標
- ✅ 建置時間 < 5 分鐘
- ✅ 沒有編譯錯誤
- ✅ 服務正常啟動
- ✅ API 端點可訪問

### 測試 URL
- `https://your-app.onrender.com/` - 基本健康檢查
- `https://your-app.onrender.com/webhook` - Line Bot webhook

## 📞 支援資源

- [Render 官方文件](https://render.com/docs)
- [Python 版本支援](https://render.com/docs/python-version)
- [故障排除指南](./RENDER_DEPLOYMENT_GUIDE.md)

---

**最後更新**: 2024-06-14  
**狀態**: 🚨 緊急修復版本  
**Python 版本**: 3.8.18  
**套件策略**: 最穩定版本組合 