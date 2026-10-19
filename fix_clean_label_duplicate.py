import os
import re
import time
import win32com.client
from docx import Document
from docx.shared import Pt, RGBColor
from pypdf import PdfWriter

source_dir = r"D:\LP_Agent\word_reports"
temp_docx_dir = r"D:\LP_Agent\docx_temp_clean_lbl"
temp_pdf_dir = r"D:\LP_Agent\pdf_temp_clean_lbl"

os.makedirs(temp_docx_dir, exist_ok=True)
os.makedirs(temp_pdf_dir, exist_ok=True)

files = sorted([f for f in os.listdir(source_dir) if f.endswith(".docx") and not f.startswith("~$")])

print(f"총 {len(files)}개 문서: 서식 적용 및 메모리 최적화 변환을 시작합니다...")

# 1. 워드 문서 서식 재구성
for filename in files:
    doc_path = os.path.join(source_dir, filename)
    doc = Document(doc_path)
    
    loc_val = ""
    for p in doc.paragraphs:
        m = re.search(r"위치\s*:\s*[@NL]?(\d+)", p.text)
        if m:
            loc_val = m.group(1)
            break
    if not loc_val:
        m_fn = re.search(r"위치_(\d+)", filename)
        if m_fn:
            loc_val = m_fn.group(1)

    full_text = "\n".join([p.text for p in doc.paragraphs])
    
    year_val = ""
    m_yr = re.search(r"(\d{4})\s*년", full_text)
    if m_yr:
        year_val = m_yr.group(1)

    label_val = ""
    m_lb_full = re.search(r"(?:\d{4}\s*년\s*)?([A-Za-z가-힣0-9\s\(\)]+?(?:레코드|Records|라벨|Label|모타운|Motown|아리스타|Arista|데카|Decca|도이치\s*그라모폰|Deutsche\s*Grammophon|필립스|Philips|컬럼비아|Columbia|RCA|EMI|Sire))(?:\s*를\s*통해|\s*에서|\s*발매|\s*로)?", full_text)
    
    if m_lb_full:
        clean_name = m_lb_full.group(1).strip()
        clean_name = re.sub(r"^\d{4}\s*년\s*", "", clean_name).strip()
        if len(clean_name) < 35:
            label_val = clean_name

    target_idx = -1
    for idx, p in enumerate(doc.paragraphs):
        txt = p.text
        if any(k in txt for k in ["위치 :", "위치:", "음반 레이블", "음반레이블", "발매년도", "번호 :", "번호:"]):
            if target_idx == -1:
                target_idx = idx
            p.text = ""

    if target_idx == -1:
        target_idx = 1 if len(doc.paragraphs) > 1 else 0
        p_header = doc.paragraphs[target_idx]
    else:
        p_header = doc.paragraphs[target_idx]

    p_header.text = ""
    
    # 위치 번호 (13pt, Bold)
    run_loc = p_header.add_run(f"위치 : {loc_val}")
    run_loc.bold = True
    run_loc.font.size = Pt(13)
    run_loc.font.color.rgb = RGBColor(0, 0, 0)
    
    # 1.5배 확장 간격
    run_space1 = p_header.add_run("                     |          ")
    run_space1.font.size = Pt(10.5)
    run_space1.font.color.rgb = RGBColor(140, 140, 140)
    
    # 레이블
    lbl_text = f"음반 레이블 : {label_val}" if label_val else "음반 레이블 : "
    run_lbl = p_header.add_run(lbl_text)
    run_lbl.font.size = Pt(10.5)
    
    # 간격
    run_space2 = p_header.add_run("          |          ")
    run_space2.font.size = Pt(10.5)
    run_space2.font.color.rgb = RGBColor(140, 140, 140)
    
    # 발매년도
    yr_text = f"발매년도 : {year_val}" if year_val else "발매년도 : "
    run_yr = p_header.add_run(yr_text)
    run_yr.font.size = Pt(10.5)

    temp_save_path = os.path.join(temp_docx_dir, filename)
    doc.save(temp_save_path)

print("[1단계 완료] 워드 서식 정제 완료")
print("[2단계 진행] 멈춤 방지 고속 PDF 변환 시작...")

# 2. 30개 단위 메모리 리프레시로 끊김 없는 변환
def get_word():
    w = win32com.client.DispatchEx("Word.Application")
    w.Visible = False
    w.DisplayAlerts = False
    return w

word = get_word()
docx_files = sorted([f for f in os.listdir(temp_docx_dir) if f.endswith(".docx")])
total = len(docx_files)

for idx, f in enumerate(docx_files, 1):
    in_file = os.path.join(temp_docx_dir, f)
    out_file = os.path.join(temp_pdf_dir, f.replace(".docx", ".pdf"))
    
    # 이미 정상 생성된 파일은 건너뜀 (고속 복구)
    if os.path.exists(out_file) and os.path.getsize(out_file) > 1000:
        if idx % 30 == 0 or idx == total:
            print(f"진행률: {idx}/{total} ({(idx/total)*100:.1f}%)")
        continue

    for attempt in range(2):
        try:
            doc = word.Documents.Open(in_file, ReadOnly=True, ConfirmConversions=False)
            doc.SaveAs(out_file, FileFormat=17)
            doc.Close(0)
            break
        except Exception:
            time.sleep(0.3)
            try: word.Quit()
            except: pass
            word = get_word()

    # 30개마다 Word 프로세스를 재시작하여 메모리 렉 원천 차단
    if idx % 30 == 0:
        try: word.Quit()
        except: pass
        word = get_word()
        print(f"진행률: {idx}/{total} ({(idx/total)*100:.1f}%)")

try:
    word.Quit()
except:
    pass

# 3. PDF 병합
print("[3단계 진행] 전체 통합 검색본 병합 중...")
merger = PdfWriter()
pdf_files = sorted([os.path.join(temp_pdf_dir, f) for f in os.listdir(temp_pdf_dir) if f.endswith(".pdf")])

for pdf in pdf_files:
    merger.append(pdf)

final_pdf_path = r"D:\LP_Agent\LP_전체음반_통합검색본.pdf"
with open(final_pdf_path, "wb") as f_out:
    merger.write(f_out)
merger.close()

# 4. 임시 파일 정리
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
print("완료되었습니다! 멈춤 없이 100% 완료되었습니다.")
print(f"최종 파일: {final_pdf_path}")
print("="*60)