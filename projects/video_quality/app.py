import streamlit as st
import cv2
import tempfile
import os
from imquality import brisque
from PIL import Image
import numpy as np
import pandas as pd

# Streamlit UI
st.title("🎥 Video Quality Assessment (No-Reference - BRISQUE)")
st.write("Upload a video file to evaluate its visual quality using BRISQUE score.")

# Upload video
uploaded_video = st.file_uploader("Upload a video", type=["mp4", "avi", "mov"])

if uploaded_video:
    # Save uploaded video to a temporary file
    temp_video_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    temp_video_file.write(uploaded_video.read())
    temp_video_file.close()

    # Open video using OpenCV
    cap = cv2.VideoCapture(temp_video_file.name)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    st.write(f"Total frames in video: {frame_count}")

    brisque_scores = []
    frame_interval = max(1, frame_count // 30)  # Sample up to 30 frames

    st.write("Calculating BRISQUE scores for sampled frames...")

    frame_index = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if frame_index % frame_interval == 0:
            # Convert frame to RGB and PIL Image
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(frame_rgb)

            # Resize image to reduce computation (optional)
            pil_image = pil_image.resize((512, 512))

            # Compute BRISQUE score
            score = brisque.score(pil_image)
            brisque_scores.append(score)

        frame_index += 1

    cap.release()
    os.remove(temp_video_file.name)

    # Display results
    if brisque_scores:
        avg_score = np.mean(brisque_scores)
        df = pd.DataFrame({
            "Frame Index": list(range(len(brisque_scores))),
            "BRISQUE Score": brisque_scores
        })

        st.write("📊 BRISQUE Scores for Sampled Frames")
        st.dataframe(df)

        st.write(f"📈 Average BRISQUE Score: **{avg_score:.2f}**")
    else:
        st.warning("No frames were processed. Please check the video file.")

