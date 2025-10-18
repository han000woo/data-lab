import os
import time
import pandas as pd
import requests
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError

print("🚀 파이썬 스크립트 시작!")

# --- 1. 환경 변수에서 DB 접속 정보 가져오기 ---
# (docker-compose.yml에서 이 변수들을 주입할 예정)
DB_USER = os.getenv("DB_USER", "user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_HOST = os.getenv("DB_HOST", "db") # 'db'는 docker-compose의 서비스 이름!
DB_NAME = os.getenv("DB_NAME", "mydatabase")
DB_PORT = os.getenv("DB_PORT", "5432")

# --- 2. 📊 데이터 가져오기 (Fetch) ---
print("데이터 가져오는 중... (API 호출)")
try:
    response = requests.get("https://jsonplaceholder.typicode.com/posts")
    response.raise_for_status() # 오류가 있으면 예외 발생
    data = response.json()
    print("✅ 데이터 가져오기 성공!")
except requests.RequestException as e:
    print(f"❌ API 호출 실패: {e}")
    exit(1) # 스크립트 종료

# --- 3. 🛠️ 데이터 처리 (Process) ---
print("데이터 처리 중... (Pandas DataFrame 변환)")
df = pd.DataFrame(data)
df = df[['userId', 'id', 'title']] # 필요한 컬럼만 선택
df.rename(columns={'id': 'post_id'}, inplace=True) # 컬럼명 변경
print(f"✅ 총 {len(df)}개의 레코드 처리 완료!")
print(df.head())

# --- 4. 💾 DB에 저장 (Store) ---
db_url = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# DB가 준비될 때까지 대기 (컨테이너 실행 순서 보장)
max_retries = 10
retry_delay = 5
engine = None

for i in range(max_retries):
    try:
        engine = create_engine(db_url)
        engine.connect()
        print(f"\n⏱️ ({i+1}/{max_retries}) DB 연결 시도... 성공!")
        break # 연결 성공 시 루프 탈출
    except OperationalError as e:
        print(f"\n⏱️ ({i+1}/{max_retries}) DB 연결 대기 중... ({e})")
        time.sleep(retry_delay)
else:
    print("❌ DB 연결 실패! 스크립트를 종료합니다.")
    exit(1) # 최대 시도 횟수 초과 시 종료

# DataFrame을 SQL 테이블로 저장
try:
    print("데이터를 'posts' 테이블에 저장 중...")
    # 'if_exists='replace'' : 테이블이 이미 있으면 덮어쓰기
    df.to_sql('posts', engine, if_exists='replace', index=False)
    print("✅ 모든 데이터가 DB에 성공적으로 저장되었습니다!")
except Exception as e:
    print(f"❌ DB 저장 중 오류 발생: {e}")

print("🎉 파이썬 스크립트 종료!")
