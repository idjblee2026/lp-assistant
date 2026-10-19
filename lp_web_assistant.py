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

word_files = os.listdir(WORD_DIR) if os.path.exists(WORD_DIR) else []

for idx, row in filtered.iterrows():
    row_text_list = [str(val).strip() for val in row.values if pd.notna(val)]
    title_text = " - ".join(row_text_list[:3])
    
    st.markdown(f"### 🎵 {title_text}")
    
    # 워드 문서 자동 매칭
    matched_doc = None
    for wf in word_files:
        if not wf.endswith('.docx') or wf.startswith('~$'):
            continue
        for val in row_text_list:
            if len(val) >= 2 and val in wf:
                matched_doc = os.path.join(WORD_DIR, wf)
                break
        if matched_doc:
            break
            
    # 워드 원본 내용 화면에 바로 펼침
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
