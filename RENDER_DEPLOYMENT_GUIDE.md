# Render 部署指南

## 🚨 Python 3.13 相容性問題解決方案

### 問題描述
在 Render 部署時遇到以下錯誤：
```
error: #error "this header requires Py_BUILD_CORE define"
ERROR: Failed building wheel for greenlet
Failed to build lxml aiohttp greenlet
```

### 解決方案

#### 1. 已修復的檔案
- ✅ `requirements.txt` - 移除問題套件，使用穩定版本
- ✅ `runtime.txt` - 降級到 Python 3.11.7
- ✅ `build.sh` - Render 建置腳本
- ✅ `start.sh` - Render 啟動腳本

#### 2. Render 設定

**Build Command:**
```bash
./build.sh
```

**Start Command:**
```bash
./start.sh
```

**Environment Variables:**
```
PYTHON_VERSION=3.11.7
```

#### 3. 套件版本說明

**穩定版本套件：**
- `flask==2.2.5` - Web 框架
- `requests==2.28.2` - HTTP 請求
- `beautifulsoup4==4.12.2` - HTML 解析
- `lxml==4.9.3` - XML/HTML 處理
- `greenlet==2.0.2` - 修復相容性問題

**移除的套件：**
- `playwright` - 在 Render 上資源消耗過大，改用 requests + BeautifulSoup
- `aiohttp` 版本指定 - 讓 line-bot-sdk 2.4.2 自動決定使用 aiohttp==3.8.4

### 部署步驟

1. **確認檔案已更新**
   ```bash
   git status
   git log --oneline -5
   ```

2. **在 Render Dashboard 設定**
   - Build Command: `./build.sh`
   - Start Command: `./start.sh`
   - Python Version: 3.11.7

3. **觸發重新部署**
   - 在 Render Dashboard 點擊 "Manual Deploy"
   - 或推送新的 commit 觸發自動部署

4. **監控部署日誌**
   - 檢查建置日誌確認套件安裝成功
   - 檢查啟動日誌確認服務正常運行

### 故障排除

#### 如果仍然遇到套件安裝問題：

1. **檢查 Python 版本**
   ```bash
   python --version  # 應該是 3.11.7
   ```

2. **清除 Render 快取**
   - 在 Render Dashboard 的 Settings 中清除 Build Cache

3. **檢查套件相容性**
   ```bash
   pip install --dry-run -r requirements.txt
   ```

#### 如果服務啟動失敗：

1. **檢查環境變數**
   - 確認所有必要的環境變數已設定
   - 特別是 Firebase 和 Line Bot 相關變數

2. **檢查埠號設定**
   ```bash
   echo $PORT  # Render 會自動設定
   ```

3. **檢查 Gunicorn 設定**
   - Workers: 1 (避免記憶體不足)
   - Timeout: 120 秒
   - Bind: 0.0.0.0:$PORT

### 本地測試

在部署前，可以本地測試相容性：

```bash
# 建立虛擬環境
python3.11 -m venv venv_test
source venv_test/bin/activate

# 安裝套件
pip install -r requirements.txt

# 測試套件相容性
python test_dependencies.py

# 測試啟動
python app.py
```

### 回滾方案

如果新版本有問題，可以回滾到備份版本：

```bash
# 恢復原始 requirements.txt
cp requirements.txt.backup_* requirements.txt

# 恢復原始 runtime.txt
cp runtime.txt.backup_* runtime.txt

# 提交回滾
git add .
git commit -m "回滾到穩定版本"
git push
```

### 監控和維護

1. **定期檢查套件更新**
   ```bash
   pip list --outdated
   ```

2. **監控服務狀態**
   - Render Dashboard 的 Metrics
   - 應用程式日誌

3. **效能優化**
   - 監控記憶體使用量
   - 調整 Gunicorn workers 數量

### 聯絡支援

如果問題持續存在：
1. 檢查 Render 官方文件
2. 查看 Render Community Forum
3. 提交 Support Ticket

---

**最後更新：** 2024-06-14
**版本：** 1.0
**狀態：** ✅ 已測試並修復 