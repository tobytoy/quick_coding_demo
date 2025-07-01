import streamlit as st
import os
import ffmpeg
import whisper
import cv2
import google.generativeai as genai
from skimage.metrics import structural_similarity as ssim
import numpy as np
import soundfile as sf
import noisereduce as nr
import tempfile
import time

# --- UI 設定 ---
st.set_page_config(page_title="影片 Hashtag 自動生成器", layout="wide")
st.title("影片 Hashtag 自動生成系統 (Gemini POC)")
st.markdown("一個基於多模態 AI 的概念驗證，從影片的聲音和畫面中自動提取並生成相關的 Hashtag。")

# 在側邊欄獲取 API Key
st.sidebar.header("設定")
api_key = st.sidebar.text_input("請輸入您的 Google Gemini API Key", type="password")

uploaded_file = st.file_uploader("請上傳您的影片檔案 (mp4, mov, avi)", type=["mp4", "mov", "avi"])

# --- 核心功能函式 ---

# 1. 音訊處理
def process_audio(video_path, temp_dir):
    """提取、降噪並辨識音訊"""
    st.info("🔊 音訊流程開始...")
    try:
        # 步驟 1: 提取音訊
        audio_path_raw = os.path.join(temp_dir, "raw_audio.wav")
        st.write("   - 正在提取音訊...")
        (
            ffmpeg.input(video_path)
            .output(audio_path_raw, acodec='pcm_s16le', ar='16000', ac=1)
            .run(overwrite_output=True, quiet=True)
        )

        # 步驟 2: 雜訊抑制
        st.write("   - 正在進行雜訊抑制...")
        rate, data = sf.read(audio_path_raw)

        # --- FIX START: 增加對音訊數據的穩健性檢查 ---
        if not isinstance(data, np.ndarray) or data.size == 0:
            st.warning("   - 偵測到空音訊或讀取失敗，跳過音訊處理。")
            st.success("🔊 音訊流程結束（無內容）。")
            return None
        # --- FIX END ---

        if data.ndim > 1:
            data = np.mean(data, axis=1) # 轉為單聲道
        
        # 僅在音訊夠長時才進行降噪
        if len(data) > rate: # 至少需要1秒的音訊
            reduced_noise_data = nr.reduce_noise(y=data, sr=rate)
        else:
            reduced_noise_data = data
        
        audio_path_processed = os.path.join(temp_dir, "processed_audio.wav")
        sf.write(audio_path_processed, reduced_noise_data, rate)

        # 步驟 3: 語音辨識 (Whisper)
        st.write("   - 正在進行語音辨識 (Whisper)...")
        model = whisper.load_model("tiny") 
        result = model.transcribe(audio_path_processed)
        transcript = result["text"]
        st.success("🔊 音訊流程完成！")
        return transcript
    except Exception as e:
        st.error(f"處理音訊時發生錯誤: {e}")
        return None

# 2. 視覺處理
def process_visuals(video_path, temp_dir):
    """提取關鍵畫面並用 Gemini Vision 理解"""
    st.info("🖼️ 視覺流程開始...")
    try:
        # 步驟 1: 擷取關鍵畫面
        st.write("   - 正在擷取關鍵畫面...")
        key_frames_paths = []
        cap = cv2.VideoCapture(video_path)
        prev_frame = None
        frame_count = 0
        
        frame_extraction_placeholder = st.empty()

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # 每秒取一幀進行比較
            fps = cap.get(cv2.CAP_PROP_FPS)
            if fps == 0: fps = 30 # 避免除以零
            
            if frame_count % int(fps) == 0:
                gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                gray_frame = cv2.resize(gray_frame, (128, 72)) # 縮小以加速 SSIM

                if prev_frame is not None:
                    similarity = ssim(prev_frame, gray_frame, data_range=gray_frame.max() - gray_frame.min())
                    if similarity < 0.9 or len(key_frames_paths) < 3: # 相似度低於閾值，或擷取數量少於3張時強制保存
                        frame_path = os.path.join(temp_dir, f"frame_{frame_count}.jpg")
                        cv2.imwrite(frame_path, frame)
                        key_frames_paths.append(frame_path)
                        frame_extraction_placeholder.write(f"      - 已擷取 {len(key_frames_paths)} 個關鍵畫面...")
                else: # 保存第一幀
                    frame_path = os.path.join(temp_dir, f"frame_{frame_count}.jpg")
                    cv2.imwrite(frame_path, frame)
                    key_frames_paths.append(frame_path)
                
                prev_frame = gray_frame
            frame_count += 1
            if len(key_frames_paths) >= 8: # 最多取8張關鍵畫面
                break
        
        cap.release()
        frame_extraction_placeholder.write(f"      - 共擷取 {len(key_frames_paths)} 個關鍵畫面。")

        if not key_frames_paths:
            st.warning("   - 未能擷取任何關鍵畫面。")
            st.success("🖼️ 視覺流程結束（無內容）。")
            return None

        # 步驟 2: 圖像理解
        st.write("   - 正在理解畫面內容 (Gemini)...")
        descriptions = []
        image_analysis_placeholder = st.empty()

        # --- FIX START: 更新 Gemini Vision 模型 ---
        vision_model = genai.GenerativeModel('gemini-1.5-flash-latest')
        # --- FIX END ---
        
        for i, frame_path in enumerate(key_frames_paths):
            image_analysis_placeholder.write(f"      - 正在分析第 {i+1}/{len(key_frames_paths)} 張畫面...")
            try:
                img = genai.upload_file(frame_path)
                response = vision_model.generate_content(["請簡要描述這張圖片中的主要物體、場景和氛圍。", img])
                descriptions.append(response.text)
                time.sleep(1) # 避免觸發 API 頻率限制
            except Exception as e:
                st.warning(f"分析畫面 {os.path.basename(frame_path)} 時發生錯誤: {e}")
        
        st.success("🖼️ 視覺流程完成！")
        return " ".join(descriptions)

    except Exception as e:
        st.error(f"處理視覺時發生錯誤: {e}")
        return None

