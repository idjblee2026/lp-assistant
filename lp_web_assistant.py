import streamlit as st
import json
import os

st.set_page_config(page_title="나만의 LP 서재 AI 음악 비서", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    .main { background-color: #f8fafc; }
    .stTextInput > div > div > input {
        border-radius: 8px;
    }
    .theme-btn-container {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
        margin-bottom: 20px;
    }
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

# 데이터 로드
@st.cache_data
def load_data():
    json_path = os.path.join(os.path.dirname(__file__), "lp_database.json")
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

lp_data = load_data()

# 세션 상태 초기화 (테마 버튼용)
if "search_query" not in st.session_state:
    st.session_state.search_query = ""

# 상단 감성 테마 버튼
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

# 검색창
query = st.text_input("🔍 음반 제목, 아티스트, 번호(위치), 또는 분위기를 검색하세요:", value=st.session_state.search_query)

def get_field_val(item, keys):
    for k in keys:
        if k in item and item[k] is not None:
            val = str(item[k]).strip()
            if val and val != "nan":
                return val
    return ""

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
        # 데이터 항목 정확 매칭
        raw_loc = get_field_val(item, ["위치", "loc", "연번", "번호"])
        loc = raw_loc.lstrip("@").strip()
        
        artist = get_field_val(item, ["가수명/그룹명", "아티스트", "artist", "가수"])
        title = get_field_val(item, ["앨범명", "title", "제목", "음반명"])
        genre = get_field_val(item, ["장르", "genre"])
        year = get_field_val(item, ["발매년도", "year", "연도"])
        intro = get_field_val(item, ["AI추천해설", "추천사유", "음반소개", "intro", "소개"])
        detail = get_field_val(item, ["해설원본", "해설", "detail", "내용"])

        # 헤더 텍스트 구성
        header_text = f"<span class='loc-tag'>[위치: @{loc}]</span> " if loc else ""
        header_text += artist
        if title:
            header_text += f" - {title}"

        # AI 추천 해설 구성
        ai_desc = intro if intro else (detail[:160] + "..." if len(detail) > 160 else detail)

        st.markdown(f"""
        <div class="lp-card">
            <div class="lp-loc">{header_text}</div>
            <div class="lp-meta">장르: {genre if genre else '-'} | 발매년도: {year if year else '1'} 음반 데이터</div>
            <div class="lp-ai-box">
                💡 <b>AI 추천 해설:</b><br>
                • 음반 소개: {ai_desc}
            </div>
        </div>
        """, unsafe_allow_html=True)

        expander_label = f"📖 [위치: @{loc}] 해설 원본 열기" if loc else "📖 해설 원본 열기"
        with st.expander(expander_label):
            full_text = detail if detail else (intro if intro else "등록된 해설 내용이 없습니다.")
            safe_text = str(full_text).replace("~", "～")
            st.write(safe_text)
else:
    st.info("검색된 음반이 없습니다. 다른 키워드나 번호를 입력해 보세요.")
