import streamlit as st
import json

st.set_page_config(page_title="나만의 LP 서재 음악 비서", page_icon="🎵", layout="wide")

@st.cache_data
def load_data():
    with open("lp_database.json", "r", encoding="utf-8") as f:
        return json.load(f)

try:
    data = load_data()
    st.title("🎵 나만의 LP 서재 음악 비서")
    
    query = st.text_input("🔍 검색어를 입력하세요 (가수, 곡명, 앨범명, 위치 번호 등):", "")
    
    # 검색어 필터링
    if query:
        results = [item for item in data if query.lower() in " ".join([str(v) for v in item.values() if v]).lower()]
    else:
        results = data

    st.write(f"총 **{len(results)}**장의 음반이 있습니다. (제목을 터치하면 상세 정보가 열립니다)")
    st.divider()

    # 터치하면 펼쳐지는 상세 보기 상자
    for item in results:
        album_title = item.get("album", "앨범명 없음")
        artist = item.get("artist", "아티스트 미상")
        loc = item.get("location", "위치 미정")
        
        # 터치 가능한 아코디언 상자 생성
        with st.expander(f"📍 [위치 {loc}] {album_title} - {artist}"):
            st.markdown(f"**💿 앨범명:** {album_title}")
            st.markdown(f"**👤 아티스트:** {artist}")
            st.markdown(f"**📍 서재 보관 위치:** {loc}번")
            
            # 수록곡 및 파일 안의 모든 상세 내용 출력
            for key, val in item.items():
                if key not in ["album", "artist", "location", "filename"] and val:
                    st.markdown(f"**• {key}:** {val}")

except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
