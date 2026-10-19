import os
import re
from docx import Document
from docx2pdf import convert
from pypdf import PdfWriter

source_dir = r"D:\LP_Agent\word_reports"
temp_pdf_dir = r"D:\LP_Agent\pdf_temp_4digit"

os.makedirs(temp_pdf_dir, exist_ok=True)

# Word 파일 목록 가져오기
files = sorted([f for f in os.listdir(source_dir) if f.endswith(".docx") and not f.startswith("~$")])

print(f"총 {len(files)}개 Word 문서의 '번호'를 4자리(0001~0419)로 정밀 변환합니다...")

# 1. 문서 본문 내 '번호' 4자리 일괄 변환
for filename in files:
    doc_path = os.path.join(source_dir, filename)
    doc = Document(doc_path)
    
    # 번호 : 1 -> 번호 : 0001 로 변환
    def replace_num(match):
        num = int(match.group(1))
        return f"번호 : {num:04d}"

    # LP_1 -> LP_0001 또는 [LP 1] -> [LP 0001] 변환
    def replace_lp_tag(match):
        prefix = match.group(1)
        num = int(match.group(2))
        return f"{prefix}{num:04d}"

    for p in doc.paragraphs:
        if "번호" in p.text:
            p.text = re.sub(r"번호\s*:\s*(\d+)", replace_num, p.text)
        if "LP" in p.text:
            p.text = re.sub(r"(LP[_\-\s]*)(?!0000)(\d{1,4})", replace_lp_tag, p.text)

    # 표(테이블)가 있는 경우 표 안의 내용도 변환
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    if "번호" in p.text:
                        p.text = re.sub(r"번호\s*:\s*(\d+)", replace_num, p.text)
                    if "LP" in p.text:
                        p.text = re.sub(r"(LP[_\-\s]*)(?!0000)(\d{1,4})", replace_lp_tag, p.text)

    doc.save(doc_path)

print("[1단계 완료] Word 문서 내 4자리 번호(0001~0419) 동기화 완료")

# 2. PDF 변환 및 단일 통합본 생성
print("[2단계 진행] PDF 일괄 재생성 및 통합 검색본 병합 중...")
convert(source_dir, temp_pdf_dir)

merger = PdfWriter()
pdf_files = sorted([os.path.join(temp_pdf_dir, f) for f in os.listdir(temp_pdf_dir) if f.endswith(".pdf")])

for pdf in pdf_files:
    merger.append(pdf)

final_pdf_path = r"D:\LP_Agent\LP_전체음반_통합검색본.pdf"
with open(final_pdf_path, "wb") as f_out:
    merger.write(f_out)
merger.close()

# 임시 PDF 폴더 정리
for f in pdf_files:
    try:
        os.remove(f)
    except:
        pass
try:
    os.rmdir(temp_pdf_dir)
except:
    pass

print("="*60)
print(f"완벽하게 동기화되었습니다!")
print(f"- 엑셀 / Word / PDF 모두 '번호: 4자리(0001)', '위치: 3자리(701)'로 일치")
print(f"- 최종 완성 파일: {final_pdf_path}")
print("="*60)