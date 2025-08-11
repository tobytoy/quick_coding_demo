import os
import json
import time
import random
import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager



# 建立 salary 資料夾（程式所在目錄）
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
salary_dir = os.path.join(BASE_DIR, "salary")
os.makedirs(salary_dir, exist_ok=True)


# 設定頁面配置
st.set_page_config(
    page_title="薪資比較爬蟲工具",
    page_icon="💰",
    layout="wide"
)

st.title("💰 薪資比較爬蟲工具")
st.markdown("---")

# 側邊欄設定
st.sidebar.header("設定")
sleep_min = st.sidebar.number_input("最小休息時間 (秒)", min_value=1, max_value=60, value=3)
sleep_max = st.sidebar.number_input("最大休息時間 (秒)", min_value=1, max_value=60, value=8)

if sleep_min > sleep_max:
    st.sidebar.error("最小休息時間不能大於最大休息時間")

# 主要內容區域
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📁 JSON 檔案上傳")
    uploaded_file = st.file_uploader("選擇 JSON 檔案", type=['json'])
    
    # 預設範例 JSON
    default_json = {
        "高考": {
            "1": 799820,
            "2": 816350,
            "3": 833025
        },
        "普考": {
            "1": 623065,
            "2": 634230,
            "3": 645250
        },
        "初考": {
            "1": 505760,
            "2": 513590,
            "3": 521420
        }
    }
    
    if uploaded_file is not None:
        try:
            json_data = json.load(uploaded_file)
            st.success("JSON 檔案載入成功！")
        except json.JSONDecodeError:
            st.error("JSON 檔案格式錯誤，請檢查檔案內容")
            json_data = default_json
    else:
        json_data = default_json
        st.info("使用預設範例資料")

with col2:
    st.header("✏️ JSON 內容編輯")
    json_text = st.text_area(
        "編輯 JSON 內容",
        value=json.dumps(json_data, ensure_ascii=False, indent=2),
        height=300
    )
    
    try:
        edited_json = json.loads(json_text)
        st.success("JSON 格式正確")
        json_data = edited_json
    except json.JSONDecodeError as e:
        st.error(f"JSON 格式錯誤: {str(e)}")

# 顯示解析後的資料結構
st.header("📊 資料預覽")
if json_data:
    total_items = 0
    for category, items in json_data.items():
        if isinstance(items, dict):
            total_items += len(items)
    
    st.info(f"總共將處理 {total_items} 筆薪資資料")
    
    # 顯示資料表格
    preview_data = []
    for category, items in json_data.items():
        if isinstance(items, dict):
            for key, salary in items.items():
                preview_data.append({
                    "類別": category,
                    "編號": key,
                    "年薪": f"{salary:,}",
                    "檔案名稱": f"{category}_{key}_{salary}.png"
                })
    
    if preview_data:
        st.dataframe(preview_data, use_container_width=True)

# 爬蟲功能
def setup_driver():
    """設定 Chrome WebDriver"""
    chrome_options = Options()
    chrome_options.binary_location = "/usr/bin/google-chrome"
    # chrome_options.add_argument("--headless")  # 無頭模式
    chrome_options.add_argument("--headless=new")

    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    # chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # service = Service(ChromeDriverManager().install())
    # driver = webdriver.Chrome(service=service, options=chrome_options)
    service = Service('./chromedriver')
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver


