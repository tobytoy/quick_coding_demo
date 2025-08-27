import os
import whisper
import tempfile
import streamlit as st
from dotenv import load_dotenv
from pyannote.audio import Pipeline

# Load Hugging Face token from .env file
load_dotenv()
HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN")

st.title("🎙️ 語音辨識與語者分離 Demo")
st.write("上傳一段語音檔案，我們將使用 Whisper 進行語音轉文字，並用 pyannote-audio 分離不同語者的發言。")

audio_file = st.file_uploader("請上傳語音檔案（支援 mp3, wav 等格式）", type=["mp3", "wav", "m4a"])

if audio_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_audio:
        tmp_audio.write(audio_file.read())
        tmp_audio_path = tmp_audio.name

    st.audio(tmp_audio_path, format='audio/wav')
    st.write("✅ 檔案已上傳，開始處理中...")

    # Whisper 語音轉文字
    st.write("🔍 使用 Whisper 進行語音轉文字...")
    whisper_model = whisper.load_model("base")
    transcription = whisper_model.transcribe(tmp_audio_path, language="zh")

    st.subheader("📝 Whisper 語音轉文字結果")
    st.text(transcription["text"])

    # pyannote 語者分離
    st.write("🔍 使用 pyannote-audio 進行語者分離...")
    pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization", use_auth_token=HUGGINGFACE_TOKEN)
    diarization = pipeline(tmp_audio_path)

    st.subheader("🧑‍🤝‍🧑 語者分離結果")
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        st.write(f"[{turn.start:.2f}s - {turn.end:.2f}s] 語者 {speaker}")

    st.subheader("📝 語者發言內容")
    segments = transcription["segments"]
    for segment in segments:
        start = segment["start"]
        end = segment["end"]
        text = segment["text"]
        speaker_label = "未知語者"
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            if start >= turn.start and end <= turn.end:
                speaker_label = speaker
                break
        st.write(f"[{start:.2f}s - {end:.2f}s] {speaker_label}：{text}")

    os.remove(tmp_audio_path)

