import streamlit as st
import yt_dlp
import os
import re
import subprocess
from pathlib import Path
import tempfile
import shutil

# 設定頁面配置
st.set_page_config(
    page_title="多平台影片下載工具",
    page_icon="📹",
    layout="wide"
)

def sanitize_filename(filename):
    """清理檔名，移除不合法的字元"""
    # 移除或替換不合法的字元
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # 移除多餘的空格
    filename = re.sub(r'\s+', ' ', filename).strip()
    # 限制檔名長度
    if len(filename) > 200:
        filename = filename[:200]
    return filename

def get_video_info(url):
    """取得影片資訊"""
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                'title': info.get('title', 'Unknown'),
                'duration': info.get('duration', 0),
                'uploader': info.get('uploader', 'Unknown'),
                'view_count': info.get('view_count', 0),
                'thumbnail': info.get('thumbnail', ''),
            }
    except Exception as e:
        return None

def download_video(url, output_format, download_type):
    """下載影片"""
    try:
        # 建立臨時目錄
        temp_dir = tempfile.mkdtemp()
        
        # 取得影片資訊
        info = get_video_info(url)
        if not info:
            return None, "無法取得影片資訊"
        
        # 清理檔名
        clean_title = sanitize_filename(info['title'])
        
        # 設定下載選項
        if download_type == "影片連結":
            # 只取得下載連結，不實際下載
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'format': 'best[ext=mp4]/best',
                'geturl': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                download_url = ydl.extract_info(url, download=False)
                return download_url.get('url', ''), "成功取得下載連結"
        
        else:
            # 實際下載檔案
            if output_format == "MP4":
                ydl_opts = {
                    'format': 'best[ext=mp4]/best',
                    'outtmpl': os.path.join(temp_dir, f'{clean_title}.%(ext)s'),
                    'quiet': True,
                    'no_warnings': True,
                }
            else:  # MP3
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': os.path.join(temp_dir, f'{clean_title}.%(ext)s'),
                    'quiet': True,
                    'no_warnings': True,
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            # 尋找下載的檔案
            downloaded_files = list(Path(temp_dir).glob('*'))
            if downloaded_files:
                downloaded_file = downloaded_files[0]
                
                # 如果需要轉換格式
                final_extension = output_format.lower()
                if not downloaded_file.name.endswith(f'.{final_extension}'):
                    # 使用 ffmpeg 轉換
                    output_file = Path(temp_dir) / f'{clean_title}.{final_extension}'
                    
                    if final_extension == 'mp3':
                        cmd = ['ffmpeg', '-i', str(downloaded_file), '-acodec', 'mp3', '-ab', '192k', str(output_file), '-y']
                    else:  # mp4
                        cmd = ['ffmpeg', '-i', str(downloaded_file), '-c:v', 'libx264', '-c:a', 'aac', str(output_file), '-y']
                    
                    try:
                        subprocess.run(cmd, check=True, capture_output=True)
                        downloaded_file = output_file
                    except subprocess.CalledProcessError:
                        pass  # 如果轉換失敗，使用原檔案
                
                return str(downloaded_file), "下載成功"
            else:
                return None, "下載失敗：找不到檔案"
                
    except Exception as e:
        return None, f"下載失敗：{str(e)}"

# 主要介面
st.title("📹 多平台影片下載工具")
st.markdown("支援 YouTube、Facebook、Instagram、Dcard、TikTok 等平台")

# 側邊欄設定
with st.sidebar:
    st.header("⚙️ 設定")
    
    # 支援的平台列表
    st.subheader("支援的平台")
    platforms = [
        "🔴 YouTube",
        "📘 Facebook", 
        "📷 Instagram",
        "💬 Dcard",
        "🎵 TikTok",
        "🐦 Twitter/X",
        "📺 其他平台"
    ]
    
    for platform in platforms:
        st.write(platform)

