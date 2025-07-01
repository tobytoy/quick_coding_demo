import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase
import tensorflow as tf
import tensorflow_hub as hub
import numpy as np
import cv2
import av
import csv
import os
from datetime import datetime

st.title("MoveNet 人體姿勢偵測並儲存關節座標")

# 檢查是否有 GPU
gpus = tf.config.list_physical_devices('GPU')
device = "/GPU:0" if gpus else "/CPU:0"
st.write(f"目前使用設備：{device}")

# 載入 MoveNet 模型
with tf.device(device):
    movenet_model = hub.load("https://tfhub.dev/google/movenet/singlepose/lightning/4")
    movenet = movenet_model.signatures['serving_default']

# 建立 CSV 檔案與標題
csv_dir = "pose_data"
os.makedirs(csv_dir, exist_ok=True)
csv_path = os.path.join(csv_dir, "keypoints.csv")
if not os.path.exists(csv_path):
    with open(csv_path, mode='w', newline='') as f:
        writer = csv.writer(f)
        header = ["timestamp"]
        for i in range(17):
            header += [f"kp{i}_y", f"kp{i}_x", f"kp{i}_score"]
        writer.writerow(header)

# 畫出人體骨架
def draw_keypoints_and_edges(image, keypoints, confidence_threshold=0.3):
    height, width, _ = image.shape
    keypoints = keypoints[0, 0, :, :]

    edges = [
        (0, 1), (1, 3), (0, 2), (2, 4),
        (5, 7), (7, 9), (6, 8), (8, 10),
        (5, 6), (5, 11), (6, 12),
        (11, 12), (11, 13), (13, 15),
        (12, 14), (14, 16)
    ]

    for idx, kp in enumerate(keypoints):
        y, x, confidence = kp
        if confidence > confidence_threshold:
            cv2.circle(image, (int(x * width), int(y * height)), 4, (0, 255, 0), -1)

    for edge in edges:
        p1, p2 = edge
        y1, x1, c1 = keypoints[p1]
        y2, x2, c2 = keypoints[p2]
        if c1 > confidence_threshold and c2 > confidence_threshold:
            cv2.line(image,
                     (int(x1 * width), int(y1 * height)),
                     (int(x2 * width), int(y2 * height)),
                     (0, 255, 255), 2)

    return image

# 建立 VideoProcessor 類別
class PoseProcessor(VideoProcessorBase):
    def __init__(self):
        self.model = movenet

    def recv(self, frame: av.VideoFrame) -> av.VideoFrame:
        img = frame.to_ndarray(format="bgr24")
        input_image = tf.image.resize_with_pad(tf.expand_dims(img, axis=0), 192, 192)
        input_image = tf.cast(input_image, dtype=tf.int32)

        with tf.device(device):
            outputs = self.model(input_image)
        keypoints = outputs['output_0'].numpy()

        # 畫出骨架
        img = draw_keypoints_and_edges(img, keypoints)

        # 儲存關節座標到 CSV
        timestamp = datetime.now().isoformat()
        flat_keypoints = keypoints[0, 0, :, :].flatten().tolist()
        row = [timestamp] + flat_keypoints
        with open(csv_path, mode='a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(row)

        return av.VideoFrame.from_ndarray(img, format="bgr24")

# 啟動 WebRTC 串流
webrtc_streamer(key="pose", video_processor_factory=PoseProcessor)
