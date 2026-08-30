import streamlit as st
import json
import os
import re

st.set_page_config(page_title="나만의 LP 서재 AI 음악 비서", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    .main { background-color: #f8fafc; }
    .lp-card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 18px 20px;
        margin-bottom: 16px;
        border-left: 6px solid #2563eb;
        box-shadow: 0 2px 6px rgba(0,0,0,0.04);
    }
    .lp-loc { font-size: 17px; font-weight: bold; color: #1e293b; }
    .lp-loc span.loc-tag { color: #dc2626; }
    .lp-meta { font-size: 13px; color: #64748b; margin: 4px 0 10px 0; }
    .lp-ai-box { background-color: #f8fafc; border-radius: 8px; padding: 12px; margin-top: 8px; font-size: 13.5px; color: #334155; line-height: 1.6; }
</style>
""", unsafe_allow_html=True)

st.title("📀 나만의 LP 서재 AI 음악 비서")

@st.cache_data
def load_data():
    json_path = os.path.join(os.path.dirname(__file__), "lp_database.json")
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

lp_data = load_data()

if "search_query" not in st.session_state:
    st.session_state.search_query = ""

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    if st.button("🟠 아침 서정적 클래식"):
        st.session_state.search_query = "클래식"
with col2:
    if st.button("🟣 비 오는 날 감성 보컬"):
        st.session_state.search_query = "보컬"
with col3:
    if st.button("🍃 밤 피아노"):
        st.session_state.search_query = "피아노"
with col4:
    if st.button("🎷 모타운 레이블"):
        st.session_state.search_query = "모타운"
with col5:
    if st.button("🎸 80년대 팝"):
        st.session_state.search_query = "80년대"

query = st.text_input("🔍 음반 제목, 아티스트, 번호(위치), 또는 분위기를 검색하세요:", value=st.session_state.search_query)

if query:
    q = query.lower().strip()
    filtered = [
        item for item in lp_data 
        if any(q in str(val).lower() for val in item.values())
    ]
else:
    filtered = lp_data

if filtered:
    st.write(f"총 **{len(filtered)}**개의 음반이 검색되었습니다.")
    for item in filtered:
        # 1. 위치 번호 추출 (@숫자 형식 또는 번호 필드 자동 탐색)
        loc = ""
        full_text_combined = " ".join([str(v) for v in item.values() if v is not None])
        
        # 텍스트 전체에서 위치 번호 패턴 탐색 (예: 위치 : @105, @105, 위치_235 등)
        loc_match = re.search(r'위치\s*[:_]\s*@?([0-9A-Za-z_-]+)', full_text_combined)
        if loc_match:
            loc = loc_match.group(1).strip()
        else:
            for k, v in item.items():
                if any(x in str(k) for x in ["위치", "loc", "연번", "번호"]) and v:
                    loc = str(v).replace("@", "").strip()
                    break

        # 2. 텍스트 값들을 길이순/내용순으로 분류
        values = [str(v).strip() for v in item.values() if v is not None and str(v).strip() not in ["", "nan", "None"]]
        
        # 아티스트 및 앨범명 추출
        artist = ""
        title = ""
        for k, v in item.items():
            k_str = str(k)
            if any(x in k_str for x in ["가수", "아티스트", "artist"]) and v:
                artist = str(v).strip()
            elif any(x in k_str for x in ["앨범", "title", "제목", "음반명"]) and v:
                title = str(v).strip()

        # 키로 못 찾았을 때 짧은 텍스트들에서 추정
        if not artist and len(values) > 0:
            artist = values[0]
        if not title and len(values) > 1 and values[1] != artist:
            title = values[1]

        # 3. 해설/소개 텍스트 자동 추출 (가장 긴 본문 텍스트들 활용)
        long_texts = sorted([v for v in values if len(v) > 25], key=len, reverse=True)
        
        detail_text = long_texts[0] if len(long_texts) > 0 else full_text_combined
        intro_text = long_texts[1] if len(long_texts) > 1 else (detail_text[:150] + "..." if len(detail_text) > 150 else detail_text)

        # 헤더 표시
        header_text = f"<span class='loc-tag'>[위치: @{loc}]</span> " if loc else ""
        header_text += artist
        if title and title != artist:
            header_text += f" - {title}"

        st.markdown(f"""
        <div class="lp-card">
            <div class="lp-loc">{header_text}</div>
            <div class="lp-meta">장르: - | 발매년도: 1 음반 데이터</div>
            <div class="lp-ai-box">
                💡 <b>AI 추천 해설:</b><br>
                • 음반 소개: {intro_text}
            </div>
        </div>
        """, unsafe_allow_html=True)

        expander_title = f"📖 [위치: @{loc}] 해설 원본 열기" if loc else "📖 해설 원본 열기"
        with st.expander(expander_title):
            safe_text = str(detail_text).replace("~", "～")
            st.write(safe_text)
else:
    st.info("검색된 음반이 없습니다. 다른 키워드나 번호를 입력해 보세요.")
