import streamlit as st
import json
import os
import re

st.set_page_config(page_title="나만의 LP 서재 AI 음악 비서", layout="wide", initial_sidebar_state="collapsed")

# PC와 태블릿/스마트폰 글자 크기 분리 스타일 적용
st.markdown("""
<style>
    .main { background-color: #f8fafc; }
    
    /* 1. 기본 PC 화면 스타일 (단정하고 편안한 기본 크기) */
    .lp-card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 18px 22px;
        margin-bottom: 18px;
        border-left: 7px solid #2563eb;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    .lp-loc { font-size: 19px !important; font-weight: bold !important; color: #0f172a !important; line-height: 1.4 !important; }
    .lp-loc span.loc-tag { color: #dc2626 !important; font-size: 19px !important; }
    .lp-meta { font-size: 14px !important; color: #64748b !important; margin: 4px 0 10px 0 !important; }
    .lp-ai-box { 
        background-color: #f1f5f9 !important; 
        border-radius: 8px !important; 
        padding: 14px 16px !important; 
        margin-top: 8px !important; 
        font-size: 15px !important; 
        color: #1e293b !important; 
        line-height: 1.65 !important; 
        word-break: keep-all !important;
    }
    .expander-content {
        font-size: 15px !important;
        line-height: 1.7 !important;
        color: #1e293b !important;
        background-color: #ffffff !important;
        padding: 14px !important;
        border-radius: 8px !important;
        word-break: keep-all !important;
    }

    /* 2. 아이패드 및 태블릿/모바일 전용 스타일 (시원한 대형 글씨 자동 전환) */
    @media screen and (max-width: 1024px) {
        .lp-card {
            padding: 24px 26px !important;
            margin-bottom: 22px !important;
            border-left: 10px solid #2563eb !important;
        }
        .lp-loc { font-size: 26px !important; line-height: 1.4 !important; font-weight: 800 !important; }
        .lp-loc span.loc-tag { font-size: 26px !important; font-weight: 800 !important; }
        .lp-meta { font-size: 18px !important; margin: 8px 0 14px 0 !important; }
        
        /* 아이패드용 AI 추천 해설 대형 글씨 */
        .lp-ai-box { 
            padding: 20px 22px !important; 
            font-size: 24px !important; 
            font-weight: 500 !important;
            line-height: 1.85 !important; 
        }
        .lp-ai-box b { font-size: 25px !important; color: #1e3a8a !important; }
        
        /* 아이패드용 해설 원본 대형 글씨 */
        [data-testid="stExpander"] details summary span {
            font-size: 24px !important;
            font-weight: bold !important;
            padding: 8px 0 !important;
        }
        .expander-content {
            font-size: 23px !important;
            line-height: 1.85 !important;
            padding: 20px !important;
        }
    }
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
    clean_query = query.lower().strip()
    words = [w for w in re.split(r'[\s,./?~!@#]+', clean_query) if len(w) >= 2]
    
    filtered = []
    for item in lp_data:
        item_text = " ".join([str(v).lower() for v in item.values() if v is not None])
        if clean_query in item_text:
            filtered.append(item)
        elif words and any(w in item_text for w in words):
            filtered.append(item)
else:
    filtered = lp_data

if filtered:
    st.write(f"총 **{len(filtered)}**개의 음반이 검색되었습니다.")
    for item in filtered:
        full_text = " ".join([str(v) for v in item.values() if v is not None])

        # 1. 위치 번호 추출
        loc = ""
        loc_match = re.search(r'위치\s*[:_]?\s*@?([0-9]+)', full_text)
        if loc_match:
            loc = loc_match.group(1)
        else:
            for k, v in item.items():
                if any(x in str(k) for x in ["위치", "loc", "번호"]):
                    m = re.search(r'([0-9]+)', str(v))
                    if m:
                        loc = m.group(1)
                        break

        # 2. 항목별 텍스트 추출
        artist = ""
        title = ""
        for k, v in item.items():
            k_s = str(k).lower()
            val_s = str(v).strip() if v else ""
            if any(x in k_s for x in ["가수", "아티스트", "artist"]) and val_s:
                artist = val_s
            elif any(x in k_s for x in ["앨범", "title", "제목", "음반명"]) and val_s:
                title = val_s

        # 3. 해설 본문 분리
        raw_detail = max([str(v) for v in item.values() if v is not None], key=len, default="")
        intro_clean = ""
        if "• 음반 소개:" in raw_detail:
            intro_clean = raw_detail.split("• 음반 소개:")[-1].strip()
        elif "음반소개:" in raw_detail:
            intro_clean = raw_detail.split("음반소개:")[-1].strip()
        elif "음반 소개:" in raw_detail:
            intro_clean = raw_detail.split("음반 소개:")[-1].strip()
        else:
            intro_clean = re.sub(r'^(LP_.*?\n|.*?위치\s*:.*?\n|.*?발매년도\s*:.*?\n)+', '', raw_detail).strip()

        # 4. 아티스트란에 '가수 - 앨범명' 형식인 경우 분리
        if "-" in artist:
            parts = artist.split("-", 1)
            artist = parts[0].strip()
            title = parts[1].strip()

        # 5. 본문 속 [앨범명] 또는 《앨범명》, <앨범명> 추출
        body_title_match = re.search(r'(?:앨범\s*)?[\[《<]([^\]》>]+)[\]》>]', intro_clean)
        if body_title_match:
            title = body_title_match.group(1).strip()

        ai_summary = intro_clean[:180] + "..." if len(intro_clean) > 180 else intro_clean

        # 6. 헤더 텍스트 조합
        loc_badge = f"<span class='loc-tag'>[위치: @{loc}]</span> " if loc else ""
        
        if title:
            if artist and artist != title:
                display_title = f"<b>{title}</b> ({artist})"
            else:
                display_title = f"<b>{title}</b>"
        else:
            display_title = f"<b>{artist}</b>"

        header_text = f"{loc_badge}{display_title}"

        st.markdown(f"""
        <div class="lp-card">
            <div class="lp-loc">{header_text}</div>
            <div class="lp-meta">장르: - | 발매년도: 1 음반 데이터</div>
            <div class="lp-ai-box">
                💡 <b>AI 추천 해설:</b><br>
                • 음반 소개: {ai_summary if ai_summary else '음반 소개 정보가 준비 중입니다.'}
            </div>
        </div>
        """, unsafe_allow_html=True)

        expander_title = f"📖 [위치: @{loc}] 해설 원본 열기" if loc else "📖 해설 원본 열기"
        with st.expander(expander_title):
            safe_text = str(intro_clean if intro_clean else raw_detail).replace("~", "～")
            st.markdown(f'<div class="expander-content">{safe_text}</div>', unsafe_allow_html=True)
else:
    st.info("검색된 음반이 없습니다. 다른 키워드나 번호를 입력해 보세요.")
