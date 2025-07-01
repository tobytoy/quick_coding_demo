import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase
import av
import cv2
import datetime
import os

st.title("攝影機拍照應用程式")

# 建立影像處理類別
class SnapshotProcessor(VideoProcessorBase):
    def __init__(self):
        self.frame = None

    def recv(self, frame: av.VideoFrame) -> av.VideoFrame:
        img = frame.to_ndarray(format="bgr24")
        self.frame = img
        return av.VideoFrame.from_ndarray(img, format="bgr24")

# 啟動 WebRTC 串流，使用 video_processor_factory（非舊版）
ctx = webrtc_streamer(key="snapshot", video_processor_factory=SnapshotProcessor)

# 拍照按鈕
if ctx.video_processor and st.button("📸 拍照並存檔"):
    snapshot = ctx.video_processor.frame
    if snapshot is not None:
        os.makedirs("snapshots", exist_ok=True)
        filename = datetime.datetime.now().strftime("snapshots/snapshot_%Y%m%d_%H%M%S.jpg")
        cv2.imwrite(filename, snapshot)
        st.success(f"已儲存影像：{filename}")
    else:
        st.warning("尚未擷取到影像，請稍後再試。")
