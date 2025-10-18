# 1. 파이썬 3.10 경량 버전을 기반으로 합니다.
FROM python:3.10-slim

# 2. 컨테이너 내부의 작업 디렉터리를 /api로 설정
WORKDIR /api

# 3. 라이브러리 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. 나머지 코드를 /api 디렉터리로 복사
COPY . .

# 5. FastAPI 서버 실행 (포트 8000번)
# 0.0.0.0으로 호스트를 열어야 도커 외부(Host)에서 접속 가능
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
