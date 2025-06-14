# 🚀 Render 部署指南

## 📋 Render 設定參數

### 基本設定
- **Language**: `Python 3`
- **Branch**: `main`
- **Region**: `Singapore (Southeast Asia)` ✅
- **Root Directory**: 留空（使用根目錄）

### 建置與啟動命令
```bash
# Build Command
pip install -r requirements.txt

# Start Command (選擇其中一種)
python start_render.py
# 或使用 gunicorn (推薦生產環境)
gunicorn --bind 0.0.0.0:$PORT start_render:app
```

## 🔧 環境變數設定

在 Render 的 Environment Variables 中設定以下變數：

### 必要環境變數
```env
# Line Bot 設定
LINE_CHANNEL_ACCESS_TOKEN=你的Line Bot Token
LINE_CHANNEL_SECRET=你的Line Bot Secret
LINE_WEBHOOK_URL=https://apple-scraper-1ntk.onrender.com/webhook

# OpenAI 設定
OPENAI_API_KEY=你的OpenAI API Key
OPENAI_MODEL=gpt-3.5-turbo

# Firebase 設定
FIREBASE_PROJECT_ID=你的Firebase專案ID
GOOGLE_APPLICATION_CREDENTIALS=firebase-service-account.json

# Render 設定
RENDER_APP_URL=https://apple-scraper-1ntk.onrender.com
ENABLE_SCRAPING=true
SCRAPE_INTERVAL_MINUTES=5

# 其他設定
TZ=Asia/Taipei
LOG_LEVEL=INFO
```

### Firebase 服務帳戶金鑰設定
由於 Render 不支援檔案上傳，需要將 Firebase 金鑰轉為環境變數：

1. 將 `firebase-service-account.json` 內容複製
2. 在 Render 環境變數中新增：
   ```env
   FIREBASE_SERVICE_ACCOUNT_JSON={"type":"service_account","project_id":"..."}
   ```

## 📁 檔案結構檢查

確保以下檔案存在：
```
├── requirements.txt          # Python 套件清單
├── start_render.py          # Render 啟動檔案
├── linebot_service.py       # Line Bot 服務
├── render_keepalive.py      # 防休眠服務
├── apple_scraper_with_firebase.py  # 爬蟲程式
├── config_loader.py         # 設定載入器
└── data/                    # 資料目錄
    ├── apple_refurbished_mac.json
    ├── apple_refurbished_ipad.json
    └── ...
```

## 🔄 部署流程

### 1. 準備階段
```bash
# 確保所有檔案已提交到 GitHub
git add .
git commit -m "準備 Render 部署"
git push
```

### 2. Render 設定
1. 登入 [Render](https://render.com)
2. 點擊 "New" → "Web Service"
3. 連接你的 GitHub 倉庫
4. 填入上述設定參數
5. 設定環境變數

### 3. 部署後檢查
- 檢查部署日誌是否有錯誤
- 訪問 `https://apple-scraper-1ntk.onrender.com` 確認服務運行
- 訪問 `https://apple-scraper-1ntk.onrender.com/health` 檢查健康狀態

## 🐛 常見問題

### 1. 部署失敗
```bash
# 檢查 requirements.txt 是否包含所有套件
pip install -r requirements.txt

# 本地測試啟動檔案
python start_render.py
```

### 2. 環境變數問題
- 確保所有必要的環境變數都已設定
- 檢查 Firebase 金鑰格式是否正確
- 使用 `python config_loader.py` 本地測試

### 3. Line Bot Webhook 設定
1. 部署成功後，複製 Render 提供的 URL
2. 在 Line Developers Console 設定 Webhook URL：
   ```
   https://apple-scraper-1ntk.onrender.com/webhook
   ```

### 4. 服務休眠問題
- Render 免費版會在 15 分鐘無活動後休眠
- `render_keepalive.py` 會每 5 分鐘自動 ping 防止休眠
- 也可以使用外部監控服務（如 UptimeRobot）

## 📊 監控與維護

### 健康檢查端點
- `GET /` - 基本狀態
- `GET /health` - 詳細健康狀態
- `GET /scraper/status` - 爬蟲狀態

### 日誌監控
在 Render 控制台查看即時日誌：
- 部署日誌
- 應用程式日誌
- 錯誤日誌

## 🔒 安全注意事項

1. **不要在程式碼中硬編碼 API 金鑰**
2. **使用環境變數管理敏感資訊**
3. **定期更新套件版本**
4. **監控 API 使用量避免超額**

## 🎯 效能優化

1. **使用 gunicorn 作為 WSGI 伺服器**
2. **設定適當的 worker 數量**
3. **啟用 gzip 壓縮**
4. **使用 CDN 加速靜態資源**

---

📞 **需要幫助？**
- 查看 Render 官方文檔
- 檢查 GitHub Issues
- 聯繫技術支援 