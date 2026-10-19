import os
import pandas as pd

BASE_DIR = r"D:\LP_Agent"
EXCEL_PATH = os.path.join(BASE_DIR, "lp_list.xlsx")
WORD_DIR = os.path.join(BASE_DIR, "word_reports")

print("=" * 50)
print("1. 엑셀 파일 확인")
print("=" * 50)

if os.path.exists(EXCEL_PATH):
    df = pd.read_excel(EXCEL_PATH)
    print("성공: 엑셀 파일을 찾았습니다.")
    print(f"- 등록된 음반 수: {len(df)}개")
    print(f"- 엑셀 제목 칸들: {list(df.columns)}")
    print("\n[엑셀 내용 미리보기]")
    print(df.head(2))
else:
    print("실패: lp_list.xlsx 파일을 찾을 수 없습니다.")

print("\n" + "=" * 50)
print("2. 워드 보고서 폴더 확인")
print("=" * 50)

if os.path.exists(WORD_DIR):
    word_files = [f for f in os.listdir(WORD_DIR) if f.endswith(".docx") and not f.startswith("~$")]
    print("성공: 워드 폴더를 찾았습니다.")
    print(f"- 들어있는 워드 파일 개수: {len(word_files)}개")
    print("\n[워드 파일 이름 예시 5개]")
    for fname in word_files[:5]:
        print(f"  - {fname}")
else:
    print("실패: word_reports 폴더를 찾을 수 없습니다.")

print("=" * 50)