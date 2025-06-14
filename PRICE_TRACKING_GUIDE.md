# 🏷️ Apple 整修品價格追蹤系統使用指南

## 📋 系統概述

Apple 整修品價格追蹤系統是一個完整的價格監控解決方案，能夠：

- 📊 **每日價格記錄**：自動記錄每件商品每天的價格變化
- 🔔 **智能通知系統**：降價時自動通知相關用戶
- 📈 **價格趨勢分析**：提供詳細的價格分析和市場報告
- ☁️ **雲端備份**：所有資料自動備份到 Firebase
- 🤖 **自動化排程**：無需人工干預的全自動運行

## 🚀 快速開始

### 1. 建立範例資料（首次使用）

```bash
# 建立30天的範例價格歷史資料
python create_sample_price_data.py
```

這會建立：
- 過去30天的價格歷史資料
- 包含價格變化的範例資料
- 用於測試分析功能的完整資料集

### 2. 執行價格追蹤

```bash
# 手動執行一次價格追蹤
python price_tracker.py
```

選擇功能：
1. **執行今日價格追蹤** - 爬取最新價格並比較變化
2. **查看產品價格歷史** - 查詢特定產品的價格變化
3. **生成價格變化報告** - 產生詳細的價格分析報告
4. **查看價格變化摘要** - 快速瀏覽價格變化統計

### 3. 啟動自動排程

```bash
# 啟動每日價格追蹤排程器
python daily_price_scheduler.py
```

自動排程時間：
- **每天 09:00** - 執行價格追蹤
- **每天 21:00** - 執行價格追蹤  
- **每天 22:00** - 生成每日報告

## 📊 價格分析工具

### 啟動分析工具

```bash
python price_analyzer.py
```

### 分析功能

#### 1. 價格趨勢分析
- 分析每個產品的價格變化趨勢
- 計算價格波動性和變化百分比
- 判斷趨勢方向（上漲/下跌/穩定）

#### 2. 類別價格統計
- 各產品類別的價格分布
- 最高價、最低價、平均價、中位數
- 價格範圍和標準差

#### 3. 最佳優惠查詢
- 找出降價最多的產品
- 按降價金額或百分比排序
- 提供購買建議

#### 4. 市場報告生成
- 完整的市場分析報告
- 包含趨勢分析、統計資料、最佳優惠
- 適合定期檢視市場狀況

## 🔔 通知系統設定

### Firebase 設定

