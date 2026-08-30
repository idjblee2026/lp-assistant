import streamlit as st
import json
import os

st.set_page_config(page_title="나만의 LP 서재 AI 음악 비서", page_icon="📀", layout="wide")

st.markdown("""
<style>
    .main { background-color: #f8fafc; }
    .lp-card {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 16px;
        border-left: 6px solid #1e40af;
        box-shadow: 0 2px 5px rgba(0,0,0,0.06);
    }
    .lp-loc-title { font-size: 18px; font-weight: bold; color: #0f172a; margin-bottom: 4px; }
    .lp-meta { font-size: 13px; color: #64748b; margin-bottom: 10px; }
    .lp-ai-box { background-color: #f0fdf4; border-left: 3px solid #16a34a; padding: 10px; border-radius: 6px; margin-top: 8px; font-size: 14px; color: #166534; line-height: 1.6; }
</style>
""", unsafe_allow_html=True)

st.title("📀 나만의 LP 서재 AI 음악 비서")

@st.cache_data
def load_data():
    if os.path.exists("lp_database.json"):
        with open("lp_database.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return []

data = load_data()

# 상단 감성 프리셋 버튼
MOOD_PRESETS = {
    "비 오는 날 감성 보컬": ["비", "차분", "우울", "재즈", "센티멘탈", "빗소리", "발라드", "스트링", "보컬"],
    "아침 서정적 클래식": ["아침", "상쾌", "산뜻", "서정적", "모차르트", "클래식", "기분전환", "밝은"],
    "밤 피아노": ["밤", "새벽", "조용한", "피아노", "첼로", "어쿠스틱", "독주", "사색"],
    "모타운 레이블": ["모타운", "motown", "소울", "r&b", "디스코", "펑크"],
    "80년대 팝": ["80년대", "팝", "락", "댄스", "신스팝", "pop", "1980"]
}

cols = st.columns(len(MOOD_PRESETS))
selected_preset = None
for i, name in enumerate(MOOD_PRESETS.keys()):
    if cols[i].button(name):
        selected_preset = name

col_input, col_btn = st.columns([5, 1])
with col_input:
    query = st.text_input("검색어를 입력하세요 (예: 비 오는 날 감성 보컬, 작곡가, 연주자, 위치 번호)", value=selected_preset if selected_preset else "")
with col_btn:
    search_clicked = st.button("검색/추천", use_container_width=True)

if query:
    query_terms = [query]
    if query in MOOD_PRESETS:
        query_terms += MOOD_PRESETS[query]

    results = []
    for item in data:
        full_text = " ".join([str(v) for v in item.values()])
        score = sum(1 for term in query_terms if term.lower() in full_text.lower())
        if score > 0:
            results.append((score, item))

    results.sort(key=lambda x: x[0], reverse=True)

    if results:
        st.write(f"총 **{len(results)}건**의 맞춤 음반을 찾았습니다:")
        for _, item in results[:40]:
            loc = str(item.get('location', item.get('위치', '미확인'))).replace('@', '').strip()
            artist = item.get('artist', item.get('Artists', item.get('가수/작곡가', '미확인')))
            album = item.get('album', item.get('앨범명', ''))
            year = item.get('year', item.get('발매년도', '1 음반 데이터'))
            genre = item.get('genre', item.get('장르', '-'))
            
            # 워드 본문 전체 내용 가져오기
            detail = item.get('full_text') or item.get('content') or item.get('tracks') or item.get('description') or ''
            
            # AI 추천 해설: 워드 본문 중 '음반 소개' 또는 첫 설명 문단 추출
            intro = item.get('intro') or item.get('summary') or ''
            if not intro and detail:
                paragraphs = [p.strip() for p in detail.split('\n') if len(p.strip()) > 30]
                if paragraphs:
                    intro = paragraphs[0]
                else:
                    intro = detail[:200] + "..."
            
            if not intro:
                intro = "소장 LP 음반 해설입니다."

            st.markdown(f"""
            <div class="lp-card">
                <div class="lp-loc-title">[위치: @{loc}] {artist} - {album}</div>
                <div class="lp-meta">장르: {genre} | 발매년도: {year}</div>
                <div class="lp-ai-box">
                    💡 <b>AI 추천 해설:</b><br>
                    • 음반 소개: {intro}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            with st.expander(f"📖 [위치: @{loc}] 해설 원본 열기"):
                st.write(detail if detail else intro)
    else:
        st.info("검색된 음반이 없습니다. 다른 키워드나 테마 버튼을 선택해 보세요.")
else:
    st.info("💡 위의 감성 테마 버튼을 터치하시거나, 검색창에 원하시는 분위기/가수/위치 번호를 입력해 보세요.")
