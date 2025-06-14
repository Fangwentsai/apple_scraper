# Apple 整修品爬蟲專案 🍎

這是一個專門爬取 Apple 台灣官網整修品資訊的 Python 專案，支援多種查詢方式和 Line Bot 整合。

## 📊 專案概述

本專案可以爬取以下 Apple 整修品類別：
- **Mac 整修品** (84 個產品)
- **iPad 整修品** (8 個產品)
- **AirPods 整修品** (2 個產品)
- **HomePod 整修品** (2 個產品)
- **配件整修品** (4 個產品)
- **iPhone 整修品** (目前無產品)
- **Apple TV 整修品** (目前無產品)

**總計：100 個 Apple 整修品產品**

## 🚀 快速開始

### 環境需求

- Python 3.8+
- Node.js (用於 Playwright)

### 安裝步驟

1. **克隆專案**
```bash
git clone https://github.com/Fangwentsai/apple_scraper.git
cd apple_scraper
```

2. **安裝 Python 依賴**
```bash
pip install -r requirements.txt
```

3. **安裝 Playwright 瀏覽器**
```bash
playwright install chromium
```

## 📁 檔案結構

```
apple_scraper/
├── README.md                           # 專案說明文件
├── requirements.txt                    # Python 依賴套件
├── apple_scraper.py                    # 主要爬蟲程式
├── chatgpt_query.py                    # ChatGPT 查詢介面
├── linebot_service.py                  # Line Bot 服務
├── render_keepalive.py                 # Render 防休眠程式
├── data/                               # 資料目錄
│   ├── apple_refurbished_mac.json      # Mac 整修品資料
│   ├── apple_refurbished_ipad.json     # iPad 整修品資料
│   ├── apple_refurbished_airpods.json  # AirPods 整修品資料
│   ├── apple_refurbished_homepod.json  # HomePod 整修品資料
│   ├── apple_refurbished_accessories.json # 配件整修品資料
│   ├── apple_refurbished_iphone.json   # iPhone 整修品資料
│   ├── apple_refurbished_appletv.json  # Apple TV 整修品資料
│   └── apple_refurbished_summary.json  # 總結資料
└── templates/                          # 模板目錄
    └── flex_templates.json             # Line Bot Flex Message 模板
```

## 🔧 使用方法

### 1. 爬取 Apple 整修品資料

```bash
python apple_scraper.py
```

這會：
- 爬取所有類別的 Apple 整修品
- 使用完整的 Headers 模擬真實瀏覽器
- 將資料分別儲存到對應的 JSON 檔案
- 生成總結報告

### 2. ChatGPT 查詢介面

```bash
python chatgpt_query.py
```

功能：
- 載入所有整修品資料
- 提供結構化的查詢介面
- 支援按類別、價格範圍、關鍵字搜尋
- 格式化輸出適合 ChatGPT 使用

### 3. Line Bot 服務

```bash
python linebot_service.py
```

功能：
- 整合 Line Messaging API
- 支援 Quick Reply 快速選單
- 使用 Flex Message 美化產品展示
- 提供互動式產品查詢

### 4. Render 防休眠服務

```bash
python render_keepalive.py
```

功能：
- 每 5 分鐘自動發送請求防止休眠
- 可選擇性重新爬取資料
- 適用於 Render 免費版部署

## 🌐 部署到 Render

### 1. 準備部署檔案

確保專案包含以下檔案：
- `requirements.txt`
- `render_keepalive.py`
- 所有資料檔案

### 2. 在 Render 建立服務

1. 連接 GitHub 倉庫
2. 選擇 Web Service
3. 設定環境變數：
   ```
   LINE_CHANNEL_ACCESS_TOKEN=你的Line Bot Token
   LINE_CHANNEL_SECRET=你的Line Bot Secret
   ```

### 3. 部署設定

- **Build Command**: `pip install -r requirements.txt && playwright install chromium`
- **Start Command**: `python render_keepalive.py`

## 📱 Line Bot 設定

### 1. 建立 Line Bot

1. 前往 [Line Developers Console](https://developers.line.biz/)
2. 建立新的 Provider 和 Channel
3. 取得 Channel Access Token 和 Channel Secret

### 2. 設定 Webhook

將 Render 部署的 URL 設定為 Line Bot 的 Webhook URL：
```
https://your-app.onrender.com/webhook
```

### 3. 功能特色

- **Quick Reply 選單**：快速選擇產品類別
- **Flex Message**：美化的產品卡片展示
- **互動式查詢**：支援關鍵字搜尋和價格篩選

## 🔍 API 介面

### ChatGPT 查詢 API

```python
from chatgpt_query import AppleRefurbishedQuery

query = AppleRefurbishedQuery()

# 搜尋 Mac 產品
mac_products = query.search_by_category('mac')

# 價格範圍搜尋
budget_products = query.search_by_price_range(10000, 30000)

# 關鍵字搜尋
macbook_products = query.search_by_keyword('MacBook')
```

### Line Bot 訊息格式

```python
from linebot_service import create_product_flex_message

# 建立產品 Flex Message
flex_message = create_product_flex_message(product_data)

# 建立 Quick Reply 選單
quick_reply = create_category_quick_reply()
```

## 📊 資料格式

每個產品的 JSON 格式：
```json
{
  "序號": 1,
  "產品標題": "MacBook Air M2 8GB 256GB - 太空灰色 (整修品)",
  "產品售價": "NT$25,900",
  "產品概覽": "MacBook Air M2 8GB 256GB - 太空灰色 (整修品)",
  "產品URL": "https://www.apple.com/tw/shop/refurbished/mac"
}
```

## 🛠️ 技術特色

### 爬蟲技術
- **Playwright** 處理動態網頁
- **完整 Headers** 模擬真實瀏覽器
- **人性化延遲** 避免被反爬蟲偵測
- **錯誤重試機制** 提高穩定性

### Line Bot 功能
- **Quick Reply** 快速選單導航
- **Flex Message** 豐富的視覺展示
- **Carousel** 多產品輪播展示
- **Postback Actions** 互動式操作

### 部署優化
- **防休眠機制** 適用於免費服務
- **自動更新** 定期重新爬取資料
- **錯誤監控** 自動記錄和報告

## 🔧 自訂設定

### 修改爬取頻率

編輯 `render_keepalive.py`：
```python
# 修改爬取間隔（秒）
SCRAPE_INTERVAL = 3600  # 1小時爬取一次
```

### 新增產品類別

編輯 `apple_scraper.py`：
```python
self.categories['new_category'] = {
    'url': 'https://www.apple.com/tw/shop/refurbished/new_category',
    'filename': 'apple_refurbished_new_category.json',
    'name': '新類別整修品'
}
```

## 📞 支援與貢獻

- **Issues**: [GitHub Issues](https://github.com/Fangwentsai/apple_scraper/issues)
- **Pull Requests**: 歡迎提交改進建議
- **聯絡**: 透過 GitHub 或 Line Bot 聯繫

## 📄 授權

MIT License - 詳見 [LICENSE](LICENSE) 檔案

## 🙏 致謝

- Apple 台灣官網提供整修品資訊
- Playwright 團隊提供優秀的網頁自動化工具
- Line Messaging API 提供豐富的聊天機器人功能
- Render 提供免費的雲端部署服務

---

**⭐ 如果這個專案對您有幫助，請給個 Star！** 