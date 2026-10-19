import os
import streamlit as st
import pandas as pd
import docx

st.set_page_config(page_title="동암 LP 비서", layout="wide")
st.title("동암 LP 컬렉션 비서")

# 엑셀 데이터 로드
EXCEL_FILE = "lp_list.xlsx"
WORD_DIR = "word_reports"

if not os.path.exists(EXCEL_FILE):
    st.error("lp_list.xlsx 파일을 찾을 수 없습니다.")
    st.stop()

@st.cache_data
def load_data():
    return pd.read_excel(EXCEL_FILE)

df = load_data()

# 검색창
search_query = st.text_input("🔍 검색 (가수, 곡명, 번호 등)", "").strip()

if search_query:
    filtered = df[df.apply(lambda row: row.astype(str).str.contains(search_query, case=False).any(), axis=1)]
else:
    filtered = df

st.write(f"총 **{len(filtered)}**건이 검색되었습니다.")

# 검색 결과 목록 표시
for idx, row in filtered.iterrows():
    loc = str(row.get('위치', '')).strip()
    artist = str(row.get('가수', row.get('아티스트', ''))).strip()
    album = str(row.get('앨범', row.get('음반명', ''))).strip()
    
    st.markdown(f"### 💿 {album} - {artist}")
    st.caption(f"위치: {loc} | 인덱스: {idx}")
    
    # 워드 문서 자동 매칭 및 전문 직접 표시
    doc_file = None
    if os.path.exists(WORD_DIR):
        for f in os.listdir(WORD_DIR):
            if f.endswith('.docx') and (loc in f or (album and album in f)):
                doc_file = os.path.join(WORD_DIR, f)
                break
                
    if doc_file and os.path.exists(doc_file):
        try:
            doc = docx.Document(doc_file)
            full_text = [p.text for p in doc.paragraphs if p.text.strip()]
            st.markdown("#### 📖 음반 해설 전문")
            st.write("

".join(full_text))
        except Exception as e:
            st.info("해설 문서를 불러오는 중입니다...")
    st.markdown("---")
