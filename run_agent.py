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

def set_font(run, font_name="맑은 고딕", size_pt=10.5, bold=False, color=None):
    run.font.name = font_name
    run._r.get_or_add_rPr().set(qn('w:rFonts'), font_name)
    run._r.get_or_add_rPr().rFonts.set(qn('w:eastAsia'), font_name)
    run.font.size = Pt(size_pt)
    run.font.bold = bold
    if color:
        run.font.color.rgb = color

def generate_lp_content(location, artist, album):
    prompt = f"""
당신은 대한민국 최고의 정통 LP 음악 평론가입니다.
제공된 LP 음반에 대해 클래식/팝 애호가를 위한 격조 높고 서정적인 해설 평가서를 작성해 주세요.
반드시 아래의 항목 번호와 제목 형식을 한 글자도 바꾸지 말고 그대로 유지해 작성해 주세요.

[음반 기본 정보]
- 위치: {location}
- 아티스트: {artist}
- 앨범명: {album}

[작성 양식 가이드]
{artist} - {album}
위치 : {location}

[음반 소개] (해당 음반의 음악사적 가치와 감동을 품격 있고 서정적인 문체로 3~4문장으로 서술)

1. 음반 데이터
· 앨범명: {album}
· 아티스트: {artist}
· 발매 정보: (발매 배경 및 앨범의 역사적 성격을 정중하고 품격 있게 서술)
· LP 인기도(판매량): (발매 당시 차트 성적, 대중적 인기 및 상업적 기록 서술)
· 각종 수상경력: (수상 내역 및 음악계의 공인된 평가와 권위 서술)

2. 아티스트 정보
· 국적: (국적)
· 생몰년도: (생몰년도 또는 결성 연도)
· 그룹 소속: (솔로 또는 그룹 형태)
· 아티스트 소개: (아티스트의 음악적 독창성과 팝 역사에서의 위상을 2~3문장으로 서술)

3. 음반 상세 분석
· 역사적 위치: (팝/음악사적 관점에서 이 앨범이 갖는 완성도와 의의 서술)
· 시대의 흔적(스토리텔링): (당시 시대상, 청춘들의 문화적 공기와 정서적 감성을 담아 서술)

4. 주요 수록곡 및 감상 제언
· 주요 수록곡 특징: (대표 명곡들을 언급하고 각 곡의 음악적 매력과 서정성을 서술)
· 빈티지 감상 제언: (LP 특유의 따뜻하고 풍성한 아날로그 사운드, 진공관 앰프/턴테이블 음향 특성에 맞춘 감상 포인트 서술)
· 소장 가치: (LP 컬렉터 관점에서 이 음반을 소장해야 하는 가치 서술)

(마지막 줄은 "이 음반을 통해 ~ 전해주는 감동을 다시 한번 경험해 보시는 것은 어떨까요?" 형태의 따뜻한 권유형 문장 한 줄로 마무리)
"""
    for model_name in ['gemini-2.5-pro', 'gemini-1.5-flash']:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt
            )
            if response and response.text:
                return response.text.strip()
        except Exception:
            continue
    return ""

