import os
import shutil
import time
import urllib.parse
import urllib.request
import json
import pandas as pd

# 1. 파일 경로 설정
BASE_DIR = r"D:\LP_Agent"
EXCEL_FILE = os.path.join(BASE_DIR, "lp_list.xlsx")
BACKUP_FILE = os.path.join(BASE_DIR, "lp_list_백업.xlsx")

if not os.path.exists(EXCEL_FILE):
    print("lp_list.xlsx 파일을 찾을 수 없습니다.")
    input("엔터를 누르면 종료합니다...")
    exit()

# 2. 안전한 백업 파일 생성
shutil.copy2(EXCEL_FILE, BACKUP_FILE)
print("원본 보호를 위해 [lp_list_백업.xlsx] 백업을 완료했습니다.")

# 3. 엑셀 데이터 불러오기
df = pd.read_excel(EXCEL_FILE)

# 가수 열 이름 찾기
artist_col = None
for col in df.columns:
    if str(col).strip() in ['가수', 'Artists', '아티스트', 'Artist']:
        artist_col = col
        break

if not artist_col:
    print("가수(Artists) 열을 찾을 수 없습니다.")
    input("엔터를 누르면 종료합니다...")
    exit()

# 4. 대상 가수 목록 추출
unique_artists = df[artist_col].dropna().unique()
targets = []

for a in unique_artists:
    name = str(a).strip()
    # 빈 값, Various Artists 계열, 이미 괄호가 있는 경우 제외
    if not name or name.lower() in ['various artists', 'various', 'v.a.', 'v.a']:
        continue
    if '(' in name and ')' in name:
        continue
    targets.append(name)

print(f"총 {len(unique_artists)}명 중 한글 발음 추가 대상: {len(targets)}명")

if not targets:
    print("변환할 대상이 없습니다. 이미 완료되었거나 Various Artists입니다.")
    input("엔터를 누르면 종료합니다...")
    exit()

# 5. API 키 없이 구글 번역을 통해 한글 발음/이름 변환
def get_korean_name(english_name):
    # 잘 알려진 고전 팝 아티스트 예외 사전
    custom_dict = {
        "Bill Justis": "빌 저스티스",
        "The Beatles": "비틀즈",
        "Carpenters": "카펜터스",
        "ABBA": "아바",
        "Simon & Garfunkel": "사이먼 앤 가펑클",
        "Bee Gees": "비지스",
        "Elvis Presley": "엘비스 프레슬리",
        "Cliff Richard": "클리프 리처드",
        "Neil Sedaka": "닐 세다카",
        "Paul Anka": "폴 앵카",
        "Andy Williams": "앤디 윌리엄스",
        "Pat Boone": "팻 분",
        "Connie Francis": "코니 프랜시스",
        "Brenda Lee": "브렌다 리",
        "Nat King Cole": "냇 킹 콜",
        "Frank Sinatra": "프랭크 시나트라",
        "Engelbert Humperdinck": "잉글버트 험퍼딩크",
        "Tom Jones": "톰 존스",
        "Olivia Newton-John": "올리비아 뉴튼 존",
        "Anne Murray": "앤 머레이"
    }
    
    if english_name in custom_dict:
        return custom_dict[english_name]
        
    try:
        url = "https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=ko&dt=t&q=" + urllib.parse.quote(english_name)
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        res = urllib.request.urlopen(req, timeout=5)
        data = json.loads(res.read().decode('utf-8'))
        korean = data[0][0][0].strip()
        # 번역 결과가 그대로 영문인 경우 방지
        if korean and korean.lower() != english_name.lower():
            return korean
    except Exception:
        pass
    return ""

print("한글 이름 변환을 시작합니다. 잠시만 기다려주세요...")

artist_map = {}
total = len(targets)

for idx, name in enumerate(targets, 1):
    kor = get_korean_name(name)
    if kor:
        artist_map[name] = kor
    if idx % 20 == 0 or idx == total:
        print(f"진행 상황: ({idx}/{total}) 완료...")
    time.sleep(0.2)

# 6. 엑셀 데이터에 반영
def update_artist_name(val):
    if pd.isna(val):
        return val
    orig = str(val).strip()
    if orig.lower() in ['various artists', 'various', 'v.a.', 'v.a']:
        return orig
    if '(' in orig and ')' in orig:
        return orig
    if orig in artist_map:
        return f"{orig} ({artist_map[orig]})"
    return orig

df[artist_col] = df[artist_col].apply(update_artist_name)

# 7. 엑셀 파일 저장
df.to_excel(EXCEL_FILE, index=False)

print("\n========================================")
print("  축하합니다! 가수 이름 변환이 완료되었습니다.")
print("========================================")
input("엔터(Enter) 키를 누르면 창이 닫힙니다...")