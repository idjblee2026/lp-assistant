import os
import re
from docx import Document
from docx2pdf import convert
from pypdf import PdfWriter

source_dir = r"D:\LP_Agent\enhanced_reports"
temp_docx_dir = r"D:\LP_Agent\reports_connected_700"
temp_pdf_dir = r"D:\LP_Agent\pdf_temp_connected"

os.makedirs(temp_docx_dir, exist_ok=True)
os.makedirs(temp_pdf_dir, exist_ok=True)

files = sorted([f for f in os.listdir(source_dir) if f.startswith("LP_0") and f.endswith(".docx")])

# 1. 기존 파일들의 원본 위치 번호 파악
raw_locs = []
file_loc_map = {}

for filename in files:
    m = re.search(r"위치_(\d+)", filename)
    if m:
        loc = int(m.group(1))
        file_loc_map[filename] = loc
        raw_locs.append(loc)

# 100 미만 번호 중 가장 큰 번호 찾기
sub_100 = [loc for loc in raw_locs if loc < 100]
max_sub_100 = max(sub_100) if sub_100 else 0
next_start_for_700 = 700 + max_sub_100 + 1  # 100 미만이 끝난 바로 다음 700대 번호

# 700~722번 음반들에 새 번호 매핑 맵 생성
existing_700_series = sorted(list(set([loc for loc in raw_locs if 700 <= loc <= 722])))
reassign_700_map = {}
for i, old_loc in enumerate(existing_700_series):
    reassign_700_map[old_loc] = next_start_for_700 + i

print(f"1~99번 변환 범위: 701 ~ {700 + max_sub_100}")
if existing_700_series:
    print(f"기존 700~722번 재배치 범위: {next_start_for_700} ~ {next_start_for_700 + len(existing_700_series) - 1}")

# 2. Word 문서 본문 및 파일명 변경
for filename in files:
    doc_path = os.path.join(source_dir, filename)
    doc = Document(doc_path)
    old_loc = file_loc_map.get(filename, None)
    
    if old_loc is not None:
        if old_loc < 100:
            target_loc = old_loc + 700
        elif 700 <= old_loc <= 722:
            target_loc = reassign_700_map[old_loc]
        else:
            target_loc = old_loc
    else:
        target_loc = old_loc

    # 본문 텍스트 수정
    def replace_body(match):
        num = int(match.group(1))
        if num < 100:
            return f"위치 : {num + 700}"
        elif 700 <= num <= 722:
            return f"위치 : {reassign_700_map.get(num, num)}"
        return f"위치 : {num}"

    for p in doc.paragraphs:
        if "위치" in p.text:
            p.text = re.sub(r"위치\s*:\s*(\d+)", replace_body, p.text)

    # 파일명 변경
    new_filename = re.sub(r"위치_(\d+)", f"위치_{target_loc}", filename)
    new_doc_path = os.path.join(temp_docx_dir, new_filename)
    doc.save(new_doc_path)

print("[1단계 완료] 번호 충돌 없는 Word 문서 생성 완료 (위치: D:\\LP_Agent\\reports_connected_700)")

# 3. PDF 변환 및 통합 파일 생성
print("[2단계 진행] PDF 일괄 변환 및 단일 검색본 병합 중...")
convert(temp_docx_dir, temp_pdf_dir)

merger = PdfWriter()
pdf_files = sorted([os.path.join(temp_pdf_dir, f) for f in os.listdir(temp_pdf_dir) if f.endswith(".pdf")])

for pdf in pdf_files:
    merger.append(pdf)

final_pdf_path = r"D:\LP_Agent\LP_전체음반_통합검색본.pdf"
with open(final_pdf_path, "wb") as f_out:
    merger.write(f_out)
merger.close()

print("="*60)
print(f"완벽하게 정리되었습니다!")
print(f"통합 검색 PDF 파일: {final_pdf_path}")
print("="*60)