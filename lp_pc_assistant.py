import os
import urllib.parse
import streamlit as st
import pandas as pd
import docx

st.set_page_config(page_title="LP 비서 (PC 전용)", layout="wide")
st.title("동암 LP 컬렉션 비서 (음악 감상실)")

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
EXCEL_FILE = os.path.join(BASE_DIR, "lp_list.xlsx")
WORD_DIR = os.path.join(BASE_DIR, "word_reports")

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

search_query = st.text_input("검색어 입력 (번호, 가수, 곡명 등)", "").strip()

if search_query:
    filtered = df[df.apply(lambda row: row.astype(str).str.contains(search_query, case=False).any(), axis=1)]
else:
    filtered = df

st.write(f"총 **{len(filtered)}**건")

word_files = [f for f in os.listdir(WORD_DIR) if f.endswith(".docx") and not f.startswith("~$")] if os.path.exists(WORD_DIR) else []

for idx, row in filtered.iterrows():
    row_dict = {str(k).strip(): str(v).strip() for k, v in row.items() if pd.notna(v)}
    
    loc = row_dict.get("위치", row_dict.get("번호", ""))
    artist = row_dict.get("가수", row_dict.get("Artists", row_dict.get("아티스트", "")))
    album = row_dict.get("앨범", row_dict.get("앨범명", ""))
    
    title_display = f"{album} - {artist}" if album and artist else " - ".join(list(row_dict.values())[:3])
    st.markdown(f"### [음반] {title_display}")
    
    info_details = " | ".join([f"**{k}**: {v}" for k, v in row_dict.items() if k not in ["해설", "비고"]])
    st.markdown(info_details)
    
    clean_search = f"{artist} {album}".strip() if (artist or album) else title_display
    yt_query = urllib.parse.quote_plus(clean_search)
    yt_url = f"https://www.youtube.com/results?search_query={yt_query}"
    
    st.markdown(
        f'''<a href="{yt_url}" target="_blank" style="text-decoration:none;">
            <button style="background-color:#FF0000; color:white; border:none; padding:8px 16px; border-radius:6px; font-weight:bold; cursor:pointer; margin-top:5px; margin-bottom:12px;">
                [▶] YouTube에서 음악 듣기
            </button>
        </a>''',
        unsafe_allow_html=True
    )
    
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

    if matched_doc and os.path.exists(matched_doc):
        try:
            doc = docx.Document(matched_doc)
            paras = [p.text for p in doc.paragraphs if p.text.strip()]
            if paras:
                st.markdown("---")
                st.markdown("#### 음반 해설 전문")
                for p in paras:
                    st.write(p)
        except Exception:
            pass

    st.markdown("---")
