import os
import streamlit as st
import pandas as pd
import docx

st.set_page_config(page_title="LP 비서", layout="wide")
st.title("💿 LP 컬렉션 비서")

EXCEL_FILE = "lp_list.xlsx"
WORD_DIR = "word_reports"

if not os.path.exists(EXCEL_FILE):
    st.error("lp_list.xlsx 파일을 찾을 수 없습니다.")
    st.stop()

@st.cache_data
def load_data():
    return pd.read_excel(EXCEL_FILE)

try:
    df = load_data()
except Exception as e:
    st.error(f"엑셀 로딩 실패: {e}")
    st.stop()

# 검색창
search_query = st.text_input("🔍 검색어 입력 (번호, 가수, 곡명 등)", "").strip()

if search_query:
    filtered = df[df.apply(lambda row: row.astype(str).str.contains(search_query, case=False).any(), axis=1)]
else:
    filtered = df

st.write(f"총 **{len(filtered)}**건")

word_files = [f for f in os.listdir(WORD_DIR) if f.endswith('.docx') and not f.startswith('~$')] if os.path.exists(WORD_DIR) else []

for idx, row in filtered.iterrows():
    # 엑셀 행의 주요 정보 추출
    row_dict = {str(k).strip(): str(v).strip() for k, v in row.items() if pd.notna(v)}
    
    # 대표 필드 값 찾기
    loc = row_dict.get('위치', row_dict.get('번호', ''))
    artist = row_dict.get('가수', row_dict.get('아티스트', ''))
    album = row_dict.get('앨범', row_dict.get('음반명', ''))
    
    title_display = f"{album} - {artist}" if album and artist else " - ".join(list(row_dict.values())[:3])
    st.markdown(f"### 🎵 {title_display}")
    
    # 기본 정보 안내
    info_details = " | ".join([f"**{k}**: {v}" for k, v in row_dict.items() if k not in ['해설', '비고']])
    st.markdown(info_details)
    
    # 정확한 워드 파일 매칭: [위치] 또는 [앨범명] 기준
    matched_doc = None
    if loc:
        for wf in word_files:
            if f"[{loc}]" in wf or f"위치_{loc}_" in wf or wf.startswith(f"{loc}_") or wf.startswith(f"{loc} "):
                matched_doc = os.path.join(WORD_DIR, wf)
                break
                
    if not matched_doc and album:
        for wf in word_files:
            if album in wf:
                matched_doc = os.path.join(WORD_DIR, wf)
                break

    # 워드 문서 내용 표시
    if matched_doc and os.path.exists(matched_doc):
        try:
            doc = docx.Document(matched_doc)
            paras = [p.text for p in doc.paragraphs if p.text.strip()]
            if paras:
                st.markdown("---")
                st.markdown("#### 📖 음반 해설 전문")
                for p in paras:
                    st.write(p)
        except Exception:
            pass
            
    st.markdown("---")
