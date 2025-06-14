# 🍎 增強版 Apple 爬蟲使用指南

## 📋 概述

增強版 Apple 爬蟲專門設計來從 Apple 產品頁面的 `rc-pdsection-mainpanel column large-9 small-12` 區域提取詳細的產品概覽和規格資訊，而不是僅僅複製產品標題。

## 🎯 主要功能

### 1. 詳細產品概覽提取
- 從 `rc-pdsection-mainpanel` 區域提取完整產品描述
- 包含產品規格、特色、技術細節
- 自動清理和格式化文字內容
- 範例輸出：
  ```
  最初於 2023 年 10 月推出
  16.2 吋 (對角線) Liquid Retina XDR 顯示器¹；3456 x 2234 原生解析度，每吋 254 像素
  48GB 統一記憶體
  1TB SSD²
  Touch ID
  1080p FaceTime HD 相機
  三個 Thunderbolt 4 (USB-C) 埠
  ```

### 2. 多重選擇器策略
程式使用多種 CSS 選擇器來確保能夠提取到產品資訊：
- `.rc-pdsection-mainpanel.column.large-9.small-12`
- `.rc-pdsection-mainpanel`
- `.pd-overview`
- `.pd-highlights`
- `.rf-pdp-overview`
- `.rf-pdp-techspecs`

### 3. 智能文字清理
- 移除購買按鈕、法律聲明等無關內容
- 保留重要的產品規格和特色
- 格式化換行和空白
- 限制文字長度避免過長

## 🚀 使用方法

### 方法一：生產版概覽更新（推薦）

```bash
python3 production_overview_updater.py
```

**功能：**
- 載入現有的產品資料
- 根據產品 URL 訪問詳細頁面
- 從 `rc-pdsection-mainpanel` 區域提取詳細概覽
- 自動備份原始檔案
- 支援分批處理和斷點續傳

**適用情況：**
- 已有產品資料，需要更新概覽欄位
- 想要保持現有的資料結構和序號
- 需要處理大量產品資料

**使用範例：**
```bash
# 更新 Mac 類別的所有產品
python3 production_overview_updater.py
# 選擇 1 (Mac)，然後按 Enter 使用預設設定

# 更新前 10 個產品
python3 production_overview_updater.py
# 選擇類別，輸入 10 作為數量限制

# 從第 20 個產品開始更新
python3 production_overview_updater.py
# 選擇類別，設定開始位置為 20
```

### 方法二：簡化版測試

```bash
python3 simple_overview_test.py
```

**功能：**
- 測試概覽提取功能
- 處理前 3 個產品作為範例
- 比較原始概覽和增強概覽的差異
- 驗證提取的概覽品質

**適用情況：**
- 測試功能是否正常運作
- 驗證概覽提取效果
- 在大量更新前先測試

### 方法三：全新爬取（進階用戶）

```bash
python3 enhanced_apple_scraper.py
```

**功能：**
- 從 Apple 網站爬取產品列表
- 訪問每個產品的詳細頁面
- 提取完整的產品概覽和規格
- 儲存到新的 JSON 檔案

**適用情況：**
- 需要爬取新的產品類別
- 想要建立包含詳細概覽的全新資料集

## 📊 資料結構比較

### 原始資料結構
```json
{
  "序號": 1,
  "產品標題": "16 吋 MacBook Pro Apple M3 Max 晶片配備 16 核心 CPU 與 40 核心 GPU - 太空黑色 (整修品)",
  "產品概覽": "16 吋 MacBook Pro Apple M3 Max 晶片配備 16 核心 CPU 與 40 核心 GPU - 太空黑色 (整修品)",
  "產品售價": "NT$89,900",
  "產品URL": "https://www.apple.com/tw/shop/product/..."
}
```

