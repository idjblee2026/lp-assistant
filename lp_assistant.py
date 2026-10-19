import os
import re
import json
from docx import Document

INDEX_FILE = r"D:\LP_Agent\lp_database.json"
SOURCE_DIR = r"D:\LP_Agent\word_reports"

def build_or_load_database():
    if os.path.exists(INDEX_FILE):
        print("기존에 생성된 LP 지식 베이스를 빠르게 불러옵니다...")
        with open(INDEX_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    
    print("419개 워드 해설 문서를 정밀 분석하여 AI 음악 비서 데이터베이스를 구축합니다...")
    files = sorted([f for f in os.listdir(SOURCE_DIR) if f.endswith(".docx") and not f.startswith("~$")])
    database = []
    
    for filename in files:
        doc_path = os.path.join(SOURCE_DIR, filename)
        try:
            doc = Document(doc_path)
            full_text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
            
            # 위치 추출
            m_loc = re.search(r"위치\s*:\s*[@NL]?(\d+)", full_text)
            loc = m_loc.group(1) if m_loc else ""
            if not loc:
                m_fn = re.search(r"위치_(\d+)", filename)
                loc = m_fn.group(1) if m_fn else "미확인"
                
            # 앨범명 추출
            m_album = re.search(r"앨범명\s*:\s*([^\n]+)", full_text)
            album = m_album.group(1).strip() if m_album else filename.replace(".docx", "")
            
            # 아티스트 추출
            m_art = re.search(r"아티스트\s*:\s*([^\n]+)", full_text)
            artist = m_art.group(1).strip() if m_art else "미확인"
            
            # 레이블 추출
            m_lb = re.search(r"음반\s*레이블\s*:\s*([^\n|]+)", full_text)
            label = m_lb.group(1).strip() if m_lb else ""
            
            # 발매년도 추출
            m_yr = re.search(r"발매년도\s*:\s*(\d{4})", full_text)
            year = m_yr.group(1) if m_yr else ""
            
            # 음반 소개 요약 추출
            m_intro = re.search(r"음반\s*소개\s*:\s*([^\n]+)", full_text)
            intro = m_intro.group(1).strip() if m_intro else full_text[:150]
            
            database.append({
                "filename": filename,
                "location": loc,
                "album": album,
                "artist": artist,
                "label": label,
                "year": year,
                "intro": intro,
                "full_text": full_text
            })
        except Exception as e:
            continue
            
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(database, f, ensure_ascii=False, indent=2)
        
    print(f"총 {len(database)}개 음반의 AI 지식 베이스 구축이 완료되었습니다!")
    return database

def search_lp(query, database):
    # 키워드 매핑 및 의미 확장
    synonyms = {
        "비": ["비", "감성", "서정", "발라드", "비오는", "차분한", "멜로디", "우수"],
        "재즈": ["재즈", "jazz", "색소폰", "트럼펫", "스윙", "마일즈", "콜트레인"],
        "클래식": ["교향곡", "협주곡", "소나타", "오케스트라", "바이올린", "첼로", "필하모닉", "심포니"],
        "조용한": ["어쿠스틱", "피아노", "발라드", "서정", "차분", "밤", "새벽"],
        "모타운": ["motown", "모타운", "소울", "r&b"],
        "비틀즈": ["beatles", "비틀즈", "폴 매카트니", "존 레논", "apple records", "애플 레코드"]
    }
    
    q_words = query.lower().split()
    expanded_words = set(q_words)
    for w in q_words:
        for k, syn_list in synonyms.items():
            if k in w:
                expanded_words.update(syn_list)
                
    results = []
    for item in database:
        score = 0
        text_lower = item["full_text"].lower()
        
        # 앨범명, 아티스트, 레이블 일치 시 가중치
        for w in q_words:
            if w in item["album"].lower():
                score += 15
            if w in item["artist"].lower():
                score += 15
            if item["label"] and w in item["label"].lower():
                score += 10
            if item["year"] and w in item["year"]:
                score += 10
            if w == item["location"]:
                score += 50
                
        # 본문 내용 매칭
        for w in expanded_words:
            if w in text_lower:
                score += text_lower.count(w)
                
        if score > 0:
            results.append((score, item))
            
    results.sort(key=lambda x: x[0], reverse=True)
    return [r[1] for r in results[:5]]

def main():
    print("=" * 65)
    print("      📀 나만의 LP 서재 AI 음악 비서 (LP-Agent Chat) 📀")
    print("=" * 65)
    
    db = build_or_load_database()
    
    print("\n음악 비서가 준비되었습니다. 질문을 자유롭게 입력해 주세요.")
    print("- 예시: '비 오는 날 들을 감성적인 보컬 추천해줘'")
    print("- 예시: '모타운 레이블 음반 위치'", " '피아노 협주곡'", " '1984년 음반'")
    print("- 종료하시려면 'q' 또는 '종료'를 입력하세요.\n")
    
    while True:
        try:
            query = input("💬 질문 입력 >> ").strip()
            if not query:
                continue
            if query.lower() in ["q", "quit", "exit", "종료", "끝"]:
                print("\n음악 비서를 종료합니다. 즐거운 감상 시간 되세요!")
                break
                
            matched = search_lp(query, db)
            
            if not matched:
                print("\n🔍 관련된 음반을 서재에서 찾지 못했습니다. 다른 키워드로 물어봐 주세요.\n")
                continue
                
            print(f"\n✨ 소장 LP 서재에서 {len(matched)}장의 최적 음반을 추천해 드립니다:\n")
            for i, lp in enumerate(matched, 1):
                loc_tag = f"[위치 : {lp['location']}]"
                print(f"{i}. {loc_tag} {lp['artist']} - 《{lp['album']}》")
                if lp['label'] or lp['year']:
                    info = []
                    if lp['label']: info.append(f"레이블: {lp['label']}")
                    if lp['year']: info.append(f"발매년도: {lp['year']}")
                    print(f"   * {' | '.join(info)}")
                if lp['intro']:
                    # 100자 내외 요약
                    summary = lp['intro'][:120] + "..." if len(lp['intro']) > 120 else lp['intro']
                    print(f"   * 해설 요약: {summary}")
                print("-" * 60)
            print()
        except KeyboardInterrupt:
            print("\n음악 비서를 종료합니다.")
            break

if __name__ == "__main__":
    main()