# 環境變數設定指南

## 📋 支援的環境變數

### Line Bot 設定
```bash
export LINE_CHANNEL_ACCESS_TOKEN="你的Line Bot Channel Access Token"
export LINE_CHANNEL_SECRET="你的Line Bot Channel Secret"
export LINE_WEBHOOK_URL="https://your-app.onrender.com/webhook"
```

### OpenAI/ChatGPT 設定
```bash
export OPENAI_API_KEY="你的OpenAI API Key"
export OPENAI_MODEL="gpt-3.5-turbo"  # 可選，預設為 gpt-3.5-turbo
export OPENAI_MAX_TOKENS="1000"      # 可選，預設為 1000
export OPENAI_TEMPERATURE="0.7"      # 可選，預設為 0.7
```

### Firebase 設定
```bash
export GOOGLE_APPLICATION_CREDENTIALS="path/to/firebase-service-account.json"
export FIREBASE_PROJECT_ID="你的Firebase專案ID"
```

### Render 部署設定
```bash
export RENDER_APP_URL="https://your-app.onrender.com"
export ENABLE_SCRAPING="true"         # 啟用自動爬取
export SCRAPE_INTERVAL_MINUTES="5"    # 爬取間隔（分鐘）
```

### 爬蟲設定
```bash
export USER_AGENT="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
export DELAY_BETWEEN_REQUESTS="3"     # 請求間延遲（秒）
export MAX_RETRIES="3"                # 最大重試次數
```

## 🔧 設定方法

### 1. 本地開發環境

#### macOS/Linux
```bash
# 建立 .env 檔案
cat > .env << EOF
LINE_CHANNEL_ACCESS_TOKEN=你的Line Bot Token
LINE_CHANNEL_SECRET=你的Line Bot Secret
OPENAI_API_KEY=你的OpenAI API Key
GOOGLE_APPLICATION_CREDENTIALS=firebase-service-account.json
RENDER_APP_URL=http://localhost:5000
ENABLE_SCRAPING=true
SCRAPE_INTERVAL_MINUTES=5
EOF

# 載入環境變數
source .env
```

#### Windows
```cmd
# 建立 .env 檔案
echo LINE_CHANNEL_ACCESS_TOKEN=你的Line Bot Token > .env
echo LINE_CHANNEL_SECRET=你的Line Bot Secret >> .env
echo OPENAI_API_KEY=你的OpenAI API Key >> .env
echo GOOGLE_APPLICATION_CREDENTIALS=firebase-service-account.json >> .env
echo RENDER_APP_URL=http://localhost:5000 >> .env
echo ENABLE_SCRAPING=true >> .env
echo SCRAPE_INTERVAL_MINUTES=5 >> .env
```

### 2. Render 部署環境

在 Render Dashboard 中設定環境變數：

1. 進入你的 Web Service
2. 點擊 "Environment" 分頁
3. 新增以下環境變數：

```
LINE_CHANNEL_ACCESS_TOKEN = 你的Line Bot Token
LINE_CHANNEL_SECRET = 你的Line Bot Secret
OPENAI_API_KEY = 你的OpenAI API Key
GOOGLE_APPLICATION_CREDENTIALS = firebase-service-account.json
ENABLE_SCRAPING = true
SCRAPE_INTERVAL_MINUTES = 5
```

### 3. Docker 環境

```dockerfile
# Dockerfile 中設定
ENV LINE_CHANNEL_ACCESS_TOKEN=""
ENV LINE_CHANNEL_SECRET=""
ENV OPENAI_API_KEY=""
ENV GOOGLE_APPLICATION_CREDENTIALS="firebase-service-account.json"
ENV ENABLE_SCRAPING="true"
ENV SCRAPE_INTERVAL_MINUTES="5"
```

或使用 docker-compose.yml：

```yaml
version: '3.8'
services:
  apple-scraper:
    build: .
    environment:
      - LINE_CHANNEL_ACCESS_TOKEN=${LINE_CHANNEL_ACCESS_TOKEN}
      - LINE_CHANNEL_SECRET=${LINE_CHANNEL_SECRET}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - GOOGLE_APPLICATION_CREDENTIALS=firebase-service-account.json
      - ENABLE_SCRAPING=true
      - SCRAPE_INTERVAL_MINUTES=5
    volumes:
      - ./firebase-service-account.json:/app/firebase-service-account.json
```

## 🔑 API 金鑰取得方法

### Line Bot
1. 前往 [Line Developers Console](https://developers.line.biz/)
2. 建立 Provider 和 Messaging API Channel
3. 在 Channel 設定中取得：
   - Channel Access Token
   - Channel Secret

### OpenAI API
1. 前往 [OpenAI Platform](https://platform.openai.com/)
2. 註冊並登入帳號
3. 前往 API Keys 頁面
4. 建立新的 API Key

### Firebase
1. 前往 [Firebase Console](https://console.firebase.google.com/)
2. 建立專案並啟用 Firestore
3. 前往專案設定 → 服務帳戶
4. 產生新的私密金鑰並下載 JSON 檔案

## 🛡️ 安全性注意事項

### 1. 保護 API 金鑰
- 絕對不要將 API 金鑰提交到 Git
- 使用 `.gitignore` 排除設定檔案
- 定期更換 API 金鑰

### 2. 環境變數最佳實務
```bash
# 好的做法：使用環境變數
export OPENAI_API_KEY="sk-..."

# 壞的做法：寫死在程式碼中
api_key = "sk-proj-abc123..."  # 不要這樣做！
```

### 3. 權限控制
- Line Bot：設定適當的 Webhook URL
- OpenAI：監控 API 使用量和費用
- Firebase：設定 Firestore 安全規則

## 🔍 除錯和驗證

### 檢查環境變數
```bash
# 檢查特定環境變數
echo $LINE_CHANNEL_ACCESS_TOKEN
echo $OPENAI_API_KEY

# 檢查所有相關環境變數
env | grep -E "(LINE|OPENAI|FIREBASE|RENDER)"
```

### 使用設定載入器測試
```bash
python config_loader.py
```

### 常見問題

#### Q: 環境變數設定後程式仍無法讀取
A: 確認：
1. 環境變數名稱正確
2. 重新啟動終端機或程式
3. 檢查是否有空格或特殊字元

#### Q: Render 部署後 API 無法使用
A: 檢查：
1. Render 環境變數是否正確設定
2. 服務是否重新部署
3. 查看 Render 日誌確認錯誤訊息

#### Q: Firebase 權限錯誤
A: 確認：
1. 服務帳戶金鑰檔案路徑正確
2. 檔案內容完整且格式正確
3. Firebase 專案 ID 正確

## 📝 設定檢查清單

- [ ] Line Bot Token 和 Secret 已設定
- [ ] OpenAI API Key 已設定並有效
- [ ] Firebase 服務帳戶金鑰已下載並設定
- [ ] 環境變數已正確載入
- [ ] 所有敏感檔案已加入 .gitignore
- [ ] Render 環境變數已設定（如需部署）
- [ ] 測試所有 API 連接正常 