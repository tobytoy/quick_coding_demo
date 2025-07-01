import streamlit as st
import json
import feedparser
import os

# Path to the RSS JSON file
RSS_JSON_PATH = "rss_sources.json"

# Load RSS sources from JSON file
def load_rss_sources():
    if os.path.exists(RSS_JSON_PATH):
        with open(RSS_JSON_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# Save RSS sources to JSON file
def save_rss_sources(sources):
    with open(RSS_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(sources, f, indent=2, ensure_ascii=False)

# Page 1: Manage RSS Sources
def page_manage_sources():
    st.header("📁 管理 RSS 資源")

    sources = load_rss_sources()

    st.subheader("目前的 RSS 資源")
    for i, source in enumerate(sources):
        st.markdown(f"**{source['name']}** - {source['category']}<br>{source['url']}", unsafe_allow_html=True)

    st.subheader("➕ 新增 RSS 資源")
    with st.form("add_rss_form"):
        name = st.text_input("名稱")
        url = st.text_input("RSS 連結")
        category = st.text_input("分類")
        submitted = st.form_submit_button("新增")
        if submitted and name and url and category:
            sources.append({"name": name, "url": url, "category": category})
            save_rss_sources(sources)
            st.success("已新增 RSS 資源！")
            st.experimental_rerun()

    st.subheader("🗑️ 刪除 RSS 資源")
    delete_options = [f"{s['name']} ({s['category']})" for s in sources]
    selected = st.selectbox("選擇要刪除的資源", delete_options)
    if st.button("刪除"):
        index = delete_options.index(selected)
        sources.pop(index)
        save_rss_sources(sources)
        st.success("已刪除 RSS 資源！")
        st.experimental_rerun()

# Page 2: View and Filter RSS Feed
def page_view_feed():
    st.header("🔍 查看 RSS 內容")

    sources = load_rss_sources()
    if not sources:
        st.warning("尚未設定任何 RSS 資源。請先到第一頁新增。")
        return

    selected_name = st.selectbox("選擇 RSS 資源", [s["name"] for s in sources])
    selected_source = next(s for s in sources if s["name"] == selected_name)

    st.write(f"來源：{selected_source['url']}")
    feed = feedparser.parse(selected_source["url"])

    keyword = st.text_input("🔎 關鍵字過濾")

    for entry in feed.entries:
        title = entry.get("title", "")
        summary = entry.get("summary", "")
        link = entry.get("link", "")
        if keyword.lower() in title.lower() or keyword.lower() in summary.lower():
            st.markdown(f"### {title}")
            st.write(summary)

# Streamlit multi-page setup
st.sidebar.title("📚 RSS 工具")
page = st.sidebar.radio("選擇頁面", ["管理 RSS 資源", "查看 RSS 內容"])

if page == "管理 RSS 資源":
    page_manage_sources()
else:
    page_view_feed()




