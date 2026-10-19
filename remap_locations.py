import os
import re
import json
import pandas as pd

# 1. 엑셀 파일 읽기
excel_path = "lp_list.xlsx"
df = pd.read_excel(excel_path)

# 2. JSON 데이터베이스 불러오기
json_path = "lp_database.json"
if os.path.exists(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        db = json.load(f)
else:
    db = []

# 3. 아티스트/앨범명을 기준으로 새 위치 번호 매핑 (AI 호출 없이 텍스트만 갱신)
for item in db:
    # 기존 항목에서 가수나 앨범명 추출
    item_text = " ".join([str(v) for v in item.values() if v is not None])
    
    # 엑셀과 대조하여 새 번호로 덮어쓰기
    for idx, row in df.iterrows():
        album_name = str(row.get("앨범명", "")).strip()
        new_loc = str(row.get("위치", "")).strip()
        
        if album_name and album_name in item_text:
            # 기존 본문 안의 위치 번호 텍스트를 새 번호로 변경
            for k, v in item.items():
                if "위치" in str(k) or "loc" in str(k).lower():
                    item[k] = new_loc
                elif isinstance(v, str) and "위치" in v:
                    item[k] = re.sub(r'위치\s*[:_]?\s*@?\d+', f'위치: @{new_loc}', v)

# 4. 갱신된 JSON 저장 (토큰 소모 0원)
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(db, f, ensure_ascii=False, indent=2)

print("기존 음반 위치 번호가 AI 호출 없이 성공적으로 갱신되었습니다.")