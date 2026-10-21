import os
import re
import docx
from docx.shared import Pt, RGBColor, Inches
from docx.oxml.ns import qn

BASE_DIR = r"D:\LP_Agent"
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

def save_word_doc(location, artist, album, full_text, target_filepath):
    doc = docx.Document()
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.9)
        section.right_margin = Inches(0.9)

    lines = [line.strip() for line in full_text.split("\n") if line.strip()]
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
        if not clean_line or clean_line == first_line or clean_line.startswith("위치 :"):
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
            p.paragraph_format.space_after = Pt(6)
            parts = clean_line.split("]", 1)
            r_tag = p.add_run(parts[0] + "] ")
            set_font(r_tag, size_pt=11, bold=True, color=RGBColor(31, 41, 55))
            if len(parts) > 1 and parts[1].strip():
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
    print(f"✨ [496번 1,000자 장문 리포트 갱신 성공] -> {os.path.basename(target_filepath)}")

# 130번 케니 G와 동일한 격조와 3대 단락 1,000자 정통 평론 문안
MILLI_VANILLI_1000 = """Milli Vanili (밀리 바닐리) - Baby Don't Forget My Number
위치 : 496

[음반 소개]
1980년대 후반 전 세계 팝 음악계의 지형도를 단숨에 뒤흔들며 화려하게 등장했던 밀리 바닐리(Milli Vanilli)의 기념비적인 댄스 팝 명작입니다. 유럽 디스코 씬의 거장 프로듀서 프랑크 파리안(Frank Farian)의 정교하고 감각적인 프로듀싱과 롭 필라투스, 팹 모르반의 압도적인 시각적 매력이 결합하여 탄생한 이 음반은, 발매와 동시에 미국 빌보드 핫 100 정상을 정복하며 MTV 시대를 상징하는 찬란한 아이콘으로 군림했습니다. 경쾌하게 요동치는 베이스라인과 중독성 넘치는 멜로디의 훅은 당대 대중들이 갈망하던 세련된 도회적 낭만과 댄스 플로어의 열기를 완벽하게 직조해낸 결과물이었습니다.

당대 대중음악사에서 본 작은 팝 역사상 가장 화려하면서도 비극적인 드라마를 품고 있는 독보적인 작품입니다. 훗날 밝혀진 세기의 립싱크 파문과 그래미 신인상 반납이라는 전무후무한 스캔들의 소용돌이에 휘말렸으나, 그러한 논란의 장막 너머에 존재하는 음악 자체의 완성도는 당대 유로 팝과 미국식 알앤비 댄스가 도달할 수 있었던 상업적·예술적 절정을 여실히 입증합니다. 스튜디오 세션 보컬리스트들의 탄탄하고 소울풀한 가창력, 한 치의 오차도 없이 맞물려 돌아가는 아날로그 신디사이저 편곡은 단순한 기획 상품을 넘어선 시대의 탁월한 음악적 유산임을 증명하고 있습니다.

세월이 흘러 디지털 음원이 범람하는 오늘날에도 《Baby Don't Forget My Number》의 검은 바이닐 그루브가 회전할 때 뿜어져 나오는 생명력은 결코 빛바래지 않는 온기를 전합니다. 화려했던 80년대 말의 공기와 청춘들의 순수했던 열정, 그리고 팝 음악 비즈니스의 빛과 그림자를 고스란히 간직한 채 턴테이블 바늘을 타고 흐르는 묵직한 아날로그 사운드는, 단순한 유행가를 넘어 지나간 시대의 찬란한 단면을 회고하게 만드는 각별한 울림을 선사합니다.

1. 음반 데이터
· 앨범명: Baby Don't Forget My Number
· 아티스트: Milli Vanili (밀리 바닐리)
· 발매 정보: 1988년 Arista 레코드 발매, 미국 빌보드 핫 100 1위를 기록한 글로벌 히트 앨범
· LP 인기도(판매량): 미국 내 600만 장 이상(6x 플래티넘) 판매, 전 세계 수천만 장의 판매고를 기록한 메가 히트작
· 각종 수상경력: 제32회 그래미 어워드 최우수 신인상 수상(이후 반납) 및 아메리칸 뮤직 어워드 다수 석권

2. 아티스트 정보
· 국적: 독일 / 프랑스 (유럽 연합)
· 생몰년도: 1988년 결성
· 그룹 소속: 팝/댄스 듀오
· 아티스트 소개: 감각적인 스타일과 유로 댄스 비트로 80년대 후반 팝 음악계의 판도를 바꾼 전설의 프로젝트 듀오입니다.

3. 음반 상세 분석
· 역사적 위치: MTV 시각 문화와 유로 댄스 음악이 결합하여 전 세계 팝 차트를 정복한 상업적 정점의 모델입니다.
· 시대의 흔적(스토리텔링): 화려했던 80년대 말 팝 음악의 황금기와 쇼비즈니스의 이면을 동시에 간직한 시대의 타임캡슐입니다.

4. 주요 수록곡 및 감상 제언
· 주요 수록곡 특징: 빌보드 1위곡 'Baby Don't Forget My Number'의 세련된 베이스라인과 중독적인 코러스의 매력
· 빈티지 감상 제언: LP 그루브 깊숙한 곳에서 울려 퍼지는 두툼하고 탄력적인 베이스와 신스 사운드가 진공관 오디오의 배음과 만나 깊은 현장감을 재현합니다.
· 소장 가치: 대중음악사의 가장 극적인 사건을 증언하는 상징적인 명반이자 오리지널 아날로그 사운드의 진수를 담은 필청 바이닐입니다.

이 음반을 통해 아날로그 턴테이블이 전해주는 찬란했던 80년대 팝의 감동을 다시 한번 경험해 보시는 것은 어떨까요?
"""

def main():
    existing_files = os.listdir(WORD_DIR)
    target_path = None
    for f in existing_files:
        if "_496_" in f or f.startswith("위치_496") or f.startswith("496_"):
            target_path = os.path.join(WORD_DIR, f)
            break

    if not target_path:
        target_path = os.path.join(WORD_DIR, "위치_496_Milli Vanili (밀리 바닐리)_Baby Don't Forget My Number.docx")

    save_word_doc("496", "Milli Vanili (밀리 바닐리)", "Baby Don't Forget My Number", MILLI_VANILLI_1000, target_path)

    cache_file = os.path.join(BASE_DIR, "lp_database.json")
    if os.path.exists(cache_file):
        try:
            os.remove(cache_file)
        except Exception:
            pass

    print("\n🎉 496번이 130번(케니 G)과 완벽히 동일한 정통 1,000자 양식으로 교체되었습니다!")
    input("\n엔터(Enter) 키를 누르면 종료됩니다...")

if __name__ == "__main__":
    main()