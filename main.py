import time
import requests
import re
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# 깃허브 설정(Secrets)에서 가져오기
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')
KEYWORDS = ["학점은행제", "운영일정", "안내"]
DB_FILE = "seen_notices.txt"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.get(url, params={"chat_id": CHAT_ID, "text": message})

def check_kmooc():
    # 이미 본 글 목록 불러오기 (파일이 없으면 빈 세트)
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            seen_titles = set(line.strip() for line in f.readlines())
    else:
        seen_titles = set()

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        driver.get("https://www.kmooc.kr/edubank/notice")
        time.sleep(5)
        titles = driver.find_elements(By.CSS_SELECTOR, "span.title a")
        
        for tag in titles:
            title_text = tag.text.strip()
            link_attr = tag.get_attribute("href")
            
            if title_text and title_text not in seen_titles:
                if any(kw in title_text for kw in KEYWORDS):
                    post_id = re.sub(r'[^0-9]', '', link_attr)
                    real_link = f"https://www.kmooc.kr/board_detail/edubank/notice/{post_id}"
                    msg = f"🆕 [K-MOOC 새 공지]\n📌 제목: {title_text}\n🔗 링크: {real_link}"
                    send_telegram(msg)
                
                # 메모장에 추가
                with open(DB_FILE, "a", encoding="utf-8") as f:
                    f.write(title_text + "\n")
    finally:
        driver.quit()

if __name__ == "__main__":
    check_kmooc()
