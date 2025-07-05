# 多平台影片下載工具

這是一個使用 Streamlit 建立的多平台影片下載工具，支援 YouTube、Facebook、Instagram、Dcard、TikTok 等平台的影片下載。

## 功能特色

- 🎯 **多平台支援**：支援 YouTube、Facebook、Instagram、Dcard、TikTok、Twitter/X 等主流平台
- 📥 **雙重下載模式**：可選擇直接下載檔案或僅取得下載連結
- 🎵 **格式轉換**：支援 MP4 影片格式和 MP3 音訊格式
- 📝 **智慧檔名處理**：自動清理不合法字元，確保檔名相容性
- 🔄 **自動格式轉換**：使用 FFmpeg 自動轉換不符合需求的格式
- 📊 **影片資訊預覽**：顯示影片標題、時長、上傳者、觀看次數等詳細資訊
- 🎨 **友善介面**：直觀的 Streamlit 網頁介面，操作簡單

## 安裝需求

### 系統需求
- Python 3.7 或更高版本
- FFmpeg（用於影片格式轉換）

### Python 套件
所有需要的 Python 套件都列在 `requirements.txt` 檔案中：

```
streamlit>=1.28.0
yt-dlp>=2023.10.13
pathlib2>=2.3.7
```

## 安裝步驟

1. **安裝 FFmpeg**（如果尚未安裝）：

   **Ubuntu/Debian:**
   ```bash
   sudo apt update
   sudo apt install ffmpeg
   ```

   **macOS (使用 Homebrew):**
   ```bash
   brew install ffmpeg
   ```

   **Windows:**
   - 從 [FFmpeg 官網](https://ffmpeg.org/download.html) 下載
   - 將 FFmpeg 加入系統 PATH

2. **安裝 Python 依賴套件**：
   ```bash
   pip install -r requirements.txt
   ```

## 使用方法

1. **啟動應用程式**：
   ```bash
   streamlit run app.py
   ```

2. **開啟瀏覽器**：
   - 應用程式會自動在瀏覽器中開啟
   - 預設網址：http://localhost:8501

3. **使用步驟**：
   - 在「影片網址」欄位貼上您想下載的影片連結
   - 選擇下載方式：
     - **下載為檔案**：直接下載影片到您的裝置
     - **取得影片連結**：僅取得下載連結，可用於其他下載工具
   - 選擇輸出格式：
     - **MP4**：影片格式，包含影像和聲音
     - **MP3**：音訊格式，僅包含聲音
   - 點擊「開始下載」按鈕

## 支援的平台

- 🔴 **YouTube** - 支援各種影片格式和品質
- 📘 **Facebook** - 支援公開影片
- 📷 **Instagram** - 支援貼文和限時動態影片
- 💬 **Dcard** - 支援 Dcard 平台影片
- 🎵 **TikTok** - 支援 TikTok 短影片
- 🐦 **Twitter/X** - 支援推文中的影片
- 📺 **其他平台** - 支援 yt-dlp 相容的其他影片平台

## 注意事項

- ⚠️ **版權聲明**：請遵守各平台的使用條款和版權規定
- 🔒 **平台限制**：某些平台可能有下載限制或需要登入
- 📁 **檔名處理**：檔名會自動清理不合法字元，確保相容性
- 🔄 **格式轉換**：如果原始格式不符合需求，會自動使用 FFmpeg 轉換
- 📱 **私人內容**：無法下載私人或受保護的內容

## 故障排除

### 常見問題

1. **HTTP Error 403: Forbidden**
   - 這通常表示該影片受到平台保護或有地區限制
   - 嘗試使用「取得影片連結」模式

2. **無法取得影片資訊**
   - 檢查網址是否正確
   - 確認影片是公開的
   - 某些平台可能需要更新 yt-dlp

3. **FFmpeg 相關錯誤**
   - 確認 FFmpeg 已正確安裝
   - 檢查 FFmpeg 是否在系統 PATH 中

### 更新 yt-dlp

如果遇到下載問題，可以嘗試更新 yt-dlp：

```bash
pip install --upgrade yt-dlp
```

## 技術架構

- **前端框架**：Streamlit
- **下載引擎**：yt-dlp
- **格式轉換**：FFmpeg
- **檔案處理**：Python pathlib

## 檔案結構

```
video-downloader/
├── app.py              # 主要應用程式檔案
├── requirements.txt    # Python 依賴套件列表
└── README.md          # 說明文件
```

## 授權

本專案僅供學習和個人使用。使用時請遵守相關平台的服務條款和當地法律法規。

## 更新日誌

- **v1.0.0** - 初始版本
  - 支援多平台影片下載
  - MP4/MP3 格式選擇
  - 智慧檔名處理
  - FFmpeg 自動格式轉換