### 增強後資料結構
```json
{
  "序號": 1,
  "產品標題": "16 吋 MacBook Pro Apple M3 Max 晶片配備 16 核心 CPU 與 40 核心 GPU - 太空黑色 (整修品)",
  "產品概覽": "最初於 2023 年 10 月推出\n16.2 吋 (對角線) Liquid Retina XDR 顯示器¹；3456 x 2234 原生解析度，每吋 254 像素\n48GB 統一記憶體\n1TB SSD²\nTouch ID\n1080p FaceTime HD 相機\n三個 Thunderbolt 4 (USB-C) 埠",
  "產品售價": "NT$89,900",
  "產品URL": "https://www.apple.com/tw/shop/product/...",
  "category": "mac"
}
```

## ⚙️ 設定選項

### 爬取數量限制
```python
# 限制爬取 5 個產品
products = await scraper.scrape_category_with_details('mac', limit=5)

# 爬取所有產品
products = await scraper.scrape_category_with_details('mac')
```

### 支援的產品類別
- `mac` - Mac 電腦
- `ipad` - iPad 平板
- `iphone` - iPhone 手機
- `airpods` - AirPods 耳機
- `homepod` - HomePod 音響
- `appletv` - Apple TV
- `accessories` - 配件

### 瀏覽器設定
```python
# 顯示瀏覽器（除錯用）
headless=False

# 隱藏瀏覽器（生產環境）
headless=True
```

## 🛠️ 故障排除

### 常見問題

1. **無法提取到概覽**
   - 檢查網路連線
   - 確認 Apple 網站可正常訪問
   - 檢查產品 URL 是否有效

2. **概覽內容不完整**
   - Apple 可能更新了網頁結構
   - 檢查 CSS 選擇器是否需要更新
   - 增加等待時間讓頁面完全載入

3. **程式執行緩慢**
   - 調整 `asyncio.sleep()` 的等待時間
   - 減少同時處理的產品數量
   - 檢查網路速度

### 日誌分析

程式會輸出詳細的日誌資訊：
```
2024-01-15 10:30:15 - INFO - 🔍 提取產品概覽: https://www.apple.com/tw/shop/product/...
2024-01-15 10:30:18 - INFO - ✅ 找到概覽區域: .rc-pdsection-mainpanel
2024-01-15 10:30:19 - INFO - ✅ 成功提取概覽 (456 字元)
```

## 📁 檔案說明

### 核心檔案
- `enhanced_apple_scraper.py` - 增強版爬蟲主程式
- `update_product_overview.py` - 概覽更新工具
- `test_enhanced_scraper.py` - 測試腳本

### 輸出檔案
- `data/apple_refurbished_{category}_enhanced.json` - 增強版產品資料
- `data/apple_refurbished_{category}_backup_{timestamp}.json` - 備份檔案
- `data/{category}_overview_test_result.json` - 測試結果

## 🔄 整合現有系統

### 與價格追蹤系統整合
增強版概覽可以直接整合到現有的價格追蹤系統中：

```python
# 在 price_tracker.py 中使用增強版資料
def load_products_data(self, category: str):
    filename = f'data/apple_refurbished_{category}.json'  # 已包含增強概覽
    # ... 現有邏輯保持不變
```

### 與 Line Bot 整合
Line Bot 可以發送更詳細的產品資訊：

```python
# 在 linebot_service.py 中
def create_product_flex_message(self, product):
    overview = product.get('產品概覽', '')
    # 使用詳細概覽建立更豐富的 Flex Message
```

## 🎯 最佳實踐

1. **定期更新概覽**
   - 建議每週執行一次概覽更新
   - 新產品上市時立即更新

2. **備份策略**
   - 程式會自動備份原始檔案
   - 建議定期備份到雲端儲存

3. **效能優化**
   - 使用 `limit` 參數控制處理數量
   - 在非尖峰時間執行大量更新

4. **品質檢查**
   - 定期檢查概覽內容品質
   - 使用測試腳本驗證功能

## 📞 支援

如果遇到問題或需要協助，請檢查：
1. 日誌輸出中的錯誤訊息
2. Apple 網站是否可正常訪問
3. 產品 URL 是否有效
4. 網路連線是否穩定

---

**注意：** 請遵守 Apple 網站的使用條款，適度使用爬蟲功能，避免對伺服器造成過大負擔。 