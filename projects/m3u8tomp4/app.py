import os
import uuid
import tempfile
import requests
import subprocess
import streamlit as st


# Streamlit UI
st.title("🎬 M3U8 to MP4 Downloader with AES-128 Decryption")
st.write("輸入一個 m3u8 網址，系統會判斷是否加密，並下載合併為 MP4 檔案")

# User input
m3u8_url = st.text_input("請輸入 m3u8 網址")

# Download and convert
if m3u8_url:
    with st.spinner("正在分析 m3u8 檔案..."):
        try:
            # Download m3u8 content
            response = requests.get(m3u8_url)
            m3u8_content = response.text

            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".m3u8", mode='w') as temp_m3u8:
                temp_m3u8.write(m3u8_content)
                temp_m3u8_path = temp_m3u8.name

            # Check for encryption
            key_line = next((line for line in m3u8_content.splitlines() if line.startswith("#EXT-X-KEY")), None)
            is_encrypted = key_line is not None

            # Generate output filename
            output_filename = f"{uuid.uuid4().hex}.mp4"

            if is_encrypted:
                st.warning("偵測到 AES-128 加密，正在嘗試取得金鑰...")

                # Extract URI from key line
                uri_start = key_line.find('URI="') + 5
                uri_end = key_line.find('"', uri_start)
                key_uri = key_line[uri_start:uri_end]

                # Try to fetch the key using curl
                try:
                    key_response = subprocess.run(["curl", "-s", key_uri], capture_output=True, text=True)
                    st.info(f"🔑 金鑰URL：`{key_uri}`")
                    key_value = key_response.stdout.strip()
                    st.info(f"🔑 金鑰內容：`{key_value}`")

                    # Run ffmpeg with decryption key
                    ffmpeg_cmd = [
                        "ffmpeg",
                        "-decryption_key", key_value,
                        "-allowed_extensions", "ALL",
                        "-i", m3u8_url,
                        "-c", "copy",
                        "-bsf:a", "aac_adtstoasc",
                        output_filename
                    ]
                except Exception as e:
                    st.error(f"無法取得金鑰：{e}")
                    ffmpeg_cmd = []
            else:
                st.info("未偵測到加密，直接合併影片...")
                ffmpeg_cmd = [
                    "ffmpeg",
                    "-allowed_extensions", "ALL",
                    "-i", m3u8_url,
                    "-c", "copy",
                    "-bsf:a", "aac_adtstoasc",
                    output_filename
                ]
            
            # Run ffmpeg if command is ready
            if ffmpeg_cmd:
                result = subprocess.run(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                if result.returncode == 0 and os.path.exists(output_filename):
                    st.success("影片已成功下載並合併！")
                    st.video(output_filename)
                    with open(output_filename, "rb") as f:
                        st.download_button("下載 MP4 檔案", f, file_name="video.mp4")
                else:
                    st.error("ffmpeg 合併失敗，請確認 m3u8 網址與金鑰是否正確。")
        except Exception as e:
            st.error(f"處理過程中發生錯誤：{e}")

