# tarot_poc.py

import streamlit as st
import random
import google.generativeai as genai

# --- 1. 資料與類別定義 (根據報告) ---

# 偉特塔羅牌資料 (為了簡潔，這裡僅列出部分牌義，實際應用可擴充)
TAROT_CARDS_DATA = {
    # 大阿爾克那
    "愚者 (The Fool)": ("開始、天真、自由、未知", "魯莽、冒險、天真過頭"),
    "魔術師 (The Magician)": ("意志力、創造、顯化、能力", "欺騙、操縱、潛力未發揮"),
    "女祭司 (The High Priestess)": ("直覺、潛意識、秘密、智慧", "秘密被揭露、直覺被蒙蔽"),
    "皇后 (The Empress)": ("豐盛、母性、創造力、滋養", "停滯、依賴、創造力受阻"),
    "皇帝 (The Emperor)": ("權威、結構、父親、掌控", "專制、僵化、失控"),
    "教皇 (The Hierophant)": ("傳統、信仰、團體、指導", "打破常規、固執、虛偽"),
    "戀人 (The Lovers)": ("愛、結合、選擇、關係", "錯誤的選擇、失衡、衝突"),
    "戰車 (The Chariot)": ("勝利、意志、前進、征服", "失控、方向錯誤、自大"),
    "力量 (Strength)": ("內在力量、勇氣、同情、耐心", "軟弱、自我懷疑、失控"),
    "隱者 (The Hermit)": ("內省、尋求真理、獨處、指引", "孤立、迷失、退縮"),
    "命運之輪 (Wheel of Fortune)": ("命運、轉變、機會、循環", "厄運、抗拒改變、停滯"),
    "正義 (Justice)": ("公平、真理、因果、法律", "不公、偏見、逃避責任"),
    "倒吊人 (The Hanged Man)": ("犧牲、新視角、等待、順從", "無謂的犧牲、停滯不前"),
    "死神 (Death)": ("結束、轉變、重生、放手", "抗拒改變、痛苦的結束"),
    "節制 (Temperance)": ("平衡、和諧、耐心、整合", "失衡、極端、衝突"),
    "惡魔 (The Devil)": ("束縛、誘惑、物質主義、成癮", "掙脫束縛、自由、覺醒"),
    "高塔 (The Tower)": ("突變、災難、覺醒、揭示真相", "抗拒災難、恐懼改變"),
    "星星 (The Star)": ("希望、靈感、平靜、治癒", "絕望、幻想、失落"),
    "月亮 (The Moon)": ("幻象、恐懼、潛意識、不安", "真相大白、釋放恐懼"),
    "太陽 (The Sun)": ("喜悅、成功、活力、清晰", "過度樂觀、短暫的快樂"),
    "審判 (Judgement)": ("重生、內在召喚、寬恕、清算", "自我懷疑、逃避評判"),
    "世界 (The World)": ("完成、整合、成就、旅行", "未完成、停滯、不圓滿"),
    # 小阿爾克那 (權杖、聖杯、寶劍、錢幣) - 這裡僅列出代表
    "權杖首牌 (Ace of Wands)": ("新機會、創造力、靈感", "延遲、缺乏動力"),
    "權杖侍從 (Page of Wands)": ("熱情、探索、信使", "壞消息、猶豫不決"),
    "權杖騎士 (Knight of Wands)": ("行動、冒險、衝動", "魯莽、挫折、拖延"),
    "權杖皇后 (Queen of Wands)": ("自信、熱情、領導力", "嫉妒、專橫、不安全感"),
    "權杖國王 (King of Wands)": ("遠見、領導、創造者", "專制、無情、期望過高"),
    "聖杯首牌 (Ace of Cups)": ("新的愛情、情感、創造力", "情感壓抑、空虛"),
    "聖杯侍從 (Page of Cups)": ("創意、直覺、情感訊息", "情感不成熟、逃避現實"),
    "聖杯騎士 (Knight of Cups)": ("浪漫、魅力、理想主義", "幻想、欺騙、嫉妒"),
    "聖杯皇后 (Queen of Cups)": ("同情、直覺、情感支持", "情緒化、依賴、多愁善感"),
    "聖杯國王 (King of Cups)": ("情感成熟、同情、外交", "情緒操縱、冷漠"),
    "寶劍首牌 (Ace of Swords)": ("突破、清晰、真理", "困惑、殘酷、錯誤的決定"),
    "寶劍侍從 (Page of Swords)": ("好奇、新想法、警惕", "閒言閒語、防衛心強"),
    "寶劍騎士 (Knight of Swords)": ("果斷、野心、行動迅速", "魯莽、不計後果、具攻擊性"),
    "寶劍皇后 (Queen of Swords)": ("獨立、清晰的思維、智慧", "冷酷、尖酸刻薄、孤立"),
    "寶劍國王 (King of Swords)": ("權威、真理、智力", "殘酷、專制、判斷力差"),
    "錢幣首牌 (Ace of Pentacles)": ("新的機會、繁榮、顯化", "錯失良機、財務問題"),
    "錢幣侍從 (Page of Pentacles)": ("學習、勤奮、新技能", "懶惰、缺乏常識、停滯"),
    "錢幣騎士 (Knight of Pentacles)": ("可靠、勤奮、耐心", "停滯、固執、無聊"),
    "錢幣皇后 (Queen of Pentacles)": ("務實、滋養、財務安全", "過度關注物質、工作狂"),
    "錢幣國王 (King of Pentacles)": ("富裕、成功、安全", "貪婪、物質主義、頑固"),
    # ... 其他牌卡可自行擴充 ...
}

