import streamlit as st
import pandas as pd
import os
from docx import Document

st.set_page_config(page_title="LP 음반 관리 음악비서", page_icon="🎵", layout="wide")

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) if "__file__" in locals() else "."

def clean_markdown_text(text):
    if not isinstance(text, str):
        text = str(text)
    return text.replace("~~", "-").replace("~", "-")

# 컴퓨터 내 D:\LP_Agent 전체(하위 폴더 포함)를 뒤져 해당 위치 번호의 워드 파일을 찾는 함수
def find_docx_file(loc_num):
    clean_loc = str(loc_num).replace("@", "").strip()
    if not clean_loc or clean_loc == "nan":
        return None
    
    target_names = [
        f"위치_{clean_loc}_",
        f"_{clean_loc}_",
        f"위치_{clean_loc}."
    ]

    for root, dirs, files in os.walk(BASE_DIR):
        for f in files:
            if f.endswith(".docx") and not f.startswith("~$"):
                if any(t in f for t in target_names):
                    return os.path.join(root, f)
    return None

def get_docx_data(loc_num):
    doc_path = find_docx_file(loc_num)
    if not doc_path or not os.path.exists(doc_path):
        return None, "", "", ""

    try:
        doc = Document(doc_path)
        raw_paras = [p.text.replace("\x0b", "\n").replace("\r", "\n").strip() for p in doc.paragraphs if p.text.strip()]
        
        all_lines = []
        for p in raw_paras:
            for line in p.split("\n"):
                if line.strip():
                    all_lines.append(line.strip())

        artist = ""
        title = ""
        desc_lines = []
        capture = False

        for line in all_lines:
            if "아티스트" in line and ":" in line and not artist:
                artist = line.split(":", 1)[1].strip()
            elif "앨범명" in line and ":" in line and not title:
                title = line.split(":", 1)[1].strip()

            if "음반 해설" in line or "감상 가이드" in line or "음반 소개" in line:
                capture = True
                continue

            if capture:
                if any(line.startswith(k) for k in ["■ 위치", "■ 아티스트", "■ 앨범명", "■ 발매년도", "■ 주요 수록곡", "■ 음반 레이블"]):
                    capture = False
                else:
                    desc_lines.append(line)

        if not desc_lines:
            desc_lines = [l for l in all_lines if len(l) > 30 and not l.startswith("■")]

        desc_text = "\n\n".join(desc_lines) if desc_lines else "\n\n".join(all_lines)
        return doc_path, artist, title, desc_text
    except Exception:
        return doc_path, "", "", ""

@st.cache_data
def load_data():
    excel_path = os.path.join(BASE_DIR, "lp_list.xlsx")
    if os.path.exists(excel_path):
        xl = pd.ExcelFile(excel_path)
        sheet = "Sheet2" if "Sheet2" in xl.sheet_names else xl.sheet_names[0]
        return pd.read_excel(excel_path, sheet_name=sheet)
    return pd.DataFrame()

df = load_data()

st.title("🎵 LP 음반 관리 음악비서")

if df.empty:
    st.warning("LP 데이터베이스(lp_list.xlsx)를 찾을 수 없습니다.")
else:
    search_query = st.text_input("🔍 음반 검색 (앨범명, 아티스트, 수록곡, 위치 번호 등)", "")

    if search_query:
        mask = df.astype(str).apply(lambda row: row.str.contains(search_query, case=False, na=False)).any(axis=1)
        results = df[mask]
    else:
        results = df

    st.write(f"총 **{len(results)}** 건의 음반이 조회되었습니다.")
    st.divider()

    for idx, row in results.iterrows():
        # 위치 번호
        location = ""
        for col in ["위치", "위치번호", "위치 번호", "Location"]:
            if col in row and pd.notna(row[col]):
                location = str(row[col]).strip()
                break

        # 순번
        num = ""
        for col in ["번호", "순번", "No"]:
            if col in row and pd.notna(row[col]):
                num = str(row[col]).strip()
                break

        # 워드 파일 자동 탐색 및 해설 추출
        doc_path, w_artist, w_title, w_desc = get_docx_data(location)

        # 앨범명
        title = ""
        for col in ["앨범명", "제목", "음반명", "Album"]:
            if col in row and pd.notna(row[col]):
                title = str(row[col]).strip()
                break
        if not title:
            title = w_title if w_title else "제목 없음"

        # 아티스트명
        artist = ""
        for col in ["아티스트명", "아티스트", "가수", "가수명", "Artist"]:
            if col in row and pd.notna(row[col]):
                artist = str(row[col]).strip()
                break
        if not artist:
            artist = w_artist

        clean_content = clean_markdown_text(w_desc)

        # 화면 출력
        display_artist = f" - {artist}" if artist and artist != "nan" else ""
        st.subheader(f"💿 {title}{display_artist}")

        info_meta = []
        if num and num != "nan":
            info_meta.append(f"번호 : {num}")
        if location and location != "nan":
            info_meta.append(f"위치 : {location}")
        if info_meta:
            st.caption(" | ".join(info_meta))

        # 해설 바로 출력
        if True: # f"📖 [위치: {location}] 해설 열기"):
            if doc_path and os.path.exists(doc_path):
                if st.button(f"📄 워드 원본 문서 직접 열기", key=f"btn_{idx}_{location}"):
                    pass

            if clean_content and clean_content != "nan":
                st.write(clean_content)
            else:
                st.write("해설 문서를 불러오는 중이거나 내용이 비어 있습니다.")

        st.markdown("---")