1. **建立 Firebase 專案**
   - 前往 [Firebase Console](https://console.firebase.google.com/)
   - 建立新專案
   - 啟用 Firestore Database

2. **下載服務帳戶金鑰**
   - 專案設定 → 服務帳戶
   - 產生新的私密金鑰
   - 將檔案命名為 `firebase-service-account.json`

3. **設定 Firestore 規則**
   ```javascript
   rules_version = '2';
   service cloud.firestore {
     match /databases/{database}/documents {
       match /{document=**} {
         allow read, write: if true;
       }
     }
   }
   ```

### Line Bot 通知設定

1. **設定 Line Bot**
   - 參考主要 README.md 的 Line Bot 設定章節
   - 確保 Webhook 正常運作

2. **用戶通知請求**
   - 用戶透過 Line Bot 設定關注的產品類別和價格範圍
   - 系統會在 Firebase 中記錄用戶請求
   - 當有符合條件的降價時自動發送通知

## 📁 資料結構

### 價格歷史檔案格式

```json
{
  "date": "2024-01-15",
  "timestamp": "2024-01-15T09:00:00",
  "categories": {
    "mac": {
      "product_count": 84,
      "products": [
        {
          "product_id": "mac_1234",
          "title": "MacBook Air M2 8GB 256GB - 太空灰色 (整修品)",
          "price": 25900,
          "price_str": "NT$25,900",
          "url": "https://...",
          "category": "mac"
        }
      ]
    }
  },
  "total_products": 100,
  "price_changes": [
    {
      "product_id": "mac_1234",
      "title": "MacBook Air M2 8GB 256GB - 太空灰色 (整修品)",
      "category": "mac",
      "old_price": 26900,
      "new_price": 25900,
      "change_amount": -1000,
      "change_percentage": -3.72
    }
  ],
  "new_products": [],
  "discontinued_products": []
}
```

### Firebase 資料結構

#### 1. price_tracking Collection
- 文件ID：日期 (YYYY-MM-DD)
- 內容：完整的每日價格追蹤資料

#### 2. price_changes Collection
- 自動生成文件ID
- 內容：個別價格變化記錄

#### 3. requests Collection（增強版）
- 文件ID：自動生成
- 內容：用戶通知請求
```json
{
  "userid": "Line用戶ID",
  "product": "產品類別",
  "price": 最高價格,
  "category": "產品類別",
  "notice": false,
  "created_at": "建立時間",
  "updated_at": "更新時間",
  "last_query_date": "最後查詢日期",
  "notification_count": 0,
  "active": true
}
```

#### 4. price_volatility_events Collection（新增）
- 文件ID：自動生成
- 內容：價格波動事件記錄
```json
{
  "category": "產品類別",
  "product_title": "產品標題",
  "old_price": 舊價格,
  "new_price": 新價格,
  "change_amount": 變化金額,
  "change_percentage": 變化百分比,
  "event_type": "price_drop/price_increase",
  "severity": "high/medium",
  "timestamp": "事件時間",
  "date": "事件日期",
  "notified_users": 通知用戶數量
}
```

#### 5. notification_history Collection（新增）
- 文件ID：自動生成
- 內容：通知歷史記錄
```json
{
  "userid": "Line用戶ID",
  "notification_type": "price_drop/price_volatility/new_product",
  "category": "產品類別",
  "content": "通知內容",
  "timestamp": "通知時間",
  "date": "通知日期"
}
```

#### 4. system_logs Collection
- 文件ID：自動生成
- 內容：系統執行日誌

## ⚡ 價格波動通知功能

### 功能特色

1. **自動偵測高波動性產品**
   - 偵測價格變化超過 10% 的產品
   - 支援降價和漲價雙向偵測
   - 自動記錄波動事件到 Firebase

2. **智能用戶通知**
   - 通知最近 3 天內查詢過該類別的用戶
   - 避免重複通知，提升用戶體驗
   - 記錄通知歷史和統計

3. **類別追蹤系統**
   - 記錄用戶查詢的產品類別
   - 精準匹配用戶興趣
   - 支援多類別同時追蹤

### 使用方式

#### 1. 測試價格波動通知
```bash
# 執行測試腳本
python test_volatility_notifications.py
```

#### 2. 手動觸發波動檢查
```python
from daily_price_scheduler import DailyPriceScheduler

scheduler = DailyPriceScheduler()
# 這會自動檢查並發送波動通知
scheduler.run_daily_tracking()
```

#### 3. 查詢波動事件
```python
from firebase_enhanced_requests import EnhancedFirebaseRequests

firebase_requests = EnhancedFirebaseRequests()

# 查詢高波動性產品
volatile_products = firebase_requests.get_high_volatility_products(days=7)

# 查詢最近查詢過某類別的用戶
recent_users = firebase_requests.get_recent_category_users('mac', days=3)
```

### 通知訊息範例

當偵測到價格波動時，系統會發送類似以下的通知：

```
⚡ MAC 產品價格大幅波動警報！

📊 發現 3 個產品價格變化超過 10%

📉 大幅降價 (2 個):
• MacBook Air M2 8GB 256GB - 太空灰色...
  降價 20.0% (省 NT$7,000)
  現價 NT$28,000

• iMac 24吋 M1 8GB 256GB - 藍色...
  降價 15.6% (省 NT$7,000)
  現價 NT$38,000

📈 大幅漲價 (1 個):
• MacBook Pro 13吋 M2 8GB 256GB...
  漲價 12.5%
  現價 NT$45,000

💡 這是因為您最近3天內查詢過此類別產品
🛒 如有興趣請把握機會！
```

## 🛠️ 進階設定

### 自訂價格追蹤頻率

編輯 `daily_price_scheduler.py`：

```python
# 修改排程時間
schedule.every().day.at("09:00").do(self.daily_price_tracking)  # 早上9點
schedule.every().day.at("21:00").do(self.daily_price_tracking)  # 晚上9點

# 或設定更頻繁的追蹤
schedule.every(4).hours.do(self.daily_price_tracking)  # 每4小時
```

### 自訂通知條件

編輯 `daily_price_scheduler.py` 中的通知邏輯：

```python
# 修改降價通知條件
if (drop['category'] == requested_product and 
    drop['new_price'] <= max_price and
    abs(drop['change_percentage']) >= 5):  # 降價超過5%才通知
```

### 自訂分析參數

編輯 `price_analyzer.py` 中的分析參數：

```python
# 修改趨勢判斷標準
if total_change_percent > 3:      # 漲價超過3%
    trend_direction = "上漲"
elif total_change_percent < -3:   # 降價超過3%
    trend_direction = "下跌"
else:
    trend_direction = "穩定"
```

## 🔍 故障排除

### 常見問題

#### 1. 沒有價格歷史資料
```bash
# 建立範例資料
python create_sample_price_data.py
```

#### 2. Firebase 連接失敗
- 檢查 `firebase-service-account.json` 檔案是否存在
- 確認 Firebase 專案設定正確
- 檢查網路連接

#### 3. Line Bot 通知失敗
- 確認 Line Bot Token 設定正確
- 檢查 Webhook URL 是否可訪問
- 確認用戶已加入 Line Bot 好友

#### 4. 價格追蹤無資料
- 確認爬蟲程式正常運作
- 檢查網路連接和 Apple 官網可訪問性
- 查看系統日誌了解錯誤原因

### 日誌檢查

系統會在以下位置記錄日誌：
- **本地檔案**：`price_history/` 目錄
- **Firebase**：`system_logs` Collection
- **終端輸出**：執行程式時的即時日誌

## 📈 效能優化

### 1. 資料清理

定期清理舊的價格歷史檔案：
```bash
# 保留最近30天的資料
find price_history/ -name "*.json" -mtime +30 -delete
```

### 2. Firebase 成本控制

- 設定 Firestore 讀寫限制
- 定期清理舊的日誌資料
- 使用 Firebase 的免費額度監控

### 3. 記憶體優化

對於大量資料的處理，可以：
- 分批處理產品資料
- 使用生成器減少記憶體使用
- 定期清理暫存資料

## 🎯 最佳實踐

1. **定期備份**：除了 Firebase，也要定期備份本地資料
2. **監控系統**：設定系統監控，及時發現問題
3. **用戶體驗**：優化通知內容，避免過度打擾用戶
4. **資料品質**：定期檢查資料準確性，修正異常值
5. **安全性**：保護 API 金鑰和敏感資料

## 📞 技術支援

如果遇到問題，請：

1. 檢查本指南的故障排除章節
2. 查看系統日誌了解錯誤詳情
3. 確認所有依賴套件已正確安裝
4. 檢查網路連接和外部服務狀態

---

**🎉 恭喜！你現在已經掌握了完整的 Apple 整修品價格追蹤系統！** 