# 3. LLM Hashtag 生成
def generate_hashtags(text_content, prompt_type):
    """使用 Gemini Pro 從文本生成 Hashtag"""
    if not text_content or text_content.strip() == "":
        return []
    
    st.info(f"✨ 正在從 {prompt_type} 內容生成 Hashtag...")
    try:
        # 使用 gemini-1.5-flash，因為它速度快且性能好
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        prompt = f"""
        你是一位社群媒體行銷專家。根據以下內容，生成 8 個最相關、最吸引人的繁體中文 Hashtag。
        請用空格分隔每個 Hashtag，不要包含 '#' 符號或其他多餘的文字。

        內容：
        ---
        {text_content}
        ---

        Hashtags:
        """
        response = model.generate_content(prompt)
        # 清理輸出，移除可能出現的markdown等符號
        cleaned_text = response.text.replace("*", "").replace("#", "").strip()
        hashtags = [tag.strip() for tag in cleaned_text.split()]
        st.success(f"✨ {prompt_type} Hashtag 已生成！")
        return hashtags
    except Exception as e:
        st.error(f"生成 Hashtag 時發生錯誤: {e}")
        return []

# --- 主執行流程 ---
if st.button("🚀 開始生成 Hashtag", disabled=(not uploaded_file or not api_key)):
    try:
        genai.configure(api_key=api_key)
        # 創建一個臨時目錄來存放所有中間檔案
        with tempfile.TemporaryDirectory() as temp_dir:
            # 保存上傳的影片
            video_path = os.path.join(temp_dir, uploaded_file.name)
            with open(video_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            with st.spinner("正在處理中，請稍候...這可能需要幾分鐘時間。"):
                # 執行音訊和視覺流程
                transcript = process_audio(video_path, temp_dir)
                visual_descriptions = process_visuals(video_path, temp_dir)

                # 生成 Hashtags
                audio_hashtags = []
                if transcript and transcript.strip():
                    st.subheader("📝 語音辨識逐字稿")
                    st.text_area("Transcript", transcript, height=150)
                    audio_hashtags = generate_hashtags(transcript, "語音")
                
                visual_hashtags = []
                if visual_descriptions and visual_descriptions.strip():
                    st.subheader("🎨 關鍵畫面描述")
                    st.text_area("Visuals Description", visual_descriptions, height=150)
                    visual_hashtags = generate_hashtags(visual_descriptions, "視覺")
                
                # 合併與去重
                final_hashtags = sorted(list(set(audio_hashtags + visual_hashtags)))

                # 顯示最終結果
                st.subheader("🎉 最終 Hashtag 推薦")
                if final_hashtags:
                    # 以標籤形式顯示
                    tags_html = "".join([f"<span style='background-color: #1E90FF; color: white; padding: 5px 10px; border-radius: 15px; margin: 5px; display: inline-block;'>#{tag}</span>" for tag in final_hashtags])
                    st.markdown(tags_html, unsafe_allow_html=True)
                    
                    # 提供一個可複製的純文字版本
                    st.text_area("複製 Hashtags", " ".join([f"#{tag}" for tag in final_hashtags]))
                else:
                    st.warning("無法生成任何 Hashtag。可能是影片內容不足或在處理過程中發生錯誤。")

    except Exception as e:
        st.error(f"發生未知錯誤: {e}")
        st.exception(e) # 顯示詳細的錯誤追蹤

# 說明
st.sidebar.markdown("---")
st.sidebar.markdown("### 使用說明")
st.sidebar.markdown("""
1.  在上方輸入您的 Google Gemini API Key。
2.  點擊上傳按鈕，選擇一個影片檔案。
3.  點擊「開始生成 Hashtag」按鈕。
4.  系統將會處理影片並在主畫面顯示結果。
""")

st.sidebar.markdown("### 必要條件")
st.sidebar.markdown("""
- **FFmpeg**: 您的系統必須安裝 FFmpeg。請參考 [FFmpeg 官網](https://ffmpeg.org/download.html) 進行安裝。
""")




