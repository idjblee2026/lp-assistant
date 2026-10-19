import os
import subprocess
import pandas as pd
import streamlit as st

st.set_page_config(page_title="나만의 LP 서재 AI 음악 비서", layout="wide")
st.title("📀 나만의 LP 서재 AI 음악 비서")

# 1. 엑셀 데이터 불러오기
try:
    df = pd.read_excel("lp_list.xlsx")
    df = df.fillna("")
except Exception as e:
    st.error(f"엑셀 파일을 읽을 수 없습니다: {e}")
    st.stop()

# 2. 검색창
keyword = st.text_input("🔍 음반 제목, 아티스트, 번호(위치), 또는 분위기를 검색하세요:", "").strip()
clean_k = keyword.replace("@", "").strip().lower()

# 3. 검색 필터링 (번호, 위치, 앨범명, 가수 등 모든 열 대상)
if clean_k:
    def is_match(row):
        for col in df.columns:
            val = str(row[col]).strip().lower()
            if val.endswith(".0"):
                val = val[:-2]
            if clean_k in val:
                return True
        return False
    filtered_df = df[df.apply(is_match, axis=1)]
else:
    filtered_df = df

st.write(f"### 총 {len(filtered_df)}개의 음반이 검색되었습니다.")

# 4. 음반 목록 출력
for idx, row in filtered_df.iterrows():
    loc = str(row.get("위치", "")).replace(".0", "")
    title = str(row.get("앨범명", ""))
    artist = str(row.get("아티스트", ""))
    num = str(row.get("번호", "")).replace(".0", "")
    genre = str(row.get("장르", ""))
    year = str(row.get("발매년도", "")).replace(".0", "")

    st.markdown("---")
    st.markdown(f"### :blue[[위치: @{loc}]] **{title} ({artist})**")
    st.caption(f"번호: {num} | 장르: {genre} | 발매년도: {year}")

    # 상세 해설 아코디언
    desc_col = [c for c in df.columns if any(k in str(c) for k in ["소개", "해설", "설명", "리뷰"])]
    if desc_col:
        desc_text = str(row.get(desc_col[0], "")).strip()
        if desc_text:
            with st.expander(f"💡 [위치: {loc}] 상세 해설 보기"):
                st.write(desc_text)

    # 원본 워드 문서 열기 버튼
    doc_path = ""
    for c in df.columns:
        v = str(row.get(c, "")).strip()
        if ".doc" in v.lower():
            doc_path = v
            break

    if not doc_path:
        for candidate in [f"{loc}.docx", f"{num}.docx", f"@{loc}.docx", f"{title}.docx"]:
            if os.path.exists(candidate):
                doc_path = candidate
                break

    if doc_path:
        if st.button(f"📄 [위치: @{loc}] 원본 워드 문서 열기", key=f"doc_btn_{idx}"):
            try:
                os.startfile(doc_path)
            except Exception:
                subprocess.Popen(["start", "", doc_path], shell=True)