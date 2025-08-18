import streamlit as st
import base64
import cv2
import os
from openai import OpenAI
from PIL import Image
import numpy as np

client = OpenAI()

def moderate_image(image_path):
    with open(image_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode("utf-8")

    response = client.moderations.create(
        model="omni-moderation-latest",
        input="data:image/png;base64," + encoded_image
    )
    time.sleep(1000)

    result = response.results[0]
    flagged = result.flagged
    categories = result.categories

    return flagged, vars(categories)

def extract_video_info(video_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return None

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frame_count / fps if fps else 0

    cap.release()
    return width, height, fps, duration, frame_count

def extract_frames(video_path, frame_indices):
    cap = cv2.VideoCapture(video_path)
    frames = []
    for idx in frame_indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, frame = cap.read()
        if ret:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frames.append((idx, Image.fromarray(frame_rgb)))
    cap.release()
    return frames

st.title("OpenAI Moderation Tool")

tab1, tab2 = st.tabs(["Image Moderation", "Video Frame Analysis"])

with tab1:
    image_path = st.text_input("Enter image path:")
    if image_path and os.path.exists(image_path):
        st.image(image_path, caption="Uploaded Image", use_container_width=True)
        flagged, categories = moderate_image(image_path)
        if flagged:
            st.warning("⚠️ Image may contain sensitive content:")
            for category, is_flagged in categories.items():
                if is_flagged:
                    st.write(f"- {category}")
        else:
            st.success("✅ Image is safe")

with tab2:
    video_path = st.text_input("Enter video path:")
    if video_path and os.path.exists(video_path):
        info = extract_video_info(video_path)
        if info:
            width, height, fps, duration, frame_count = info
            st.write(f"Resolution: {width}x{height}")
            st.write(f"FPS: {fps}")
            st.write(f"Duration: {duration:.2f} seconds")
            st.write(f"Total Frames: {frame_count}")

            frame_input = st.text_input("Enter frame indices to analyze (comma-separated):")
            if frame_input:
                try:
                    frame_indices = [int(x.strip()) for x in frame_input.split(",")]
                    frames = extract_frames(video_path, frame_indices)
                    for idx, frame_img in frames:
                        st.image(frame_img, caption=f"Frame {idx}", use_container_width=True)
                        # Save frame temporarily to analyze
                        temp_path = f"temp_frame_{idx}.png"
                        frame_img.save(temp_path)
                        flagged, categories = moderate_image(temp_path)
                        os.remove(temp_path)
                        if flagged:
                            st.warning(f"⚠️ Frame {idx} may contain sensitive content:")
                            for category, is_flagged in categories.items():
                                if is_flagged:
                                    st.write(f"- {category}")
                        else:
                            st.success(f"✅ Frame {idx} is safe")
                except ValueError:
                    st.error("Invalid frame indices. Please enter comma-separated integers.")

