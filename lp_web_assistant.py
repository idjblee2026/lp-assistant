import streamlit as st
import json

st.set_page_config(page_title="나만의 LP 서재", page_icon="🎵", layout="wide")

@st.cache_data
def load_data():
    with open("lp_database.json", "r", encoding="utf-8") as f:
        return json.load(f)

try:
    data = load_data()
    st.title("🎵 나만의 LP 서재")
    
    query = st.text_input("🔍 검색 (선반 번호, 작곡가, 연주자, 앨범명, 곡명 등):", "").strip()
    
    if query:
        results = []
        
        # 1. 숫자 검색 (선반 위치 번호)
        if query.isdigit():
            for item in data:
                if str(item.get("location")) == str(int(query)):
                    results.append(item)
                    
        # 2. 일반 텍스트 검색
        if not results:
            for item in data:
                text_all = f"{item.get('album', '')} {item.get('artist', '')} {item.get('content', '')} {item.get('full_text', '')} {item.get('raw_content', '')}"
                if query.lower() in text_all.lower():
                    results.append(item)
        
        st.write(f"검색 결과: 총 **{len(results)}**건")
        
        if results:
            for item in results:
                loc = item.get("location", "-")
                artist = item.get("artist", "아티스트 미상")
                album = item.get("album", "앨범명 없음")
                
                # 본문 해설 내용 찾아서 가져오기
                content = item.get("full_text") or item.get("raw_content") or item.get("content") or "상세 정보가 없습니다."
                
                with st.expander(f"📍 [위치: {loc}번] {artist} - {album}", expanded=True):
                    st.markdown(f"### 📍 보관 위치: **{loc}번 선반**")
                    st.markdown(f"**아티스트:** {artist}")
                    st.markdown(f"**앨범명:** {album}")
                    st.markdown("---")
                    st.markdown("#### 🎼 수록곡 및 음반 해설")
                    st.write(content)
        else:
            st.info("검색 결과가 없습니다.")
    else:
        st.write(f"전체 소장 LP: **{len(data)}**장")
        st.dataframe(data, use_container_width=True)

except Exception as e:
    st.error(f"오류가 발생했습니다: {e}")
