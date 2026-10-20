import os
import urllib.parse
import streamlit as st
import pandas as pd
import docx

st.set_page_config(page_title="LP 비서", layout="wide")
st.title("동암 LP 컬렉션 비서 (음악 감상실)")

EXCEL_FILE = "lp_list.xlsx"
WORD_DIR = "word_reports"
TRACKS_DIR = "word_tracks"

if not os.path.exists(EXCEL_FILE):
    st.error("lp_list.xlsx 파일을 찾을 수 없습니다.")
    st.stop()

@st.cache_data
def load_data():
    raw_df = pd.read_excel(EXCEL_FILE)
    drop_cols = [c for c in raw_df.columns if str(c).strip() in ["번호", "순번", "no", "No", "NO"]]
    if drop_cols:
        raw_df = raw_df.drop(columns=drop_cols)
    return raw_df

try:
    df = load_data()
except Exception as e:
    st.error(f"엑셀 로딩 실패: {e}")
    st.stop()

search_query = st.text_input("검색어 입력 (위치, 가수, 곡명 등)", "").strip()

if search_query:
    filtered = df[df.apply(lambda row: row.astype(str).str.contains(search_query, case=False).any(), axis=1)]
else:
    filtered = df

st.write(f"총 **{len(filtered)}**건")

word_files = [f for f in os.listdir(WORD_DIR) if f.endswith('.docx') and not f.startswith('~$')] if os.path.exists(WORD_DIR) else []
track_files = [f for f in os.listdir(TRACKS_DIR) if f.endswith('.docx') and not f.startswith('~$')] if os.path.exists(TRACKS_DIR) else []

for idx, row in filtered.iterrows():
    row_dict = {str(k).strip(): str(v).strip() for k, v in row.items() if pd.notna(v)}
    
    loc = row_dict.get('위치', '')
    artist = row_dict.get('가수', row_dict.get('Artists', row_dict.get('아티스트', '')))
    album = row_dict.get('앨범', row_dict.get('앨범명', ''))
    
    title_display = f"{album} - {artist}" if album and artist else " - ".join(list(row_dict.values())[:3])
    st.markdown(f"### [음반] {title_display}")
    
    info_details = " | ".join([f"**{k}**: {v}" for k, v in row_dict.items() if k not in ['해설', '비고']])
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
    
    # 1. 기존 음반 해설 전문
    matched_doc = None
    if loc:
        for wf in word_files:
            if f"[{loc}]" in wf or f"위치_{loc}_" in wf or f"위치 {loc}" in wf or wf.startswith(f"{loc}_") or wf.startswith(f"{loc} "):
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

    # 2. 새로 추가된 수록곡 상세 해설 (word_tracks)
    matched_track_doc = None
    if loc:
        for tf in track_files:
            if f"[{loc}]" in tf or f"[위치 {loc}]" in tf or f"[위치_{loc}]" in tf or f"위치 {loc}" in tf:
                matched_track_doc = os.path.join(TRACKS_DIR, tf)
                break

    if matched_track_doc and os.path.exists(matched_track_doc):
        try:
            tdoc = docx.Document(matched_track_doc)
            tparas = [p.text for p in tdoc.paragraphs if p.text.strip()]
            if tparas:
                st.markdown("---")
                st.markdown("#### 수록곡 상세 해설")
                for p in tparas:
                    st.write(p)
        except Exception:
            pass
            
    st.markdown("---")
