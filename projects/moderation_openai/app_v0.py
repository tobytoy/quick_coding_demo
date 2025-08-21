import os
import cv2
import time
import base64
import requests
import numpy as np
from PIL import Image
import streamlit as st
from openai import OpenAI


client = OpenAI()


def is_image_url(url):
    image_extensions = [".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif"]
    return any(url.lower().endswith(ext) for ext in image_extensions)

def download_image(url, save_path="check_img"):
    response = requests.get(url)
    if response.status_code == 200:
        with open(save_path, "wb") as f:
            f.write(response.content)
        return save_path
    return None

def check_image_url(image_url):
    # Download image from URL
    response = requests.get(image_url)
    if response.status_code != 200:
        print("❌ 無法下載圖片，請確認 URL 是否正確")
        return

    # Get image content and convert to base64
    image_data = response.content
    encoded_image = base64.b64encode(image_data).decode("utf-8")

    # Determine image format from URL or response headers
    content_type = response.headers.get("Content-Type", "image/png")
    if "jpeg" in content_type:
        mime_type = "image/jpeg"
    elif "jpg" in content_type:
        mime_type = "image/jpeg"
    elif "png" in content_type:
        mime_type = "image/png"
    else:
        mime_type = "image/png"

    # Prepare input string for Moderation API
    input_string = f"data:{mime_type};base64,{encoded_image}"

    # Call Moderation API
    moderation_response = client.moderations.create(
        model="omni-moderation-latest",
        input=input_string
    )

    result = moderation_response.results[0]
    flagged = result.flagged
    categories = result.categories

    if flagged:
        print("⚠️ 圖片可能包含敏感內容：")
        for category, is_flagged in vars(categories).items():
            if is_flagged:
                print(f"- {category}")
    else:
        print("✅ 圖片安全")


def moderate_image(image_url):
    # with open(image_path, "rb") as image_file:
    #     encoded_image = base64.b64encode(image_file.read()).decode("utf-8")

    response = client.moderations.create(
        model="omni-moderation-latest",
        input=[
            # {"type": "text", "text": "...text to classify goes here..."},
            {
                "type": "image_url",
                "image_url": {
                    "url": image_url,
                }
            },
        ],
    )
    # time.sleep(1000)

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


import requests

def is_image_url(url):
    image_extensions = [".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif"]
    return any(url.lower().endswith(ext) for ext in image_extensions)

def download_image(url, save_path="check_img"):
    response = requests.get(url)
    if response.status_code == 200:
        with open(save_path, "wb") as f:
            f.write(response.content)
        return save_path
    return None

with tab1:
    image_url = st.text_input("Enter image URL:")
    if image_url:
        if is_image_url(image_url):
            downloaded_path = download_image(image_url, "check_img.png")
            if downloaded_path:
                st.image(downloaded_path, caption="Downloaded Image", use_column_width=True)
                flagged, categories = moderate_image(image_url)
                if flagged:
                    st.warning("⚠️ Image may contain sensitive content:")
                    for category, is_flagged in categories.items():
                        if is_flagged:
                            st.write(f"- {category}")
                else:
                    st.success("✅ Image is safe")
            else:
                st.error("Failed to download image.")
        else:
            st.error("URL does not appear to be an image.")

# with tab1:
#     image_url = st.text_input("Enter image url:")
#     if image_url:
#     if image_path and os.path.exists(image_path):
#         st.image(image_path, caption="Uploaded Image", use_container_width=True)
#         flagged, categories = moderate_image(image_path)
#         if flagged:
#             st.warning("⚠️ Image may contain sensitive content:")
#             for category, is_flagged in categories.items():
#                 if is_flagged:
#                     st.write(f"- {category}")
#         else:
#             st.success("✅ Image is safe")

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

