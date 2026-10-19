import os
import re
from docx import Document
from docx2pdf import convert
from pypdf import PdfWriter

# 원본 폴더 및 작업 폴더 설정
source_dir = r"D:\LP_Agent\enhanced_reports"
temp_docx_dir = r"D:\LP_Agent\reports_700"
temp_pdf_dir = r"D:\LP_Agent\pdf_temp"

os.makedirs(temp_docx_dir, exist_ok=True)
os.makedirs(temp_pdf_dir, exist_ok=True)

# 4자리 최신 Word 파일 목록 (LP_0001 ~ LP_0419)
files = sorted([f for f in os.listdir(source_dir) if f.startswith("LP_0") and f.endswith(".docx")])

print(f"총 {len(files)}개 파일의 위치 번호(100 미만 -> 700대) 일괄 변환을 시작합니다...")

for idx, filename in enumerate(files, 1):
    doc_path = os.path.join(source_dir, filename)
    doc = Document(doc_path)
    
    # 1. 문서 본문 내 '위치 : 숫자' 변환 (100 미만 숫자를 700대로)
    def replace_loc_text(match):
        loc_num = int(match.group(1))
        if loc_num < 100:
            loc_num += 700
        return f"위치 : {loc_num}"

    for p in doc.paragraphs:
        if "위치" in p.text:
            p.text = re.sub(r"위치\s*:\s*(\d+)", replace_loc_text, p.text)

    # 2. 파일 이름 속 위치 번호도 변환 (예: 위치_18 -> 위치_718)
    def replace_loc_fname(match):
        loc_num = int(match.group(1))
        if loc_num < 100:
            loc_num += 700
        return f"위치_{loc_num}"

    new_filename = re.sub(r"위치_(\d+)", replace_loc_fname, filename)
    new_doc_path = os.path.join(temp_docx_dir, new_filename)
    doc.save(new_doc_path)

print("[1단계 완료] Word 문서 내 번호 및 파일명 변환 완료 (저장 위치: D:\\LP_Agent\\reports_700)")

# 3. PDF 변환 및 통합 파일 생성
print("[2단계 진행] PDF 변환 및 통합 검색 파일 생성 중 (잠시만 기다려주세요)...")
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
print(f"모든 작업이 완료되었습니다!")
print(f"1. 변경된 Word 문서 폴더: {temp_docx_dir}")
print(f"2. 완성된 통합 PDF 파일: {final_pdf_path}")
print("="*60)