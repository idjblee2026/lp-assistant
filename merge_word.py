import os
import pandas as pd
from docx import Document

BASE_DIR = r"D:\LP_Agent"
xl_path = os.path.join(BASE_DIR, "lp_list.xlsx")

print("1. 엑셀 파일 로딩 중...")
xl = pd.ExcelFile(xl_path)
sheet = "Sheet2" if "Sheet2" in xl.sheet_names else xl.sheet_names[0]
df = pd.read_excel(xl_path, sheet_name=sheet)

def get_docx_info(loc_num):
    clean_loc = str(loc_num).replace("@", "").strip()
    if not clean_loc or clean_loc == "nan":
        return "", "", ""
    
    target_names = [f"위치_{clean_loc}_", f"_{clean_loc}_", f"위치_{clean_loc}."]
    for root, dirs, files in os.walk(BASE_DIR):
        for f in files:
            if f.endswith(".docx") and not f.startswith("~$"):
                if any(t in f for t in target_names):
                    try:
                        doc = Document(os.path.join(root, f))
                        raw_paras = [p.text.replace("\x0b", "\n").strip() for p in doc.paragraphs if p.text.strip()]
                        lines = [line.strip() for p in raw_paras for line in p.split("\n") if line.strip()]
                        
                        artist = ""
                        title = ""
                        desc_lines = []
                        capture = False
                        
                        for line in lines:
                            if "아티스트" in line and ":" in line and not artist:
                                artist = line.split(":", 1)[1].strip()
                            elif "앨범명" in line and ":" in line and not title:
                                title = line.split(":", 1)[1].strip()
                            
                            if any(k in line for k in ["음반 해설", "감상 가이드", "음반 소개"]):
                                capture = True
                                continue
                            
                            if capture:
                                if any(line.startswith(k) for k in ["■ 위치", "■ 아티스트", "■ 앨범명", "■ 발매년도", "■ 주요 수록곡", "■ 음반 레이블"]):
                                    capture = False
                                else:
                                    desc_lines.append(line)
                        
                        if not desc_lines:
                            desc_lines = [l for l in lines if len(l) > 30 and not l.startswith("■")]
                            
                        desc_text = "\n\n".join(desc_lines) if desc_lines else "\n\n".join(lines)
                        return artist, title, desc_text
                    except Exception as e:
                        pass
    return "", "", ""

print("2. 400여 개 워드 파일에서 아티스트와 상세 해설 추출 중... (잠시만 기다려주세요)")

new_records = []
for idx, row in df.iterrows():
    loc = ""
    for c in ["위치", "위치번호", "위치 번호", "Location"]:
        if c in row and pd.notna(row[c]):
            loc = str(row[c]).strip()
            break
            
    num = ""
    for c in ["번호", "순번", "No"]:
        if c in row and pd.notna(row[c]):
            num = str(row[c]).strip()
            break
            
    title = ""
    for c in ["앨범명", "제목", "음반명", "Album"]:
        if c in row and pd.notna(row[c]):
            title = str(row[c]).strip()
            break
            
    artist = ""
    for c in ["아티스트명", "아티스트", "가수", "가수명", "Artist"]:
        if c in row and pd.notna(row[c]):
            artist = str(row[c]).strip()
            break
            
    genre = str(row.get("장르", "-")).strip()
    year = str(row.get("발매년도", "-")).strip()
    
    w_artist, w_title, w_desc = get_docx_info(loc)
    
    final_title = title if (title and title != "nan") else w_title
    final_artist = artist if (artist and artist != "nan") else w_artist
    
    new_records.append({
        "번호": num,
        "위치": loc,
        "앨범명": final_title,
        "아티스트": final_artist,
        "장르": genre,
        "발매년도": year,
        "음반 소개": w_desc
    })

clean_df = pd.DataFrame(new_records)

print("3. lp_list.xlsx에 새롭게 저장하는 중...")
clean_df.to_excel(xl_path, index=False)

print("\n" + "="*50)
print("★ 작업 완료! 모든 워드 해설과 아티스트가 lp_list.xlsx에 완벽하게 저장되었습니다.")
print("="*50)
input("\n엔터 키를 누르면 창이 닫힙니다...")