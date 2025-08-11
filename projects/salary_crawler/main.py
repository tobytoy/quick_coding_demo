import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time

# 1. 建立 salary 資料夾
save_dir = os.path.join(os.path.dirname(__file__), "salary")
os.makedirs(save_dir, exist_ok=True)

# 2. 設定 Chrome 選項（Codespaces/Colab 需要這些參數）
chrome_options = Options()
chrome_options.add_argument("--headless=new")  # 無頭模式
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--window-size=1920,1080")

# 3. 啟動 WebDriver（自動下載 & 設定 ChromeDriver）
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    # 4. 前往目標網頁（這裡用 Google 當例子，你換成你的目標網址）
    url = "https://www.google.com"
    driver.get(url)
    time.sleep(2)  # 等待頁面加載

    # 5. 截圖存檔
    img_path = os.path.join(save_dir, "screenshot.png")
    driver.save_screenshot(img_path)
    print(f"圖片已儲存到: {img_path}")

finally:
    driver.quit()
