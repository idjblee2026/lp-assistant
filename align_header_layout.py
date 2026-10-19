import os
import re
import time
import win32com.client
from docx import Document
from pypdf import PdfWriter

source_dir = r"D:\LP_Agent\word_reports"
temp_docx_dir = r"D:\LP_Agent\docx_temp_align"
temp_pdf_dir = r"D:\LP_Agent\pdf_temp_align"

os.makedirs(temp_docx_dir, exist_ok=True)
os.makedirs(temp_pdf_dir, exist_ok=True)

files = sorted([f for f in os.listdir(source_dir) if f.endswith(".docx") and not f.startswith("~$")])

print("상단 정보를 '위치 | 음반 레이블 | 발매년도' 가로 한 줄로 재배치합니다...")

for filename in files:
    doc_path = os.path.join(source_dir, filename)
    doc = Document(doc_path)
    
    # 1. 기존 문서에서 위치, 레이블, 발매년도 데이터 추출
    loc_val = ""
    label_val = ""
    year_val = ""
    
    # 본문 전체 텍스트 수집
    paras = doc.paragraphs
    for p in paras:
        txt = p.text
        # 위치 추출
        m_loc = re.search(r"위치\s*:\s*[@NL]?(\d+)", txt)
        if m_loc and not loc_val:
            loc_val = m_loc.group(1)
        # 레이블 추출
        m_lbl = re.search(r"음반\s*레이블\s*:\s*([^|\n]+)", txt)
        if m_lbl and not label_val:
            label_val = m_lbl.group(1).strip()
        # 발매년도 추출
        m_yr = re.search(r"발매년도\s*:\s*([^|\n]+)", txt)
        if m_yr and not year_val:
            year_val = m_yr.group(1).strip()

    # 파일명 백업 추출
    if not loc_val:
        m_fn = re.search(r"위치_(\d+)", filename)
        if m_fn:
            loc_val = m_fn.group(1)

    # 한 줄로 합칠 문자열 구성
    parts = []
    if loc_val:
        parts.append(f"위치 : {loc_val}")
    if label_val:
        parts.append(f"음반 레이블 : {label_val}")
    else:
        parts.append("음반 레이블 :")
    if year_val:
        parts.append(f"발매년도 : {year_val}")
    else:
        parts.append("발매년도 :")

    combined_header = "    |    ".join(parts)

    # 2. 문단 재정리: 기존의 분리된 위치, 레이블, 발매년도, 번호 줄 삭제 후 첫 머리에 가로 정렬 한 줄 삽입
    first_target_idx = -1
    for idx, p in enumerate(paras):
        txt = p.text
        if any(key in txt for key in ["번호 :", "위치 :", "음반 레이블 :", "발매년도 :", "음반레이블 :"]):
            if first_target_idx == -1:
                first_target_idx = idx
            p.text = "" # 내용 비우기

    # 첫 번째 메타 정보가 있던 자리에 통합된 가로 줄 배치
    if first_target_idx != -1:
        paras[first_target_idx].text = combined_header
    else:
        # 못 찾았다면 제목 아래 문단에 새로 추가
        if len(paras) > 1:
            p_new = paras[1].insert_paragraph_before(combined_header)

    temp_save_path = os.path.join(temp_docx_dir, filename)
    doc.save(temp_save_path)

print("[1단계 완료] 가로 정렬 임시 워드 문서 생성 완료")
print("[2단계 진행] 고속 PDF 일괄 변환 중...")

# 3. PDF 변환
word = win32com.client.DispatchEx("Word.Application")
word.Visible = False
word.DisplayAlerts = False

docx_files = sorted([f for f in os.listdir(temp_docx_dir) if f.endswith(".docx")])
total = len(docx_files)

for idx, f in enumerate(docx_files, 1):
    in_file = os.path.join(temp_docx_dir, f)
    out_file = os.path.join(temp_pdf_dir, f.replace(".docx", ".pdf"))
    
    for attempt in range(3):
        try:
            doc = word.Documents.Open(in_file, ReadOnly=True)
            doc.SaveAs(out_file, FileFormat=17)
            doc.Close(0)
            break
        except Exception:
            time.sleep(0.5)
            try: word.Quit()
            except: pass
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
print("[3단계 진행] 전체 통합 검색본 병합 중...")
merger = PdfWriter()
pdf_files = sorted([os.path.join(temp_pdf_dir, f) for f in os.listdir(temp_pdf_dir) if f.endswith(".pdf")])

for pdf in pdf_files:
    merger.append(pdf)

final_pdf_path = r"D:\LP_Agent\LP_전체음반_통합검색본.pdf"
with open(final_pdf_path, "wb") as f_out:
    merger.write(f_out)
merger.close()

# 5. 임시 정리
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
print("상단 정보 가로 정렬 완료!")
print(f"- 최종 파일: {final_pdf_path}")
print("="*60)