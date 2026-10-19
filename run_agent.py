import os
import re
import time
import pandas as pd
import docx
from docx.shared import Pt, RGBColor, Inches
from docx.oxml.ns import qn
from google import genai

# ==========================================
# 1. 환경 설정 및 API 연결
# ==========================================
api_key = "AQ.Ab8RN6Ih8-Uo7PhIPOyNq6PwegslaIB4PGfFmuZDNoZRteVcYg"
client = genai.Client(api_key=api_key)

BASE_DIR = r"D:\LP_Agent"
EXCEL_FILE = os.path.join(BASE_DIR, "lp_list.xlsx")
WORD_DIR = os.path.join(BASE_DIR, "word_reports")
os.makedirs(WORD_DIR, exist_ok=True)

def set_font(run, font_name="맑은 고딕", size_pt=10, bold=False, color=None):
    run.font.name = font_name
    run._r.get_or_add_rPr().set(qn('w:rFonts'), font_name)
    run._r.get_or_add_rPr().rFonts.set(qn('w:eastAsia'), font_name)
    run.font.size = Pt(size_pt)
    run.font.bold = bold
    if color:
        run.font.color.rgb = color

def generate_lp_content(location, artist, album):
    prompt = f"""
다음 LP 음반에 대한 정확한 발매 정보와 음악 해설을 한국어로 품격 있게 작성해 주세요.
[음반 기본 정보]
- 위치(번호): {location}
- 아티스트: {artist}
- 앨범명: {album}

반드시 아래 5가지 태그 형식에 맞춰 누락 없이 채워주세요:
[레이블]: (음반 발매 레이블명, 예: Columbia, Decca, Motown 등)
[발매년도]: (최초 발매년도 4자리 숫자, 예: 1978)
[장르]: (음악 장르)
[수록곡]: (대표적인 주요 수록곡 4~6곡 목록)
[음반 및 곡 해설]: (이 음반의 배경, 음악적 가치, 연주/보컬 특징, 감상 포인트를 3~4문단으로 상세히 작성)
"""
    for model_name in ['gemini-3.6-flash', 'gemini-2.5-pro', 'gemini-1.5-flash']:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt
            )
            if response and response.text:
                return response.text
        except Exception:
            continue
    return ""

def save_word_doc(location, artist, album, ai_text, target_filepath):
    doc = docx.Document()
    for section in doc.sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)

    p_title = doc.add_paragraph()
    r_title = p_title.add_run(f"[{location}] {artist} - {album}")
    set_font(r_title, size_pt=15, bold=True, color=RGBColor(30, 58, 138))
    p_title.paragraph_format.space_after = Pt(14)

    label = re.search(r"\[레이블\]\s*:\s*(.*)", ai_text)
    year = re.search(r"\[발매년도\]\s*:\s*(.*)", ai_text)
    genre = re.search(r"\[장르\]\s*:\s*(.*)", ai_text)
    tracks = re.search(r"\[수록곡\]\s*:\s*(.*)", ai_text)
    
    label_str = label.group(1).strip() if label else "미확인"
    year_str = year.group(1).strip() if year else "미확인"
    genre_str = genre.group(1).strip() if genre else "미확인"
    tracks_str = tracks.group(1).strip() if tracks else ""

    meta_p = doc.add_paragraph()
    set_font(meta_p.add_run(f"■ 위치 : {location}\n"), bold=True)
    set_font(meta_p.add_run(f"■ 아티스트 : {artist}\n"), bold=True)
    set_font(meta_p.add_run(f"■ 앨범명 : {album}\n"), bold=True)
    set_font(meta_p.add_run(f"■ 음반 레이블 : {label_str}\n"))
    set_font(meta_p.add_run(f"■ 발매년도 : {year_str}\n"))
    set_font(meta_p.add_run(f"■ 장르 : {genre_str}\n"))
    if tracks_str:
        set_font(meta_p.add_run(f"■ 주요 수록곡 : {tracks_str}\n"))
    meta_p.paragraph_format.space_after = Pt(16)

    desc_match = re.search(r"\[음반 및 곡 해설\]\s*:\s*([\s\S]*)", ai_text)
    desc_text = desc_match.group(1).strip() if desc_match else ai_text

    p_sub = doc.add_paragraph()
    r_sub = p_sub.add_run("■ 음반 해설 및 감상 가이드")
    set_font(r_sub, size_pt=12, bold=True, color=RGBColor(31, 41, 55))
    p_sub.paragraph_format.space_after = Pt(8)

    for line in desc_text.split("\n"):
        if line.strip():
            p_desc = doc.add_paragraph()
            r_desc = p_desc.add_run(line.strip())
            set_font(r_desc, size_pt=10.5)
            p_desc.paragraph_format.line_spacing = 1.3
            p_desc.paragraph_format.space_after = Pt(6)

    doc.save(target_filepath)
    print(f"✨ 워드 생성 완료: {os.path.basename(target_filepath)}")