def save_word_doc(location, artist, album, ai_text, target_filepath):
    doc = docx.Document()
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.9)
        section.right_margin = Inches(0.9)

    lines = [line.strip() for line in ai_text.split("\n") if line.strip()]
    if not lines:
        return

    first_line = lines[0].replace("#", "").strip()
    p_title = doc.add_paragraph()
    r_title = p_title.add_run(first_line)
    set_font(r_title, size_pt=15, bold=True, color=RGBColor(30, 58, 138))
    p_title.paragraph_format.space_after = Pt(4)

    p_loc = doc.add_paragraph()
    r_loc = p_loc.add_run(f"위치 :  {location}")
    set_font(r_loc, size_pt=11, bold=True, color=RGBColor(75, 85, 99))
    p_loc.paragraph_format.space_after = Pt(12)

    for line in lines[1:]:
        clean_line = line.replace("#", "").strip()
        if not clean_line:
            continue

        if clean_line == first_line or clean_line.startswith("위치 :"):
            continue

        p = doc.add_paragraph()
        p.paragraph_format.line_spacing = 1.35

        if re.match(r"^\d+\.\s+", clean_line):
            r = p.add_run(clean_line)
            set_font(r, size_pt=12, bold=True, color=RGBColor(30, 58, 138))
            p.paragraph_format.space_before = Pt(10)
            p.paragraph_format.space_after = Pt(4)
        elif clean_line.startswith("[음반 소개]"):
            p.paragraph_format.space_before = Pt(4)
            p.paragraph_format.space_after = Pt(8)
            parts = clean_line.split("]", 1)
            r_tag = p.add_run(parts[0] + "] ")
            set_font(r_tag, size_pt=11, bold=True, color=RGBColor(31, 41, 55))
            if len(parts) > 1:
                r_body = p.add_run(parts[1].strip())
                set_font(r_body, size_pt=10.5)
        elif clean_line.startswith("·") or clean_line.startswith("-") or clean_line.startswith("*"):
            p.paragraph_format.space_after = Pt(4)
            bullet_clean = re.sub(r"^[·\-\*]\s*", "", clean_line)
            if ":" in bullet_clean or "：" in bullet_clean:
                delim = ":" if ":" in bullet_clean else "："
                k, v = bullet_clean.split(delim, 1)
                r_bullet = p.add_run("· ")
                set_font(r_bullet, size_pt=10.5, color=RGBColor(107, 114, 128))
                r_key = p.add_run(k.strip() + ": ")
                set_font(r_key, size_pt=10.5, bold=True, color=RGBColor(31, 41, 55))
                r_val = p.add_run(v.strip())
                set_font(r_val, size_pt=10.5)
            else:
                r_body = p.add_run("· " + bullet_clean)
                set_font(r_body, size_pt=10.5)
        else:
            p.paragraph_format.space_after = Pt(6)
            r_body = p.add_run(clean_line)
            if "어떨까요?" in clean_line or clean_line.endswith("?"):
                p.paragraph_format.space_before = Pt(8)
                set_font(r_body, size_pt=10.5, bold=True, color=RGBColor(67, 56, 202))
            else:
                set_font(r_body, size_pt=10.5)

    doc.save(target_filepath)
    print(f"✨ 품격 있는 워드 해설 생성 완료: {os.path.basename(target_filepath)}")

def main():
    print("=" * 65)
    print("📀 동암 LP 컬렉션 AI 에이전트 - 정통 해설 리포트 생성기 📀")
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

    print(f"매칭 기준 확인: [위치: {col_loc}] | [아티스트: {col_art}] | [앨범명: {col_alb}]")
    print("해설 리포트 필요 여부 점검 중...")

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
                if "1. 음반 데이터" not in full or "3. 음반 상세 분석" not in full or "미확인" in full:
                    need_update = True
            except Exception:
                need_update = True

        if need_update:
            targets.append((loc, art, alb, target_path))

    print(f"\n👉 새 양식으로 리포트를 작성할 음반: 총 {len(targets)}개\n")

    for i, (loc, art, alb, target_path) in enumerate(targets, 1):
        print(f"[{i}/{len(targets)}] 🔍 정통 해설 작성 중 -> [{loc}] {art} - {alb}")
        ai_res = generate_lp_content(loc, art, alb)
        if ai_res:
            save_word_doc(loc, art, alb, ai_res, target_path)
        time.sleep(1.2)

    cache_file = os.path.join(BASE_DIR, "lp_database.json")
    if os.path.exists(cache_file):
        try:
            os.remove(cache_file)
        except Exception:
            pass

    print("\n🎉 모든 정통 양식 워드 문서 작성이 완료되었습니다!")
    input("\n엔터(Enter) 키를 누르면 종료됩니다...")

if __name__ == "__main__":
    main()