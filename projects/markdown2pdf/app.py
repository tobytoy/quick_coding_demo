import streamlit as st
from fpdf import FPDF
import os
import urllib.request
import textwrap

# 字型設定
FONT_PATH = "NotoSans-Regular.ttf"
FONT_URL = "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSans/NotoSans-Regular.ttf"

# 自動下載字型（若尚未存在）
if not os.path.exists(FONT_PATH):
    urllib.request.urlretrieve(FONT_URL, FONT_PATH)

# PDF 類別
class PDF(FPDF):
    def __init__(self):
        super().__init__()
        self.add_page()
        self.add_font("NotoSans", "", FONT_PATH, uni=True)
        self.set_font("NotoSans", size=12)

    def add_text(self, text):
        lines = text.split('\n')
        for line in lines:
            # 強制斷行，處理無空白長字串
            try:
                wrapped_lines = textwrap.wrap(line, width=90, break_long_words=True, break_on_hyphens=False)
                if not wrapped_lines:
                    self.multi_cell(0, 10, "")
                for wrapped_line in wrapped_lines:
                    self.multi_cell(0, 10, wrapped_line)
            except Exception:
                self.multi_cell(0, 10, "[Skipped line due to rendering error]")

# Markdown 轉 PDF 函式（直接處理純文字）
def convert_md_to_pdf(md_content, output_path):
    pdf = PDF()
    pdf.add_text(md_content)
    pdf.output(output_path)


# Streamlit UI
st.title("Markdown to PDF Converter（支援中英文）")

uploaded_file = st.file_uploader("請上傳 Markdown (.md) 檔案", type=["md"])

if uploaded_file is not None:
    md_content = uploaded_file.read().decode("utf-8")
    st.text_area("Markdown 內容預覽", md_content, height=300)

    if st.button("轉換為 PDF"):
        output_filename = os.path.splitext(uploaded_file.name)[0] + ".pdf"
        convert_md_to_pdf(md_content, output_filename)
        with open(output_filename, "rb") as f:
            st.download_button("下載 PDF", f, file_name=output_filename)
        os.remove(output_filename)
