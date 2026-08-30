import streamlit as st
import json
import os

st.set_page_config(page_title="LP 감성 음악비서", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    .main { background-color: #f8fafc; }
    .lp-card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
        border-left: 5px solid #2563eb;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .lp-loc { font-size: 16px; font-weight: bold; color: #dc2626; }
    .lp-title { font-size: 18px; font-weight: bold; color: #1e293b; }
    .lp-meta { font-size: 13px; color: #64748b; margin: 4px 0 8px 0; }
    .lp-desc { font-size: 14px; color: #334155; line-height: 1.6; }
    .lp-ai-box { background-color: #f1f5f9; border-radius: 8px; padding: 10px; margin-top: 8px; font-size: 13.5px; color: #1e293b; }
</style>
""", unsafe_allow_html=True)

st.title("📻 LP 감성 음악비서 (Mobile/Web)")
st.caption("소장 LP 서재 & 자연어 감성 추천기")

# 데이터 로드 함수
@st.cache_data
def load_data():
    json_path = os.path.join(os.path.dirname(__file__), "lp_database.json")
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

lp_data = load_data()

# 검색창
query = st.text_input("🔍 음반 제목, 아티스트, 또는 원하는 분위기를 검색하세요:", "")

if query:
    filtered = [
        item for item in lp_data 
        if query.lower() in str(item.get("title", "")).lower() 
        or query.lower() in str(item.get("artist", "")).lower()
        or query.lower() in str(item.get("intro", "")).lower()
        or query.lower() in str(item.get("detail", "")).lower()
    ]
else:
    filtered = lp_data

if filtered:
    st.write(f"총 **{len(filtered)}**개의 음반이 검색되었습니다.")
    for item in filtered:
        loc = item.get("loc", item.get("위치", ""))
        title = item.get("title", item.get("앨범명", ""))
        artist = item.get("artist", item.get("아티스트", ""))
        genre = item.get("genre", item.get("장르", ""))
        year = item.get("year", item.get("발매년도", ""))
        intro = item.get("intro", item.get("음반소개", ""))
        detail = item.get("detail", item.get("해설", ""))

        st.markdown(f"""
        <div class="lp-card">
            <div class="lp-loc">[위치: @{loc}] {artist} - {title}</div>
            <div class="lp-meta">장르: {genre} | 발매년도: {year}</div>
            <div class="lp-ai-box">
                💡 <b>AI 추천 해설:</b><br>
                • 음반 소개: {intro}
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.expander(f"📖 [위치: @{loc}] 해설 원본 열기"):
            raw_text = detail if detail else intro
            safe_text = str(raw_text).replace("~", "～")
            st.write(safe_text)
else:
    st.info("검색된 음반이 없습니다. 다른 키워드나 테마를 선택해 보세요.")
