import streamlit as st
import os
import json

# 設定頁面
st.set_page_config(page_title="小說閱讀器", layout="wide")

st.title("📖 小說閱讀器")

# 使用者自訂樣式
font_size = st.slider("字體大小", 12, 36, 18)
bg_color = st.color_picker("背景顏色", "#ffffff")
font_color = st.color_picker("字體顏色", "#000000")

# 套用樣式
st.markdown(f"""
    <style>
    .novel-content {{
        font-size: {font_size}px;
        background-color: {bg_color};
        color: {font_color};
        padding: 20px;
        border-radius: 10px;
    }}
    </style>
""", unsafe_allow_html=True)

# 讀取小說資料夾
novel_root = "novels"
if not os.path.exists(novel_root):
    st.warning("找不到 novels 資料夾")
    st.stop()

novels = os.listdir(novel_root)
selected_novel = st.selectbox("選擇小說", novels)

chapters = os.listdir(os.path.join(novel_root, selected_novel))
selected_chapter = st.selectbox("選擇章節", chapters)

sections = os.listdir(os.path.join(novel_root, selected_novel, selected_chapter))
selected_section = st.selectbox("選擇小節", sections)

# 顯示內容
file_path = os.path.join(novel_root, selected_novel, selected_chapter, selected_section)
try:
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        content = data.get("content", "")
        st.markdown(f'<div class="novel-content">{content}</div>', unsafe_allow_html=True)
except Exception as e:
    st.error(f"讀取失敗：{e}")
