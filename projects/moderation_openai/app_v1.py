import streamlit as st
from yt_dlp import YoutubeDL
from openai import OpenAI
import cv2
import os
import tempfile
import base64
import io
from PIL import Image

# 初始化 OpenAI client（請先設定環境變數 OPENAI_API_KEY）
client = OpenAI()

st.title("🎞️ YouTube 單張畫面內容分級 (Moderation) Demo")
st.caption("輸入 YouTube URL + 指定偵號（0 起算）。若超出範圍，會提示最大可用偵號。影像會送到 OpenAI `omni-moderation-latest` 進行圖片審核。")

# --- 使用者輸入 ---
yt_url = st.text_input("請輸入 YouTube 影片 URL")
frame_idx = st.number_input("要分析的偵號（0-based）", min_value=0, step=1, value=0, help="偵號從 0 開始，最大值為 總偵數-1")

run = st.button("擷取並審核該偵")

if run:
    if not yt_url.strip():
        st.error("請先輸入 YouTube 影片 URL")
        st.stop()

    # 下載影片（取較低畫質以加速）
    with st.spinner("正在下載影片（低畫質以加速）…"):
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                ydl_opts = {
                    "format": "mp4[height<=360]/mp4[height<=480]/best[ext=mp4]/best",
                    "outtmpl": os.path.join(tmpdir, "%(id)s.%(ext)s"),
                    "quiet": True,
                    "nocheckcertificate": True,
                }
                with YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(yt_url, download=True)
                    video_path = ydl.prepare_filename(info)

                # 讀取影片資訊
                cap = cv2.VideoCapture(video_path)
                if not cap.isOpened():
                    st.error("無法開啟影片檔。")
                    st.stop()

                frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                fps = float(cap.get(cv2.CAP_PROP_FPS) or 0.0)
                duration = (frame_count / fps) if fps > 0 else None

                st.info(
                    f"偵數：{frame_count}，FPS：{fps:.2f}" + (f"，長度：約 {duration:.2f} 秒" if duration else "")
                )

                if frame_count <= 0:
                    st.error("無法取得影片偵數，可能是影片格式不支援或下載失敗。")
                    st.stop()

                max_idx = frame_count - 1
                req_idx = int(frame_idx)

                if req_idx < 0 or req_idx > max_idx:
                    st.error(f"偵號超出範圍：你輸入 {req_idx}，允許 0 ~ {max_idx}（最大能在第 {max_idx} 偵）。")
                    st.stop()

                # 跳到指定偵並擷取
                cap.set(cv2.CAP_PROP_POS_FRAMES, req_idx)
                ok, frame = cap.read()
                cap.release()

                if not ok or frame is None:
                    st.error("讀取該偵失敗。")
                    st.stop()

                # BGR -> RGB，顯示畫面
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                timestamp = (req_idx / fps) if fps > 0 else None
                st.image(
                    frame_rgb,
                    caption=(f"第 {req_idx} 偵（約 {timestamp:.2f} 秒）" if timestamp is not None else f"第 {req_idx} 偵"),
                    use_column_width=True,
                )

                # 轉成 PNG 並以 data URL 傳給 Moderation API
                pil_img = Image.fromarray(frame_rgb)
                buf = io.BytesIO()
                pil_img.save(buf, format="PNG")
                png_bytes = buf.getvalue()
                data_url = "data:image/png;base64," + base64.b64encode(png_bytes).decode("utf-8")

                with st.spinner("送至 OpenAI Moderation 進行影像審核…"):
                    mod = client.moderations.create(
                        model="omni-moderation-latest",
                        input=[
                            {
                                "type": "image_url",
                                "image_url": {"url": data_url},
                            }
                        ],
                    )

                # 顯示結果
                st.subheader("🔍 Moderation 分析結果")
                try:
                    res = mod.results[0]
                except Exception:
                    res = mod["results"][0] if isinstance(mod, dict) else mod
                st.json(res)

                # 友善摘要（依分數排列）
                try:
                    categories = getattr(res, "categories", None) or res.get("categories", {})
                    scores = getattr(res, "category_scores", None) or res.get("category_scores", {})
                    ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
                    if ranked:
                        st.markdown("**Top 類別分數：**")
                        for k, v in ranked[:8]:
                            flagged = categories.get(k, False)
                            bullet = "⚠️" if flagged else "•"
                            st.write(f"{bullet} {k}: {v:.3f}")
                except Exception:
                    pass

        except Exception as e:
            st.error(f"處理失敗：{e}")

st.divider()
st.caption("⚠️ 僅供教學示範。下載/處理 YouTube 影片請遵守該平台的服務條款與著作權規範。OpenAI Moderation 模型支援影像與文字輸入（`omni-moderation-latest`）。")
