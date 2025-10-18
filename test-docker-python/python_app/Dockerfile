# 1. 파이썬 3.10 경량 버전을 기반으로 합니다.
FROM python:3.10-slim

# 2. 컨테이너 내부의 작업 디렉터리를 /app으로 설정
WORKDIR /app

# 3. 라이브러리 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. 나머지 코드를 /app 디렉터리로 복사
COPY . .

# 5. 이 컨테이너가 실행될 때 main.py를 실행
CMD ["python", "main.py"]