class TarotCard:
    def __init__(self, name, meanings):
        self.name = name
        self.meaning_upright = meanings[0]
        self.meaning_reversed = meanings[1]
        self.is_reversed = False

    def draw(self):
        """模擬抽牌時決定正逆位"""
        self.is_reversed = random.choice([True, False])

    def get_display_name(self):
        orientation = "逆位" if self.is_reversed else "正位"
        return f"{self.name} ({orientation})"

    def get_meaning(self):
        return self.meaning_reversed if self.is_reversed else self.meaning_upright

class TarotDeck:
    def __init__(self):
        self.cards = [TarotCard(name, meanings) for name, meanings in TAROT_CARDS_DATA.items()]
        # 為了POC，我們用一個簡化的牌組，如果資料不全
        # 實際上應該有78張
        # st.info(f"牌組已初始化，共 {len(self.cards)} 張牌。")

    def shuffle(self):
        random.shuffle(self.cards)

    def draw_cards(self, num_cards):
        drawn_cards = []
        if len(self.cards) < num_cards:
            st.error("牌組剩餘牌數不足！")
            return []
        
        self.shuffle()
        for _ in range(num_cards):
            card = self.cards.pop()
            card.draw() # 決定正逆位
            drawn_cards.append(card)
        return drawn_cards

# 牌陣定義
SPREADS = {
    "時間之流 (3張)": {
        "num_cards": 3,
        "positions": ["過去", "現在", "未來"]
    },
    "關係牌陣 (4張)": {
        "num_cards": 4,
        "positions": ["您自己", "對方", "關係現況", "關係未來"]
    },
    "凱爾特十字 (10張)": {
        "num_cards": 10,
        "positions": [
            "現況", "挑戰", "根基(過去)", "近期未來",
            "目標(意識)", "潛在影響(潛意識)", "建議", "外在影響",
            "希望與恐懼", "最終結果"
        ]
    }
}

# --- 2. LLM 提示詞生成 (根據報告) ---

def generate_llm_prompt(spread_name, positions, drawn_cards, question):
    """根據報告第5章的設計，建構高品質的提示詞"""
    
    # 1. 角色設定 & 2. 任務指令
    prompt = "你是一位經驗豐富、溫暖且富有同理心的塔羅占卜師。\n"
    prompt += "請根據以下提供的塔羅牌陣抽牌結果，為問卜者提供一份詳細且富有洞察力的解讀。\n"
    
    if question:
        prompt += f"問卜者的問題是：「{question}」\n\n"
    else:
        prompt += "問卜者沒有提出具體問題，請就抽牌結果提供一個全面的生活指引。\n\n"

    # 3. 關鍵考量點 & 4. 輸出格式/風格
    prompt += "你的解讀需要：\n"
    prompt += "1. **綜合分析**：綜合考慮每張牌的正逆位牌義、其在牌陣中的位置含義，以及所有牌之間的相互關聯和故事線。\n"
    prompt += "2. **連貫故事**：將解讀組織成一個連貫流暢的故事，而不僅僅是牌義的簡單羅列。\n"
    prompt += "3. **實用建議**：在結尾提供清晰、溫和且可行的建議。\n"
    prompt += "4. **溫暖語氣**：請使用支持性、溫和的語氣進行解讀，確保內容清晰易懂。\n"
    prompt += "--- \n"
    
    # 5. 輸入數據標識
    prompt += "以下是抽牌結果：\n"
    prompt += f"牌陣名稱：{spread_name}\n\n"
    
    for i, card in enumerate(drawn_cards):
        prompt += f"位置 {i+1}: {positions[i]}\n"
        prompt += f"牌名: {card.get_display_name()}\n"
        prompt += f"牌義關鍵詞: {card.get_meaning()}\n\n"
        
    prompt += "---\n請開始你的解讀："
    return prompt

