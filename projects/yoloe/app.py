import streamlit as st
from PIL import Image
import os
from ultralytics import YOLOE
import tempfile

# 模型選項
MODEL_OPTIONS = [
    "yoloe-v8s.pt",
    "yoloe-v8m.pt",
    "yoloe-v8l.pt",
    "yoloe-v8x.pt"
]

# Streamlit 設定
st.set_page_config(page_title="YOLOE 圖片辨識介面", layout="wide")
st.title("🧠 YOLOE 圖片辨識系統")

# 分頁選擇
page = st.sidebar.radio("選擇頁面", ["辨識介面", "辨識結果"])

if page == "辨識介面":
    st.subheader("1️⃣ 選擇 YOLOE 模型")
    selected_model = st.selectbox("請選擇模型：", MODEL_OPTIONS)

    st.subheader("2️⃣ 上傳要辨識的圖片")
    uploaded_image = st.file_uploader("請上傳圖片（JPG/PNG）", type=["jpg", "jpeg", "png"])

    st.subheader("3️⃣ 上傳圖片提示（優先使用）")
    visual_prompt = st.file_uploader("請上傳提示圖片（JPG/PNG）", type=["jpg", "jpeg", "png"], key="prompt")

    st.subheader("4️⃣ 輸入文字提示（次優先）")
    text_prompt = st.text_input("請輸入提示詞，例如：小精靈")

    if st.button("開始辨識"):
        if uploaded_image:
            with tempfile.TemporaryDirectory() as tmpdir:
                image_path = os.path.join(tmpdir, uploaded_image.name)
                with open(image_path, "wb") as f:
                    f.write(uploaded_image.read())

                model = YOLOE(selected_model)

                # 設定提示
                if visual_prompt:
                    prompt_path = os.path.join(tmpdir, visual_prompt.name)
                    with open(prompt_path, "wb") as f:
                        f.write(visual_prompt.read())
                    model.set_visual_prompt(prompt_path)
                    prompt_type = "圖片提示"
                elif text_prompt:
                    model.set_classes([text_prompt])
                    prompt_type = "文字提示"
                else:
                    prompt_type = "無提示（一般推理）"

                # 執行推理
                results = model(image_path)
                results[0].save(filename=os.path.join(tmpdir, "result.jpg"))

                # 顯示結果圖片
                result_image = Image.open(os.path.join(tmpdir, "result.jpg"))
                st.image(result_image, caption="辨識結果圖片", use_column_width=True)

                # 儲存結果到 session state
                st.session_state["result"] = {
                    "model": selected_model,
                    "prompt_type": prompt_type,
                    "text_prompt": text_prompt,
                    "image_name": uploaded_image.name,
                    "boxes": results[0].boxes.data.tolist()
                }
        else:
            st.error("請先上傳要辨識的圖片！")

elif page == "辨識結果":
    st.subheader("📄 辨識結果報告")
    result = st.session_state.get("result")
    if result:
        st.write(f"✅ 使用模型：{result['model']}")
        st.write(f"🔍 提示類型：{result['prompt_type']}")
        if result['text_prompt']:
            st.write(f"📝 文字提示：{result['text_prompt']}")
        st.write(f"🖼️ 圖片檔名：{result['image_name']}")

        st.write("📦 辨識框結果：")
        for i, box in enumerate(result["boxes"]):
            st.write(f"物件 {i+1}: {box}")
    else:
        st.warning("尚未執行辨識，請先到第一頁進行操作。")