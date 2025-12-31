import streamlit as st
import requests
from bs4 import BeautifulSoup
import random
from deep_translator import GoogleTranslator # ⭐️ 匯入翻譯工具

#設定網頁
st.set_page_config(page_title="名人名言產生器", page_icon="✨")

#名人清單與網址
PEOPLE = {
    "Steve Jobs (蘋果創辦人)": "https://en.wikiquote.org/wiki/Steve_Jobs",
    "Elon Musk (特斯拉執行長)": "https://en.wikiquote.org/wiki/Elon_Musk",
    "Taylor Swift (流行樂天后)": "https://en.wikiquote.org/wiki/Taylor_Swift",
    "Bill Gates (微軟創辦人)": "https://en.wikiquote.org/wiki/Bill_Gates"
}

#爬蟲
import re

@st.cache_data
def get_quotes(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        content_div = soup.find('div', class_='mw-parser-output')
        quote_list = []
        
        #擴張排除關鍵字清單
        exclude_keywords = [
            "Introduction", "Speech at", "Interview", "Press release", 
            "At the", "On the", "Quoted in", "ISBN", "p. ", "pp. ", 
            "edition", "published", "Source:", "attributed"
        ]
        
        if content_div:
            #找到所有的列表項目
            for item in content_div.find_all('li'):
                text = item.get_text().strip()
                
                #多重過濾邏輯
                #長度必須大於 40 (過短的通常是標題或名字)
                #不能以排除關鍵字開頭 (不分大小寫)
                #不能包含 ISBN (這通常是書本資訊)
                #不能包含 " (19" 或 " (20" (這通常是年份標註)
                
                lower_text = text.lower()
                is_background = any(lower_text.startswith(kw.lower()) for kw in exclude_keywords)
                has_isbn = "isbn" in lower_text
                
                if len(text) > 40 and not is_background and not has_isbn:
                    
                    #清理掉括號內容與雜訊
                    # 移除 [1], [specific citation needed]
                    clean_text = re.sub(r'\[.*?\]', '', text)
                    #移除 (19xx) 或 (20xx) 年份標記
                    clean_text = re.sub(r'\(\d{4}\)', '', clean_text)
                    
                    #只取第一行 (維基語錄有時會在第二行寫出處)
                    clean_text = clean_text.split('\n')[0].strip()
                    
                    #清掉雜訊後太短，或是以 "by " 開頭 (作者資訊)，就不要
                    if len(clean_text) > 35 and not clean_text.lower().startswith("by "):
                        quote_list.append(clean_text)
                            
        return list(set(quote_list)) #使用 set 去除重複的名言
    except:
        return ["目前無法取得資料，請稍後再試。"]

#網頁介面
st.title("🌟 名人名言隨機產生器 (內建翻譯)")
st.write("獲取啟發性語錄，並自動對應中文翻譯。")

with st.sidebar:
    st.header("⚙️ 設定")
    selected_name = st.selectbox("請選擇一位名人：", list(PEOPLE.keys()))

target_url = PEOPLE[selected_name]
with st.spinner(f'正在獲取 {selected_name} 的語錄...'):
    quotes = get_quotes(target_url)

#初始化 Session State
if 'last_person' not in st.session_state or st.session_state.last_person != selected_name:
    st.session_state.last_person = selected_name
    st.session_state.display_quote = f"已載入 {len(quotes)} 則語錄。點擊按鈕開始！"
    st.session_state.translated_quote = ""

st.divider()

#互動按鈕
if st.button(f'🎲 隨機產生並翻譯', type="primary"):
    #隨機選一句英文
    chosen_quote = random.choice(quotes)
    st.session_state.display_quote = chosen_quote
    
    #進行翻譯
    with st.spinner('正在進行 AI 翻譯...'):
        try:
            translation = GoogleTranslator(source='en', target='zh-TW').translate(chosen_quote)
            st.session_state.translated_quote = translation
        except:
            st.session_state.translated_quote = "翻譯失敗，請再試一次。"

#顯示結果
st.subheader("💡 Original Quote (英文原文):")
st.info(f"“ {st.session_state.display_quote} ”")

#翻譯區塊
if st.session_state.translated_quote:
    st.subheader("🏮 Chinese Translation (中文翻譯):")
    st.success(f"“ {st.session_state.translated_quote} ”")

#底部資訊欄
st.write("")
st.divider()
st.caption(f"資料來源：Wikiquote ({selected_name}) | 翻譯引擎：Google Translate")
st.caption("👥 Python 第I組")