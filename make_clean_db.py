import os
import json
import re

db_file = "lp_database.json"
clean_data = []

if not os.path.exists(db_file):
    print("오류: lp_database.json 파일을 찾을 수 없습니다. D:\\LP_Agent 폴더를 확인해 주세요.")
else:
    with open(db_file, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    print(f"기존 데이터 총 {len(raw_data)}장을 정제합니다...")

    for item in raw_data:
        fn = str(item.get("filename", ""))
        raw_loc = str(item.get("location", ""))
        
        # 1. 파일명 및 필드에서 순수 위치 번호만 추출 (예: '위치_104' -> '104')
        loc_num = ""
        loc_match = re.search(r'위치[_\s:]*(\d+)', fn)
        if loc_match:
            loc_num = str(int(loc_match.group(1)))
        elif re.search(r'\d+', raw_loc):
            loc_num = str(int(re.search(r'\d+', raw_loc).group()))
        else:
            loc_num = "-"

        # 2. 본문 내용에서 불필요한 '@' 기호, 중복 '번호/위치' 텍스트 및 취소선(~) 정리
        full_text = str(item.get("full_text", item.get("content", "")))
        full_text = re.sub(r'@[0-9]+', '', full_text)
        full_text = re.sub(r'번호\s*:\s*@?\d+', '', full_text)
        full_text = re.sub(r'위치\s*:\s*@?\d+', '', full_text)
        full_text = full_text.replace("~", "-").strip()

        album = str(item.get("album", "")).replace("~", "-").strip()
        artist = str(item.get("artist", "")).replace("~", "-").strip()

        clean_data.append({
            "location": loc_num,       # 순수 숫자 위치 (예: '104')
            "album": album,           # 앨범명
            "artist": artist,         # 아티스트
            "content": full_text      # 정돈된 곡 목록 및 소개
        })

    # 위치 번호 순서대로 깔끔하게 정렬
    clean_data.sort(key=lambda x: int(x["location"]) if x["location"].isdigit() else 9999)

    # 새로운 정제 파일로 저장
    with open("lp_database_clean.json", "w", encoding="utf-8") as f:
        json.dump(clean_data, f, ensure_ascii=False, indent=2)

    print("=" * 50)
    print(f"정제 완료! 총 {len(clean_data)}장의 데이터가 새로 생성되었습니다.")
    print("생성된 파일명: lp_database_clean.json")
    print("=" * 50)