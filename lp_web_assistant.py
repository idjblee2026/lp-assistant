import streamlit as st
import json
import os

st.set_page_config(page_title="LP 감성 음악비서", page_icon="📀", layout="wide")

st.markdown("""
<style>
    .main { background-color: #f8fafc; }
    .lp-card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 16px;
        border-left: 6px solid #2563eb;
        box-shadow: 0 2px 6px rgba(0,0,0,0.06);
    }
    .lp-loc { font-size: 17px; font-weight: bold; color: #dc2626; margin-bottom: 4px; }
    .lp-title { font-size: 19px; font-weight: bold; color: #0f172a; margin: 4px 0 8px 0; }
    .lp-meta { font-size: 13px; color: #475569; margin-bottom: 12px; background-color: #f1f5f9; padding: 6px 10px; border-radius: 6px; }
    .lp-section-title { font-size: 14px; font-weight: bold; color: #1e40af; margin-top: 10px; margin-bottom: 4px; }
    .lp-desc { font-size: 14px; color: #334155; line-height: 1.6; white-space: pre-line; }
</style>
""", unsafe_allow_html=True)

st.title("📀 LP 감성 음악비서 (Mobile/Web)")
st.caption("소장 LP 서재 & 자연어 감성 추천기")

@st.cache_data
def load_data():
    if os.path.exists("lp_database.json"):
        with open("lp_database.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return []

data = load_data()

MOOD_TAGS = {
    "비 오는 날": ["비", "차분", "우울", "재즈", "센티멘탈", "빗소리", "발라드", "스트링"],
    "아침 서정적": ["아침", "상쾌", "산뜻", "서정적", "모차르트", "클래식", "기분전환", "밝은"],
    "밤/새벽 무드": ["밤", "새벽", "조용한", "피아노", "첼로", "어쿠스틱", "독주", "사색"],
    "신나는/활기찬": ["신나는", "경쾌", "팝", "락", "디스코", "댄스", "신바람"],
    "클래식 명반": ["교향곡", "협주곡", "소나타", "지휘자", "오케스트라", "필하모닉", "도이치", "데카"]
}

st.write("✨ **오늘의 추천 테마 선택**")
cols = st.columns(len(MOOD_TAGS))
selected_mood = None
for i, mood in enumerate(MOOD_TAGS.keys()):
    if cols[i].button(mood):
        selected_mood = mood

query = st.text_input("🔍 직접 검색 (예: 비 오는 날 잔잔한 현악, 베토벤, 피아노, 위치 번호)", value=selected_mood if selected_mood else "")

if query:
    query_terms = [query]
    if query in MOOD_TAGS:
        query_terms += MOOD_TAGS[query]

    results = []
    for item in data:
        full_text = f"{item.get('location', '')} {item.get('artist', '')} {item.get('album', '')} {item.get('genre', '')} {item.get('tracks', '')} {item.get('description', '')} {item.get('intro', '')} {item.get('content', '')}"
        
        score = sum(1 for term in query_terms if term.lower() in full_text.lower())
        if score > 0:
            results.append((score, item))

    results.sort(key=lambda x: x[0], reverse=True)

    st.write(f"총 **{len(results)}개**의 맞춤 음반을 찾았습니다:")
    for _, item in results[:30]:
        loc = str(item.get('location', '미확인')).replace('@', '').strip()
        intro_text = item.get('intro') or item.get('description') or '등록된 개요가 없습니다.'
        detail_content = item.get('content') or item.get('tracks') or item.get('raw_text') or ''

        st.markdown(f"""
        <div class="lp-card">
            <div class="lp-loc">📍 서재 위치: @{loc}</div>
            <div class="lp-title">{item.get('artist', '미확인')} - {item.get('album', '')}</div>
            <div class="lp-meta">🏷️ 레이블: {item.get('label', '미확인')} | 📅 발매년도: {item.get('year', '미확인')} | 🎷 장르: {item.get('genre', '-')}</div>
            <div class="lp-section-title">📖 음반 개요</div>
            <div class="lp-desc">{intro_text}</div>
        </div>
        """, unsafe_allow_html=True)
        
        if detail_content:
            with st.expander(f"📄 @{loc} 세부 워드문서 전문 펼쳐보기"):
                st.write(detail_content)
else:
    st.info("💡 위의 감성 테마 버튼을 누르시거나, 검색창에 원하시는 분위기/가수/위치 번호를 입력해 보세요.")
