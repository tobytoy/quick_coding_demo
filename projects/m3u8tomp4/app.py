import streamlit as st
import subprocess
import os
import uuid

# Streamlit UI
st.title("🎬 M3U8 to MP4 Downloader")
st.write("輸入一個 m3u8 網址，下載並合併為一個 MP4 檔案")

# User input
m3u8_url = st.text_input("請輸入 m3u8 網址")

# Download and convert
if m3u8_url:
    # Generate unique filename
    output_filename = f"{uuid.uuid4().hex}.mp4"

    # Run ffmpeg command
    with st.spinner("正在下載並合併影片，請稍候..."):
        result = subprocess.run(
            ["ffmpeg", "-i", m3u8_url, "-c", "copy", "-bsf:a", "aac_adtstoasc", output_filename],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

    # Check result
    if result.returncode == 0 and os.path.exists(output_filename):
        st.success("影片已成功下載並合併！")

        # Display video preview
        st.video(output_filename)

        # Provide download button
        with open(output_filename, "rb") as f:
            st.download_button("下載 MP4 檔案", f, file_name="video.mp4")
    else:
        st.error("下載或合併失敗，請確認 m3u8 網址是否正確，或檢查 ffmpeg 是否已安裝。")


