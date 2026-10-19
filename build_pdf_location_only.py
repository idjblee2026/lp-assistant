import os
import re
from docx import Document
from docx2pdf import convert
from pypdf import PdfWriter

source_dir = r"D:\LP_Agent\word_reports"
temp_docx_dir = r"D:\LP_Agent\docx_pdf_temp"
temp_pdf_dir = r"D:\LP_Agent\pdf_temp_clean"

os.makedirs(temp_docx_dir, exist_ok=True)
os.makedirs(temp_pdf_dir, exist_ok=True)

files = sorted([f for f in os.listdir(source_dir) if f.endswith(".docx") and not f.startswith("~$")])

print("워드 원본은 보존하고, PDF 전용으로 번호를 제거한 깔끔한 위치 번호 문서를 생성합니다...")

for filename in files:
    doc_path = os.path.join(source_dir, filename)
    doc = Document(doc_path)
    
    # 1. 문단에서 번호 라인 제거 및 위치 번호 정리 (순수 3자리 숫자)
    new_paras = []
    for p in list(doc.paragraphs):
        text = p.text
        # '번호 :'가 들어간 문단은 제거
        if "번호" in text and ":" in text:
            p._element.getparent().remove(p._element)
            continue
        
        # '위치 :' 문단은 @, L 등 기호를 모두 뺀 순수 숫자 형태로 복원
        if "위치" in text and ":" in text:
            p.text = re.sub(r"위치\s*:\s*[@NL]?(\d+)", r"위치 : \1", text)

    # 2. 표(Table) 내부의 번호 행 제거 및 위치 정리
    for table in doc.tables:
        rows_to_remove = []
        for row in table.rows:
            for cell in row.cells:
                for p in list(cell.paragraphs):
                    text = p.text
                    if "번호" in text and ":" in text:
                        p.text = ""
                    if "위치" in text and ":" in text:
                        p.text = re.sub(r"위치\s*:\s*[@NL]?(\d+)", r"위치 : \1", text)

    temp_save_path = os.path.join(temp_docx_dir, filename)
    doc.save(temp_save_path)

print("[1단계 완료] PDF용 문서 준비 완료")
print("[2단계 진행] PDF 일괄 생성 및 통합 병합 중...")

convert(temp_docx_dir, temp_pdf_dir)

merger = PdfWriter()
pdf_files = sorted([os.path.join(temp_pdf_dir, f) for f in os.listdir(temp_pdf_dir) if f.endswith(".pdf")])
for pdf in pdf_files:
    merger.append(pdf)

final_pdf_path = r"D:\LP_Agent\LP_전체음반_통합검색본.pdf"
with open(final_pdf_path, "wb") as f_out:
    merger.write(f_out)
merger.close()

# 임시 파일 정리
for f in os.listdir(temp_docx_dir):
    try:
        os.remove(os.path.join(temp_docx_dir, f))
    except:
        pass
for f in pdf_files:
    try:
        os.remove(f)
    except:
        pass

try:
    os.rmdir(temp_docx_dir)
    os.rmdir(temp_pdf_dir)
except:
    pass

print("="*60)
print("완료되었습니다!")
print("- PDF 문서에는 '번호'가 완전히 빠지고 '순수 3자리 위치 번호'만 수록되었습니다.")
print("- 이제 Ctrl+F 후 '104', '701' 등 숫자만 치시면 렉 없이 즉각 이동합니다.")
print(f"- 최종 파일: {final_pdf_path}")
print("="*60)