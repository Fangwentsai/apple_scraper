# Firebase 備份系統設定指南

## 📋 設定步驟

### 1. 建立 Firebase 專案
1. 前往 [Firebase Console](https://console.firebase.google.com/)
2. 點擊「建立專案」
3. 輸入專案名稱（例如：`apple-scraper-backup`）
4. 選擇是否啟用 Google Analytics（可選）
5. 點擊「建立專案」

### 2. 啟用 Firestore 資料庫
1. 在 Firebase Console 中，點擊左側選單的「Firestore Database」
2. 點擊「建立資料庫」
3. 選擇「以測試模式啟動」（稍後可修改安全規則）
4. 選擇資料庫位置（建議選擇 `asia-east1` 或 `asia-southeast1`）
5. 點擊「完成」

### 3. 建立服務帳戶
1. 在 Firebase Console 中，點擊左上角的齒輪圖示 → 「專案設定」
2. 點擊「服務帳戶」分頁
3. 點擊「產生新的私密金鑰」
4. 下載 JSON 檔案並重新命名為 `firebase-service-account.json`
5. 將檔案放在專案根目錄

### 4. 設定安全規則（可選）
在 Firestore 中設定適當的安全規則：

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // 允許讀取所有文件（用於查詢）
    match /{document=**} {
      allow read: if true;
    }
    
    // 只允許服務帳戶寫入
    match /apple_refurbished_{category}/{document} {
      allow write: if request.auth != null;
    }
    
    match /price_changes/{document} {
      allow write: if request.auth != null;
    }
    
    match /backup_history/{document} {
      allow write: if request.auth != null;
    }
  }
}
```

## 🗂️ Firestore 資料結構

### 產品資料集合
- `apple_refurbished_mac` - Mac 產品
- `apple_refurbished_ipad` - iPad 產品
- `apple_refurbished_airpods` - AirPods 產品
- `apple_refurbished_homepod` - HomePod 產品
- `apple_refurbished_accessories` - 配件產品
- `apple_refurbished_iphone` - iPhone 產品（如有）
- `apple_refurbished_appletv` - Apple TV 產品（如有）

### 系統集合
- `price_changes` - 價格變更記錄
- `backup_history` - 備份歷史記錄

## 🔧 使用方法

### 基本備份
```python
from firebase_backup import FirebaseBackup

# 使用服務帳戶金鑰
backup = FirebaseBackup('firebase-service-account.json')

# 備份所有類別
backup.backup_all_categories()
```

### 定期備份
```python
from firebase_scheduler import FirebaseScheduler

# 啟動定期備份
scheduler = FirebaseScheduler('firebase-service-account.json')
scheduler.start_scheduler()
```

### 環境變數設定
也可以使用環境變數：
```bash
export GOOGLE_APPLICATION_CREDENTIALS="path/to/firebase-service-account.json"
```

## 📊 資料查詢範例

### 查詢特定類別產品
```python
# 查詢所有 Mac 產品
docs = db.collection('apple_refurbished_mac').stream()
for doc in docs:
    print(f'{doc.id} => {doc.to_dict()}')
```

### 查詢價格變更記錄
```python
# 查詢最近的價格變更
docs = db.collection('price_changes')\
         .order_by('change_timestamp', direction=firestore.Query.DESCENDING)\
         .limit(10)\
         .stream()

for doc in docs:
    change = doc.to_dict()
    print(f"{change['product_title']}: {change['old_price']} → {change['new_price']}")
```

## 🚀 部署到 Render

### 環境變數設定
在 Render 中設定以下環境變數：
- `GOOGLE_APPLICATION_CREDENTIALS`: 服務帳戶金鑰的內容（JSON 字串）

### 或者上傳金鑰檔案
將 `firebase-service-account.json` 包含在部署檔案中

## 🔒 安全注意事項

1. **金鑰檔案安全**：
   - 不要將服務帳戶金鑰提交到 Git
   - 在 `.gitignore` 中加入 `firebase-service-account.json`

2. **Firestore 規則**：
   - 設定適當的安全規則
   - 限制寫入權限給服務帳戶

3. **資料備份**：
   - 定期匯出 Firestore 資料
   - 設定自動備份策略

## 📈 監控和分析

### 查看備份統計
```python
stats = backup.get_backup_statistics()
print(f"總備份次數: {stats['total_backups']}")
print(f"最後備份時間: {stats['last_backup']}")
```

### 價格變更追蹤
```python
changes = backup.get_price_change_history(50)
for change in changes:
    print(f"{change['product_title']}: {change['old_price']} → {change['new_price']}")
```

## 🆘 常見問題

### Q: Firebase 初始化失敗
A: 檢查服務帳戶金鑰檔案路徑和權限

### Q: 權限被拒絕
A: 確認 Firestore 安全規則和服務帳戶權限

### Q: 資料未同步
A: 檢查網路連接和 Firebase 專案設定

### Q: 價格變更未記錄
A: 確認 `check_price_changes` 參數為 `True` 