# --- 3. Streamlit 應用程式介面 ---

st.set_page_config(page_title="塔羅牌數位化抽牌系統 POC", layout="wide")

st.title("塔羅牌數位化抽牌系統實作報告 POC")
st.markdown("這是一個基於報告概念，使用 Streamlit 和 Google Gemini 1.5 Flash 實現的原型。")

# 使用 session state 來保存抽牌結果
if 'drawn_cards' not in st.session_state:
    st.session_state.drawn_cards = []
if 'spread_info' not in st.session_state:
    st.session_state.spread_info = {}

# 側邊欄配置
with st.sidebar:
    st.header("設定")
    # 讓使用者輸入API金鑰
    api_key = st.text_input("請輸入您的 Google AI API 金鑰", type="password")
    
    st.header("開始占卜")
    question = st.text_area("請輸入您想問的問題（可選）", placeholder="例如：我最近的事業發展如何？")
    selected_spread = st.selectbox("請選擇牌陣", list(SPREADS.keys()))

    if st.button("開始抽牌", use_container_width=True):
        if not api_key:
            st.warning("請先在側邊欄輸入您的 Google AI API 金鑰。")
        else:
            try:
                genai.configure(api_key=api_key)
                # 測試API金鑰是否有效
                genai.GenerativeModel('gemini-1.5-flash-latest')
                
                deck = TarotDeck()
                spread_info = SPREADS[selected_spread]
                st.session_state.drawn_cards = deck.draw_cards(spread_info["num_cards"])
                st.session_state.spread_info = spread_info
                st.session_state.question = question
                st.session_state.spread_name = selected_spread
                st.success("抽牌完成！結果顯示在主畫面。")
            except Exception as e:
                st.error(f"API 金鑰設定失敗或無效: {e}")

# 主畫面顯示
if st.session_state.drawn_cards:
    st.subheader(f"抽牌結果：{st.session_state.spread_name}")
    if st.session_state.question:
        st.info(f"您的問題是：「{st.session_state.question}」")

    positions = st.session_state.spread_info["positions"]
    num_cards = len(st.session_state.drawn_cards)
    
    # 使用欄位來美化顯示
    cols = st.columns(min(num_cards, 5)) # 每行最多顯示5張牌
    for i, card in enumerate(st.session_state.drawn_cards):
        col = cols[i % 5]
        with col:
            with st.container(border=True):
                st.markdown(f"**{i+1}. {positions[i]}**")
                st.markdown(f"#### {card.get_display_name()}")
                st.caption(f"關鍵詞：{card.get_meaning()}")

    st.markdown("---")
    if st.button("🔮 獲取 Gemini AI 解讀", type="primary", use_container_width=True):
        try:
            with st.spinner("Gemini 正在為您解讀牌義，請稍候..."):
                # 產生提示詞
                prompt = generate_llm_prompt(
                    st.session_state.spread_name,
                    positions,
                    st.session_state.drawn_cards,
                    st.session_state.question
                )

                # 呼叫 Gemini API
                model = genai.GenerativeModel('gemini-1.5-flash-latest')
                response = model.generate_content(prompt)
                
                # 顯示結果
                st.subheader("🌟 Gemini AI 塔羅解讀")
                st.markdown(response.text)

        except Exception as e:
            st.error(f"解讀時發生錯誤: {e}")
            st.info("請確認您的 API 金鑰是否正確且有足夠的權限。")
else:
    st.info("請在左側側邊欄設定您的 API 金鑰，選擇牌陣並點擊「開始抽牌」。")


