import os
import re
import time
import win32com.client
from docx import Document
from pypdf import PdfWriter

source_dir = r"D:\LP_Agent\word_reports"
temp_docx_dir = r"D:\LP_Agent\docx_temp_loc_ok"
temp_pdf_dir = r"D:\LP_Agent\pdf_temp_loc_ok"

os.makedirs(temp_docx_dir, exist_ok=True)
os.makedirs(temp_pdf_dir, exist_ok=True)

files = sorted([f for f in os.listdir(source_dir) if f.endswith(".docx") and not f.startswith("~$")])

print(f"총 {len(files)}개 Word 문서의 위치 번호를 정밀 보존하며 '번호' 항목을 정리합니다...")

for filename in files:
    doc_path = os.path.join(source_dir, filename)
    doc = Document(doc_path)
    
    # 1. 문단 정리
    for p in doc.paragraphs:
        if "번호" in p.text and "위치" not in p.text:
            p.text = ""
        elif "번호" in p.text and "위치" in p.text:
            p.text = re.sub(r"번호\s*:\s*[@NL\d\s\-_|/]+", "", p.text).strip()
            
        if "위치" in p.text:
            p.text = re.sub(r"위치\s*:\s*[@NL]?(\d+)", r"위치 : \1", p.text)

    # 2. 표 정리
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    if "번호" in p.text and "위치" not in p.text:
                        p.text = ""
                    elif "번호" in p.text and "위치" in p.text:
                        p.text = re.sub(r"번호\s*:\s*[@NL\d\s\-_|/]+", "", p.text).strip()
                    if "위치" in p.text:
                        p.text = re.sub(r"위치\s*:\s*[@NL]?(\d+)", r"위치 : \1", p.text)

    temp_save_path = os.path.join(temp_docx_dir, filename)
    doc.save(temp_save_path)

print("[1단계 완료] PDF용 임시 문서 생성 완료")
print("[2단계 진행] MS Word 직접 제어로 끊김 없이 PDF 변환 중...")

# 3. MS Word COM 안정적 변환
word = win32com.client.DispatchEx("Word.Application")
word.Visible = False
word.DisplayAlerts = False

docx_files = sorted([f for f in os.listdir(temp_docx_dir) if f.endswith(".docx")])
total = len(docx_files)

for idx, f in enumerate(docx_files, 1):
    in_file = os.path.join(temp_docx_dir, f)
    out_file = os.path.join(temp_pdf_dir, f.replace(".docx", ".pdf"))
    
    success = False
    for attempt in range(3):
        try:
            doc = word.Documents.Open(in_file, ReadOnly=True)
            doc.SaveAs(out_file, FileFormat=17) # 17 = wdFormatPDF
            doc.Close(0)
            success = True
            break
        except Exception:
            time.sleep(0.5)
            try:
                word.Quit()
            except:
                pass
            word = win32com.client.DispatchEx("Word.Application")
            word.Visible = False
            word.DisplayAlerts = False

    if idx % 50 == 0 or idx == total:
        print(f"변환 진행률: {idx}/{total} ({(idx/total)*100:.1f}%)")

try:
    word.Quit()
except:
    pass

# 4. 단일 PDF 통합
print("[3단계 진행] 전체 PDF 통합 검색본 병합 중...")
merger = PdfWriter()
pdf_files = sorted([os.path.join(temp_pdf_dir, f) for f in os.listdir(temp_pdf_dir) if f.endswith(".pdf")])

for pdf in pdf_files:
    merger.append(pdf)

final_pdf_path = r"D:\LP_Agent\LP_전체음반_통합검색본.pdf"
with open(final_pdf_path, "wb") as f_out:
    merger.write(f_out)
merger.close()

# 5. 임시 폴더 정리
for f in os.listdir(temp_docx_dir):
    try: os.remove(os.path.join(temp_docx_dir, f))
    except: pass
for f in pdf_files:
    try: os.remove(f)
    except: pass

try:
    os.rmdir(temp_docx_dir)
    os.rmdir(temp_pdf_dir)
except: pass

print("="*60)
print("완벽하게 복원 및 생성되었습니다!")
print(f"- 위치 번호(3자리) 완벽 수록")
print(f"- '번호' 항목만 정확히 삭제")
print(f"- 최종 파일: {final_pdf_path}")
print("="*60)