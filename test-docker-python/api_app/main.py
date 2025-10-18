import os
import pandas as pd
from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError, ProgrammingError
from fastapi.middleware.cors import CORSMiddleware

print("🚀 FastAPI 서버 시작!")

# --- 1. 환경 변수에서 DB 접속 정보 가져오기 ---
DB_USER = os.getenv("DB_USER", "user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_HOST = os.getenv("DB_HOST", "db")
DB_NAME = os.getenv("DB_NAME", "mydatabase")
DB_PORT = os.getenv("DB_PORT", "5432")

db_url = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(db_url)

# --- 2. FastAPI 앱 인스턴스 생성 ---
app = FastAPI()

origins = [
    "http://localhost:8080",             # 이전 실습용 (로컬)
    "http://sunwoo-PieceCube-X:8080",  # (핵심) 미니서버의 웹 주소
    # 만약 IP로도 접속한다면 IP도 추가
    "http://121.162.95.145:8080"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,             # origins 목록의 출처만 허용
    allow_credentials=True,
    allow_methods=["*"],               # 모든 HTTP 메소드 허용 (GET, POST 등)
    allow_headers=["*"],               # 모든 HTTP 헤더 허용
)

# --- 3. API 엔드포인트 정의 ---
@app.get("/")
def read_root():
    return {"message": "데이터 조회 API입니다. /posts 로 접속하세요."}

@app.get("/posts")
def get_posts_from_db():
    """
    PostgreSQL DB에 연결하여 'posts' 테이블의 모든 데이터를 조회합니다.
    """
    print("API: /posts 엔드포인트 호출됨")
    try:
        with engine.connect() as connection:
            # Pandas를 사용해 SQL 쿼리 결과를 DataFrame으로 바로 읽기
            df = pd.read_sql("SELECT * FROM posts", connection)
            
            # DataFrame을 JSON (dictionary list) 형태로 변환하여 반환
            return df.to_dict('records')
            
    except ProgrammingError:
        # 'app' 컨테이너가 아직 실행되지 않아 테이블이 없는 경우
        return {"error": "'posts' 테이블을 찾을 수 없습니다. 데이터 처리 앱(app)을 먼저 실행했는지 확인하세요."}
    except OperationalError as e:
        # DB 연결 실패 등
        return {"error": f"DB 연결 실패: {e}"}
    except Exception as e:
        return {"error": f"알 수 없는 오류 발생: {e}"}

