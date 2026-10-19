import os
import glob
import re
from docx import Document
import pandas as pd

base_dir = r"D:\LP_Agent"
word_dir = os.path.join(base_dir, "word_reports")

files = glob.glob(os.path.join(word_dir, "*.docx"))
print(f"총 {len(files)}개의 워드 문서를 정밀 재분석하여 위치 번호를 3자리(001~)로 규격화합니다...")

records = []

for file_path in files:
    try:
        doc = Document(file_path)
        fname = os.path.basename(file_path).replace(".docx", "")
        
        loc = ""
        artist = ""
        album = ""
        label = ""
        year = ""
        genre = ""

        # 1. 파일명에서 정보 추출
        parts = fname.split("_")
        for i, p in enumerate(parts):
            if p == "위치" and i + 1 < len(parts):
                loc = parts[i+1].strip()
            elif p.isdigit() and not loc and len(p) <= 4:
                loc = p

        # 2. 문서 내 모든 표(Table) 정밀 분석
        for table in doc.tables:
            for row in table.rows:
                cells = [c.text.strip().replace("\n", " ") for c in row.cells]
                
                for idx, cell in enumerate(cells):
                    c_clean = cell.replace(" ", "")
                    # 위치
                    if any(k in c_clean for k in ["위치", "Location"]) and idx + 1 < len(cells):
                        val = cells[idx+1].replace("@", "").strip()
                        if val and not loc: loc = val
                    # 아티스트 / 가수
                    elif any(k in c_clean for k in ["아티스트", "가수", "Artist"]) and idx + 1 < len(cells):
                        val = cells[idx+1].strip()
                        if val and not artist: artist = val
                    # 앨범명 / 타이틀
                    elif any(k in c_clean for k in ["앨범명", "타이틀", "Album", "음반명"]) and idx + 1 < len(cells):
                        val = cells[idx+1].strip()
                        if val and not album: album = val
                    # 레이블
                    elif any(k in c_clean for k in ["레이블", "Label"]) and idx + 1 < len(cells):
                        val = cells[idx+1].strip()
                        if val and not label: label = val
                    # 발매년도
                    elif any(k in c_clean for k in ["발매년도", "발매일", "Year", "연도"]) and idx + 1 < len(cells):
                        val = cells[idx+1].strip()
                        if val and not year: year = val
                    # 장르
                    elif any(k in c_clean for k in ["장르", "Genre"]) and idx + 1 < len(cells):
                        val = cells[idx+1].strip()
                        if val and not genre: genre = val

        # 3. 표에서 못 찾았을 경우 파일명 패턴에서 보충
        if not artist or not album:
            m = re.search(r"위치_([0-9]+)_(.+?)_(.+)", fname)
            if m:
                if not loc: loc = m.group(1)
                if not artist: artist = m.group(2).strip()
                if not album: album = m.group(3).strip()

        # 4. 문서 본문 문단(Paragraphs)에서 추가 탐색
        if not artist or not album:
            for p in doc.paragraphs[:10]:
                text = p.text.strip()
                if "아티스트:" in text or "가수:" in text:
                    artist = text.split(":")[-1].strip()
                elif "앨범명:" in text:
                    album = text.split(":")[-1].strip()

        if loc:
            # 정렬을 위한 숫자 계산
            digits = re.findall(r"\d+", str(loc))
            loc_num = int(digits[0]) if digits else 9999
            
            # 위치 번호를 무조건 3자리(002, 013, 127) 형식의 문자열로 변환
            if digits:
                loc_formatted = f"{int(digits[0]):03d}"
            else:
                loc_formatted = str(loc)

            records.append({
                "loc_num": loc_num,
                "위치": loc_formatted,
                "Artists": artist,
                "앨범명": album,
                "레이블": label,
                "발매년도": year,
                "장르": genre
            })
    except Exception as e:
        print(f"오류 ({os.path.basename(file_path)}): {e}")

# 위치 번호 기준 올림차순 정렬
records.sort(key=lambda x: (x["loc_num"], str(x["위치"])))

final_data = []
for idx, r in enumerate(records, 1):
    final_data.append({
        "번호": f"{idx:04d}",
        "위치": str(r["위치"]),
        "Artists": r["Artists"],
        "앨범명": r["앨범명"],
        "레이블": r["레이블"],
        "발매년도": r["발매년도"],
        "장르": r["장르"]
    })

df = pd.DataFrame(final_data)

# 엑셀 저장 시 텍스트 형식으로 온전하게 3자리 보존
output_path = os.path.join(base_dir, "lp_list.xlsx")
with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
    df.to_excel(writer, index=False)

print("\n" + "="*50)
print(f"🎉 총 {len(final_data)}장의 LP 정보가 추출되었습니다!")
print("★ 번호는 4자리(0001~), 위치는 3자리(001~)로 완벽하게 규격화되었습니다.")
print(f"저장 파일: {output_path}")
print("="*50)