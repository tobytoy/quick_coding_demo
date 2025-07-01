import streamlit as st
import os
import json
import difflib

st.set_page_config(page_title="小說編輯器", layout="wide")
st.title("✍️ 小說編輯器")

novel_root = "novels"

def get_all_sections():
    sections = []
    for novel in os.listdir(novel_root):
        for chapter in os.listdir(os.path.join(novel_root, novel)):
            for section in os.listdir(os.path.join(novel_root, novel, chapter)):
                path = os.path.join(novel_root, novel, chapter, section)
                sections.append((novel, chapter, section, path))
    return sections

tab1, tab2, tab3 = st.tabs(["新增", "修改/刪除", "搜尋"])

with tab1:
    st.subheader("新增小說內容")
    novel_name = st.text_input("小說名")
    chapter_name = st.text_input("章節")
    section_name = st.text_input("小節檔名（例如 001.json）")
    content = st.text_area("內容（支援 Markdown）", height=300)

    if st.button("儲存"):
        path = os.path.join(novel_root, novel_name, chapter_name)
        os.makedirs(path, exist_ok=True)
        file_path = os.path.join(path, section_name)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump({"content": content}, f, ensure_ascii=False, indent=2)
        st.success("儲存成功")

with tab2:
    st.subheader("修改或刪除小說內容")
    sections = get_all_sections()
    options = [f"{n}/{c}/{s}" for n, c, s, _ in sections]
    selected = st.selectbox("選擇小節", options)
    selected_path = dict(zip(options, [p for _, _, _, p in sections]))[selected]

    with open(selected_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        content = data.get("content", "")

    new_content = st.text_area("編輯內容", value=content, height=300)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("更新"):
            with open(selected_path, "w", encoding="utf-8") as f:
                json.dump({"content": new_content}, f, ensure_ascii=False, indent=2)
            st.success("更新成功")
    with col2:
        if st.button("刪除"):
            os.remove(selected_path)
            st.warning("已刪除")

with tab3:
    st.subheader("搜尋小說內容")
    keyword = st.text_input("輸入關鍵字")
    if keyword:
        results = []
        for novel, chapter, section, path in get_all_sections():
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                content = data.get("content", "")
                if keyword in content or difflib.get_close_matches(keyword, [content]):
                    results.append((novel, chapter, section, content))

        st.write(f"找到 {len(results)} 筆結果")
        for n, c, s, text in results:
            st.markdown(f"### {n}/{c}/{s}")
            st.markdown(text)
