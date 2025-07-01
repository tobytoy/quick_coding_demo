import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase
import av
import cv2
import numpy as np
import face_recognition
from scipy.signal import detrend
from scipy.fftpack import fft
import datetime
import os
import time

st.title("非接觸式心率偵測應用程式")

BUFFER_SECONDS = 10
FRAME_RATE = 20
BUFFER_SIZE = BUFFER_SECONDS * FRAME_RATE

class HeartRateProcessor(VideoProcessorBase):
    def __init__(self):
        self.rgb_buffers = {}
        self.last_bpm = {}
        self.timestamps = {}

    def recv(self, frame: av.VideoFrame) -> av.VideoFrame:
        img = frame.to_ndarray(format="bgr24")
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_img)

        for i, face_location in enumerate(face_locations):
            top, right, bottom, left = face_location
            forehead_top = top
            forehead_bottom = top + (bottom - top) // 5
            forehead_left = left + (right - left) // 4
            forehead_right = right - (right - left) // 4
            forehead_roi = rgb_img[forehead_top:forehead_bottom, forehead_left:forehead_right]

            if forehead_roi.size == 0:
                continue

            mean_rgb = np.mean(forehead_roi, axis=(0, 1))
            face_id = f"{top}_{right}_{bottom}_{left}"

            if face_id not in self.rgb_buffers:
                self.rgb_buffers[face_id] = []
                self.timestamps[face_id] = []

            self.rgb_buffers[face_id].append(mean_rgb)
            self.timestamps[face_id].append(time.time())

            if len(self.rgb_buffers[face_id]) >= BUFFER_SIZE:
                bpm = self.estimate_heart_rate(self.rgb_buffers[face_id], self.timestamps[face_id])
                self.last_bpm[face_id] = bpm
                self.rgb_buffers[face_id] = []
                self.timestamps[face_id] = []

            if face_id in self.last_bpm:
                cv2.putText(img, f"HR: {int(self.last_bpm[face_id])} BPM", (left, top - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        return av.VideoFrame.from_ndarray(img, format="bgr24")

    def estimate_heart_rate(self, rgb_buffer, timestamps):
        green_signal = np.array([rgb[1] for rgb in rgb_buffer])
        green_signal = detrend(green_signal)
        duration = timestamps[-1] - timestamps[0]
        freqs = np.fft.fftfreq(len(green_signal), d=duration / len(green_signal))
        fft_values = np.abs(fft(green_signal))
        valid_idx = np.where((freqs >= 0.75) & (freqs <= 3.0))
        valid_freqs = freqs[valid_idx]
        valid_fft = fft_values[valid_idx]

        if len(valid_fft) == 0:
            return 0

        peak_freq = valid_freqs[np.argmax(valid_fft)]
        bpm = peak_freq * 60
        return bpm

ctx = webrtc_streamer(key="heart_rate", video_processor_factory=HeartRateProcessor)
st.markdown("請保持臉部穩定並面向攝影機約 10 秒以估算心率。")