def main():
    print("=" * 65)
    print("📀 LP AI 에이전트 - 정확한 위치/아티스트 매칭 생성기 📀")
    print("=" * 65)

    if not os.path.exists(EXCEL_FILE):
        print(f"엑셀 파일({EXCEL_FILE})을 찾을 수 없습니다.")
        input("엔터를 누르면 종료됩니다...")
        return

    try:
        df = pd.read_excel(EXCEL_FILE)
    except Exception as e:
        print(f"엑셀 읽기 오류: {e}")
        input("엔터를 누르면 종료됩니다...")
        return

    # 컬럼 정확 매칭 (위치, Artists/아티스트, 앨범명)
    col_loc = next((c for c in df.columns if str(c).strip() == "위치"), None)
    if not col_loc:
        col_loc = next((c for c in df.columns if "위치" in str(c)), df.columns[1])

    col_art = next((c for c in df.columns if str(c).strip().lower() in ["artists", "artist", "아티스트", "가수"]), None)
    if not col_art:
        col_art = df.columns[2]

    col_alb = next((c for c in df.columns if str(c).strip().lower() in ["앨범명", "앨범", "음반명", "album", "title"]), None)
    if not col_alb:
        col_alb = df.columns[3]

    existing_files = os.listdir(WORD_DIR)
    targets = []

    print(f"매칭 기준 컬럼 확인: [위치: {col_loc}] | [아티스트: {col_art}] | [앨범명: {col_alb}]")
    print("빈칸 검사 중...")

    for _, row in df.iterrows():
        loc = str(row[col_loc]).strip().replace(".0", "")
        art = str(row[col_art]).strip() if pd.notna(row[col_art]) else "Various Artists"
        alb = str(row[col_alb]).strip() if pd.notna(row[col_alb]) else ""

        if not alb or alb.lower() == "nan":
            continue

        matched_file = None
        for f in existing_files:
            if f"_{loc}_" in f or f"위치_{loc}_" in f or f"LP_{loc}_" in f or f.startswith(f"{loc}_") or f.startswith(f"위치_{loc}."):
                matched_file = f
                break

        need_update = False
        target_path = ""

        if not matched_file:
            need_update = True
            safe_album = re.sub(r'[\\/*?:"<>|]', "", alb).strip()
            safe_artist = re.sub(r'[\\/*?:"<>|]', "", art).strip()
            target_path = os.path.join(WORD_DIR, f"위치_{loc}_{safe_artist}_{safe_album}.docx")
        else:
            target_path = os.path.join(WORD_DIR, matched_file)
            try:
                doc = docx.Document(target_path)
                full = "\n".join([p.text for p in doc.paragraphs])
                if "음반 레이블 :\n" in full or "음반 레이블 : \n" in full or "음반 레이블 : \t" in full or "발매년도 :\n" in full or "음반 레이블 :  " in full or "발매년도 :  " in full or "미확인" in full:
                    need_update = True
            except Exception:
                pass

        if need_update:
            targets.append((loc, art, alb, target_path))

    print(f"\n👉 AI가 정보를 채워넣어야 할 음반: 총 {len(targets)}개\n")

    for i, (loc, art, alb, target_path) in enumerate(targets, 1):
        print(f"[{i}/{len(targets)}] 🔍 AI 검색 및 작성 중 -> [{loc}] {art} - {alb}")
        ai_res = generate_lp_content(loc, art, alb)
        if ai_res:
            save_word_doc(loc, art, alb, ai_res, target_path)
        time.sleep(1.2)

    cache_file = os.path.join(BASE_DIR, "lp_database.json")
    if os.path.exists(cache_file):
        os.remove(cache_file)

    print("\n🎉 모든 빈칸 채우기 및 워드 문서 작성이 완료되었습니다!")
    input("\n엔터(Enter) 키를 누르면 종료됩니다...")

if __name__ == "__main__":
    main()