# 主要內容區域
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🔗 影片網址")
    url = st.text_input(
        "請輸入影片網址",
        placeholder="https://www.youtube.com/watch?v=...",
        help="支援 YouTube、Facebook、Instagram、Dcard、TikTok 等平台的影片網址"
    )
    
    # 下載選項
    st.subheader("📥 下載選項")
    
    col_option1, col_option2 = st.columns(2)
    
    with col_option1:
        download_type = st.radio(
            "下載方式",
            ["下載為檔案", "取得影片連結"],
            help="選擇直接下載檔案或僅取得下載連結"
        )
    
    with col_option2:
        output_format = st.selectbox(
            "輸出格式",
            ["MP4", "MP3"],
            help="選擇影片格式(MP4)或音訊格式(MP3)"
        )

with col2:
    st.subheader("ℹ️ 影片資訊")
    
    if url:
        with st.spinner("正在取得影片資訊..."):
            info = get_video_info(url)
            
        if info:
            st.success("✅ 成功取得影片資訊")
            
            # 顯示縮圖
            if info['thumbnail']:
                st.image(info['thumbnail'], width=200)
            
            # 顯示影片資訊
            st.write(f"**標題：** {info['title']}")
            st.write(f"**上傳者：** {info['uploader']}")
            
            if info['duration']:
                minutes = info['duration'] // 60
                seconds = info['duration'] % 60
                st.write(f"**時長：** {minutes}:{seconds}")
            
            if info['view_count']:
                st.write(f"**觀看次數：** {info['view_count']:,}")
                
            # 顯示清理後的檔名
            clean_filename = sanitize_filename(info['title'])
            st.write(f"**檔名：** {clean_filename}.{output_format.lower()}")
            
        else:
            st.error("❌ 無法取得影片資訊，請檢查網址是否正確")

# 下載按鈕
st.subheader("🚀 開始下載")

if st.button("開始下載", type="primary", use_container_width=True):
    if not url:
        st.error("請先輸入影片網址")
    else:
        with st.spinner("正在處理中..."):
            result, message = download_video(url, output_format, download_type)
        
        if result:
            st.success(f"✅ {message}")
            
            if download_type == "取得影片連結":
                st.subheader("📋 下載連結")
                st.code(result, language=None)
                st.info("💡 您可以複製此連結使用其他下載工具下載")
                
            else:
                st.subheader("📁 下載檔案")
                
                # 讀取檔案並提供下載
                try:
                    with open(result, 'rb') as file:
                        file_data = file.read()
                        file_name = os.path.basename(result)
                        
                        st.download_button(
                            label=f"📥 下載 {file_name}",
                            data=file_data,
                            file_name=file_name,
                            mime="application/octet-stream",
                            use_container_width=True
                        )
                        
                    # 清理臨時檔案
                    temp_dir = os.path.dirname(result)
                    shutil.rmtree(temp_dir, ignore_errors=True)
                    
                except Exception as e:
                    st.error(f"讀取檔案時發生錯誤：{str(e)}")
        else:
            st.error(f"❌ {message}")

# 頁腳資訊
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        <p>🛠️ 使用 yt-dlp 和 FFmpeg 技術</p>
        <p>⚠️ 請遵守各平台的使用條款和版權規定</p>
    </div>
    """,
    unsafe_allow_html=True
)

# 使用說明
with st.expander("📖 使用說明"):
    st.markdown("""
    ### 如何使用：
    
    1. **輸入網址**：在網址欄位貼上您想下載的影片連結
    2. **選擇下載方式**：
       - **下載為檔案**：直接下載影片到您的裝置
       - **取得影片連結**：僅取得下載連結，可用於其他下載工具
    3. **選擇格式**：
       - **MP4**：影片格式，包含影像和聲音
       - **MP3**：音訊格式，僅包含聲音
    4. **開始下載**：點擊下載按鈕開始處理
    
    ### 支援的平台：
    - YouTube
    - Facebook
    - Instagram
    - Dcard
    - TikTok
    - Twitter/X
    - 其他支援的影片平台
    
    ### 注意事項：
    - 請確保您有權下載該影片
    - 某些平台可能有下載限制
    - 檔名會自動清理不合法字元
    - 如果原始格式不符合需求，會自動使用 FFmpeg 轉換
    """)