def scrape_salary_chart(driver, salary, category, key, progress_placeholder, status_placeholder):
    """爬取單筆薪資圖表"""
    try:
        # 導航到網站
        driver.get("https://earnings.dgbas.gov.tw/experience_sub_01.aspx")
        
        # 等待頁面載入
        wait = WebDriverWait(driver, 30)
        
        # 輸入薪資
        salary_input = wait.until(EC.presence_of_element_located((By.NAME, "ctl00$ContentPlaceHolder1$txtSalary")))
        salary_input.clear()
        salary_input.send_keys(str(salary))
        
        # 選擇比較對象 (全體受僱員工)
        compare_select = wait.until(EC.element_to_be_clickable((By.NAME, "ctl00$ContentPlaceHolder1$ddlCompare")))
        compare_select.click()
        
        # 選擇全體受僱員工選項 (value="0")
        from selenium.webdriver.support.ui import Select
        select_compare = Select(compare_select)
        select_compare.select_by_value("0")
        
        # 選擇資料年 (112年)
        year_select = wait.until(EC.element_to_be_clickable((By.NAME, "ctl00$ContentPlaceHolder1$ddlYear")))
        select_year = Select(year_select)
        select_year.select_by_value("112")
        
        # 點擊查詢按鈕
        query_button = wait.until(EC.element_to_be_clickable((By.NAME, "ctl00$ContentPlaceHolder1$btnQuery")))
        query_button.click()
        
        # 等待並處理可能出現的彈窗
        time.sleep(3)
        try:
            # 尋找並點擊確認按鈕 (如果彈窗存在)
            confirm_button = driver.find_element(By.XPATH, "//button[contains(text(), '確認')]")
            if confirm_button.is_displayed():
                confirm_button.click()
                time.sleep(2)
        except:
            pass  # 如果沒有彈窗就繼續
        
        # 等待圖表載入
        # time.sleep(3)
        wait.until(EC.visibility_of_element_located((By.ID, "ContentPlaceHolder1_divChart")))
        chart_element = driver.find_element(By.ID, "ContentPlaceHolder1_divChart")

        
        # 尋找圖表容器
        try:
            # 嘗試多種可能的圖表元素選擇器
            chart_selectors = [
                "div[id*='Chart']",
                "div[id*='chart']", 
                "canvas",
                "svg",
                ".chart-container",
                "#ContentPlaceHolder1_divChart"
            ]
            
            chart_element = None
            for selector in chart_selectors:
                try:
                    chart_element = driver.find_element(By.CSS_SELECTOR, selector)
                    if chart_element.is_displayed():
                        break
                except:
                    continue
            
            if chart_element is None:
                # 如果找不到特定圖表元素，截取整個頁面內容區域
                chart_element = driver.find_element(By.TAG_NAME, "body")
        
        except Exception as e:
            status_placeholder.warning(f"⚠️ 無法找到圖表元素，將截取整個頁面: {str(e)}")
            chart_element = driver.find_element(By.TAG_NAME, "body")
        
        # 建立 salary 資料夾
        # salary_dir = os.path.join(os.path.dirname(__file__), "salary")
        # if not os.path.exists(salary_dir):
        # os.makedirs(salary_dir, exist_ok=True)

        # 儲存截圖
        filename = f"{category}_{key}_{salary}.png"
        filepath = os.path.join(salary_dir, filename)
        chart_element.screenshot(filepath)
        
        print("元素位置:", chart_element.location)
        print("元素大小:", chart_element.size)


        status_placeholder.success(f"✅ 成功儲存: {filename}")
        return True
        
    except Exception as e:
        status_placeholder.error(f"❌ 處理 {category}_{key}_{salary} 時發生錯誤: {str(e)}")
        return False

# 開始爬蟲按鈕
st.header("🚀 開始爬蟲")
if st.button("開始執行爬蟲", type="primary", use_container_width=True):
    if not json_data:
        st.error("請先載入或編輯 JSON 資料")
    elif sleep_min > sleep_max:
        st.error("請修正休息時間設定")
    else:
        # 計算總數量
        total_items = 0
        for category, items in json_data.items():
            if isinstance(items, dict):
                total_items += len(items)
        
        if total_items == 0:
            st.error("沒有找到可處理的薪資資料")
        else:
            # 建立進度條和狀態顯示
            progress_bar = st.progress(0)
            status_placeholder = st.empty()
            progress_placeholder = st.empty()
            
            # 設定 WebDriver
            status_placeholder.info("🔧 正在設定瀏覽器...")
            driver = setup_driver()
            
            try:
                current_item = 0
                success_count = 0
                
                for category, items in json_data.items():
                    if isinstance(items, dict):
                        for key, salary in items.items():
                            current_item += 1
                            
                            # 更新進度
                            progress = current_item / total_items
                            progress_bar.progress(progress)
                            progress_placeholder.info(f"📊 進度: {current_item}/{total_items} ({progress*100:.1f}%)")
                            
                            # 執行爬蟲
                            status_placeholder.info(f"🔍 正在處理: {category}_{key}_{salary}")
                            
                            success = scrape_salary_chart(driver, salary, category, key, progress_placeholder, status_placeholder)
                            if success:
                                success_count += 1
                            
                            # 隨機休息
                            if current_item < total_items:  # 最後一筆不需要休息
                                sleep_time = random.randint(sleep_min, sleep_max)
                                status_placeholder.info(f"😴 休息 {sleep_time} 秒...")
                                time.sleep(sleep_time)
                
                # 完成
                progress_bar.progress(1.0)
                progress_placeholder.success(f"🎉 爬蟲完成！成功處理 {success_count}/{total_items} 筆資料")
                status_placeholder.success("✅ 所有圖片已儲存至 salary 資料夾")
                
            except Exception as e:
                st.error(f"爬蟲過程中發生錯誤: {str(e)}")
            finally:
                driver.quit()
                status_placeholder.info("🔧 瀏覽器已關閉")

# 檔案管理
st.header("📁 檔案管理")
salary_dir = os.path.join(os.path.dirname(__file__), "salary")
if os.path.exists(salary_dir):
    files = [f for f in os.listdir(salary_dir) if f.endswith('.png')]
    if files:
        st.success(f"salary 資料夾中有 {len(files)} 個圖片檔案")
        
        # 顯示檔案列表
        with st.expander("查看檔案列表"):
            for file in sorted(files):
                st.text(file)
    else:
        st.info("salary 資料夾是空的")
else:
    st.info("salary 資料夾尚未建立")

