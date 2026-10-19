import os
import openpyxl

excel_path = r"D:\LP_Agent\lp_list.xlsx"
backup_path = r"D:\LP_Agent\lp_list_원본백업.xlsx"

# 1. 안전을 위해 원본 백업본 생성
if not os.path.exists(backup_path):
    wb_orig = openpyxl.load_workbook(excel_path)
    wb_orig.save(backup_path)
    print(f"[안내] 안전을 위해 기존 원본을 '{backup_path}'로 자동 백업했습니다.")

# 2. 엑셀 파일 열기
wb = openpyxl.load_workbook(excel_path)
ws = wb.active

# 헤더에서 '위치' 컬럼 찾기
loc_col_idx = None
for col in range(1, ws.max_column + 1):
    val = str(ws.cell(row=1, column=col).value or "").strip()
    if "위치" in val:
        loc_col_idx = col
        break

if not loc_col_idx:
    # 헤더에 위치라는 글자가 없으면 2번째 또는 3번째 열 탐색
    loc_col_idx = 2

# 기존 700~722번 음반 매핑 (725~746)
existing_700_series = list(range(700, 723))
reassign_700_map = {old: 725 + i for i, old in enumerate(existing_700_series)}

updated_count = 0
for row in range(2, ws.max_row + 1):
    cell = ws.cell(row=row, column=loc_col_idx)
    if cell.value is not None:
        try:
            num = int(str(cell.value).strip())
            if num < 100:
                cell.value = num + 700
                updated_count += 1
            elif 700 <= num <= 722:
                cell.value = reassign_700_map.get(num, num)
                updated_count += 1
        except ValueError:
            pass

wb.save(excel_path)
print("="*60)
print(f"엑셀 파일 업데이트 완료! (총 {updated_count}개 음반의 위치 번호 동기화)")
print(f"업데이트된 파일: {excel_path}")
print("="*60)