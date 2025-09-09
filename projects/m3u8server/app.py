# streamlit_flask_server.py

import streamlit as st
import subprocess
import os
import uuid
from pathlib import Path
import shutil
import threading
from flask import Flask, send_from_directory

# Constants
BASE_DIR = Path(__file__).parent.resolve()
STREAM_DIR = BASE_DIR / "stream_data"
KEY_DIR = STREAM_DIR / "keys"
PORT = 8000  # Flask port

# Ensure directories exist
os.makedirs(STREAM_DIR, exist_ok=True)
os.makedirs(KEY_DIR, exist_ok=True)

# Flask app to serve static files
flask_app = Flask(__name__)

@flask_app.route('/stream_data/<path:filename>')
def serve_stream_file(filename):
    return send_from_directory(STREAM_DIR, filename)

@flask_app.route('/stream_data/keys/<keyname>')
def serve_key(keyname):
    return send_from_directory(KEY_DIR, keyname)

def run_flask():
    flask_app.run(port=PORT)

# Start Flask in a separate thread
threading.Thread(target=run_flask, daemon=True).start()

# Streamlit UI
st.title("🎬 M3U8 HLS 產生器（加密與非加密）")
st.write("上傳影片，產生可串流的 m3u8 播放清單與段落檔案")

uploaded_file = st.file_uploader("請上傳影片檔案（如 mp4）", type=["mp4", "mov", "mkv"])

if uploaded_file:
    # Save uploaded file
    video_id = uuid.uuid4().hex
    input_path = STREAM_DIR / f"{video_id}.mp4"
    with open(input_path, "wb") as f:
        f.write(uploaded_file.read())

    # Create output folders
    plain_dir = STREAM_DIR / f"{video_id}_plain"
    encrypted_dir = STREAM_DIR / f"{video_id}_encrypted"
    os.makedirs(plain_dir, exist_ok=True)
    os.makedirs(encrypted_dir, exist_ok=True)

    # Generate plain m3u8
    plain_cmd = [
        "ffmpeg", "-i", str(input_path),
        "-c:v", "copy", "-c:a", "aac", "-f", "hls",
        "-hls_time", "5", "-hls_playlist_type", "vod",
        "-hls_segment_filename", str(plain_dir / "segment_%03d.ts"),
        str(plain_dir / "playlist.m3u8")
    ]
    subprocess.run(plain_cmd)

    # Generate encryption key
    key_path = KEY_DIR / f"{video_id}.key"
    key_uri = f"http://localhost:{PORT}/stream_data/keys/{video_id}.key"
    key_gen = os.urandom(16)
    key_hex = key_gen.hex()
    with open(key_path, "wb") as f:
        f.write(key_gen)

    keyinfo_path = STREAM_DIR / f"{video_id}.keyinfo"
    # with open(keyinfo_path, "w") as f:
    #     f.write(f"{key_path}\n{key_uri}\n{key_path}")    
    with open(keyinfo_path, "w") as f:
        f.write(f"{key_uri}\n{key_path}\n{key_gen}")


    # Generate encrypted m3u8
    encrypted_cmd = [
        "ffmpeg", "-i", str(input_path),
        "-c:v", "copy", "-c:a", "aac", "-f", "hls",
        "-hls_time", "5", "-hls_playlist_type", "vod",
        "-hls_key_info_file", str(keyinfo_path),
        "-hls_segment_filename", str(encrypted_dir / "segment_%03d.ts"),
        str(encrypted_dir / "playlist.m3u8")
    ]
    subprocess.run(encrypted_cmd)

    # Show URLs
    st.success("✅ 影片處理完成！以下是串流連結：")

    plain_url = f"http://localhost:{PORT}/stream_data/{video_id}_plain/playlist.m3u8"
    encrypted_url = f"http://localhost:{PORT}/stream_data/{video_id}_encrypted/playlist.m3u8"

    st.markdown(f"🔓 非加密版 M3U8：`{plain_url}`")
    st.markdown(f"🔐 加密版 M3U8：`{encrypted_url}`")
    st.markdown(f"🔑 金鑰 URI：`{key_uri}`")

    st.code(f"curl {key_uri}", language="bash")

