import streamlit as st
import json
import os

st.set_page_config(page_title="나만의 LP 서재 AI 음악 비서", page_icon="🎵", layout="wide")

@st.cache_data
def load_data():
    with open("lp_database.json", "r", encoding="utf-8") as f:
        return json.load(f)

def clean_text(text):
    if not isinstance(text, str):
        return text
    # 취소선 방지: 물결표(~)를 대시(-)로 변경
    return text.replace("~", "-")

try:
    data = load_data()
    st.title("🎵 나만의 LP 서재 AI 음악 비서")
    
    query = st.text_input("🔍 검색어를 입력하세요 (작곡가, 연주자, 앨범명, 곡명, 위치 등):", "")
    
    if query:
        results = []
        for item in data:
            item_str = " ".join([str(v) for v in item.values() if v])
            if query.lower() in item_str.lower():
                results.append(item)
        
        st.write(f"총 **{len(results)}**건이 검색되었습니다.")
        
        for idx, item in enumerate(results):
            title = item.get("album") or item.get("filename") or f"LP #{idx+1}"
            loc = item.get("location", "위치 미지정")
            artist = item.get("artist", "아티스트 미지정")
            
            with st.expander(f"📍 [위치: {loc}] {artist} - {title}", expanded=True):
                for k, v in item.items():
                    if v:
                        clean_v = clean_text(str(v))
                        st.markdown(f"**{k}**: {clean_v}")
    else:
        st.write(f"전체 등록된 LP: **{len(data)}**장")
        st.dataframe(data, use_container_width=True)

except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
