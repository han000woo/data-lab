# 🐳 도커를 활용한 풀스택 데이터 파이프라인

이 프로젝트는 **Docker Compose**를 사용하여 4개의 컨테이너를 오케스트레이션(orchestration)하는 풀스택(Full-stack) 데이터 파이프라인 실습입니다.

파이썬 스크립트가 외부 API에서 데이터를 가져와 PostgreSQL DB에 저장하면, FastAPI 서버가 이 데이터를 JSON API로 제공합니다. 마지막으로 Nginx 웹 서버가 이 API를 호출하여 사용자에게 데이터를 보여주는 동적 웹페이지를 제공합니다.

---

## 🚀 프로젝트 아키텍처

이 프로젝트는 4개의 도커 서비스로 구성됩니다.

1.  **`app` (Python 스크립트):**

    - 1회성으로 실행되는 작업 컨테이너입니다.
    - `jsonplaceholder` 공개 API에서 게시물 데이터를 `requests`로 가져옵니다.
    - `pandas`로 데이터를 처리(가공)합니다.
    - `db` 서비스(PostgreSQL)에 `posts` 테이블을 생성하고 데이터를 저장합니다.

2.  **`db` (PostgreSQL):**

    - `app` 서비스가 저장한 데이터를 영구적으로 보관하는 데이터베이스 컨테이너입니다.
    - 데이터는 도커 볼륨(`postgres-data`)에 저장되어 컨테이너가 종료되어도 유지됩니다.

3.  **`api` (FastAPI 서버):**

    - `db` 컨테이너에 연결하여 `/posts` 엔드포인트를 제공하는 백엔드 API 서버입니다.
    - `web` 서비스의 `fetch` 요청을 받을 수 있도록 **CORS (교차 출처 리소스 공유)** 설정이 포함되어 있습니다.
    - `8000`번 포트로 실행됩니다.

4.  **`web` (Nginx 서버):**
    - 사용자에게 `index.html`을 제공하는 프론트엔드 웹 서버입니다.
    - `index.html` 안의 JavaScript는 `api` 서비스(`:8000/posts`)를 `fetch`로 호출하여 데이터를 받아온 뒤, 동적으로 HTML 목록을 생성합니다.
    - `8080`번 포트로 실행됩니다.

### 데이터 흐름

[사용자 브라우저] ➡️ `web` (Nginx, :8080) ➡️ `index.html`의 JavaScript `fetch` 실행 ➡️ `api` (FastAPI, :8000) ➡️ `db` (PostgreSQL)

---

## 📁 프로젝트 구조

data-pipeline-docker/
├── docker-compose.yml     # 4개 서비스(app, db, api, web) 정의
├── README.md              # (프로젝트 설명 파일)
│
├── python_app/            # (Service: app) 1회성 데이터 처리
│   ├── main.py            # API 데이터 Fetch -> Pandas -> DB 저장
│   ├── Dockerfile
│   └── requirements.txt   # pandas, requests, sqlalchemy, psycopg2-binary
│
├── api_app/               # (Service: api) 백엔드 API 서버
│   ├── main.py            # FastAPI, /posts 엔드포인트, CORS 설정
│   ├── Dockerfile
│   └── requirements.txt   # fastapi, uvicorn, sqlalchemy, ...
│
└── web_app/               # (Service: web) 프론트엔드 웹 서버
    ├── index.html         # JavaScript fetch()로 API 호출
    └── Dockerfile         # Nginx

---

## 🛠️ 기술 스택

- **Infra:** Docker, Docker Compose (V2)
- **Backend:** Python, FastAPI, Pandas, SQLAlchemy
- **Frontend:** Nginx, HTML, JavaScript (Fetch API)
- **Database:** PostgreSQL

---

## ⚙️ 실행 방법

1.  이 리포지토리를 클론(clone)합니다.

    ```bash
    git clone <이 리포지토리의 URL>
    cd <프로젝트 폴더>
    ```

2.  (필수) `api_app/main.py`와 `web_app/index.html` 파일을 열어, 하드코딩된 **IP 주소** (`121.162.95.145` 등)를 **현재 서버의 IP 주소로** 변경합니다.

3.  Docker Compose (V2)로 모든 서비스를 빌드하고 실행합니다.

    ```bash
    # (주의: docker-compose가 아닌 docker compose 입니다)
    docker compose up --build -d
    ```

4.  브라우저에서 웹페이지에 접속합니다.

    - `http://<서버_IP>:8080`

5.  (선택) API 엔드포인트를 직접 확인할 수 있습니다.
    - `http://<서버_IP>:8000/posts`

---

## 💡 트러블 슈팅

- **CORS (교차 출처 리소스 공유):** 이 프로젝트의 가장 핵심적인 난관이었습니다.

  - **문제:** `web`(`:8080`)에서 받은 웹페이지가 `api`(`:8000`)에 데이터를 요청하면, 브라우저는 이 둘의 '출처(Origin)'가 다르다고 판단하여 보안상 차단합니다.
  - **해결:** `api` 서버(FastAPI)의 `main.py`에 `CORSMiddleware`를 추가하여, `http://<서버_IP>:8080`에서의 요청을 명시적으로 '허용'하도록 설정했습니다.

- **IP 주소 vs 호스트 이름:**

  - `http://<서버_IP>:8080` (IP 주소)로 접속하면 성공했습니다.
  - `http://sunwoo-piececube-x:8080` (호스트 이름)으로 접속하면 실패했습니다.
  - **원인 1 (DNS):** 사용자 PC의 브라우저는 `sunwoo-piececube-x`라는 로컬 호스트 이름을 IP 주소로 변환(Resolve)하지 못했습니다. (`ERR_NAME_NOT_RESOLVED`)
  - **원인 2 (CORS):** 설령 DNS가 해결되었더라도, `web_app/index.html`의 `fetch` URL이 IP 주소(`121...:8000`)로 하드코딩되어 있어, 요청 출처(`sunwoo-piececube-x:8080`)와 목적지(`121...:8000`)가 달라 CORS 정책에 위반됩니다.
  - **결론:** IP 주소를 기준으로 접속 URL과 CORS 설정을 통일하여 문제를 해결했습니다.

- **컨테이너 디버깅:**
  - 컨테이너가 `Up` 상태가 아니거나 접속이 거부될 때(`ERR_CONNECTION_REFUSED`), `docker compose logs <서비스이름>` (예: `docker compose logs api`) 명령어가 컨테이너 내부의 파이썬 오류(`NameError` 등)를 찾는 데 결정적이었습니다.
  - `docker compose up --build`는 코드가 변경되었을 때 컨테이너에 변경 사항을 반영하는 필수 명령어임을 확인했습니다.

## 트러블슈팅: CORS

이 프로젝트의 가장 핵심적인 난관은 **CORS (Cross-Origin Resource Sharing, 교차 출처 리소스 공유)** 문제였습니다.

* **문제 상황:**
    1.  **웹페이지 (`web`):** `http://121.162.95.145:8080`에서 호스팅됩니다.
    2.  **API (`api`):** `http://121.162.95.145:8000`에서 호스팅됩니다.
    3.  브라우저는 `8080` 포트에서 받은 웹페이지가 `8000` 포트의 리소스를 요청하는 것을 "다른 출처(Cross-Origin)"로 간주하여 보안상 차단했습니다.

* **진단:**
    * 브라우저 주소창에 API 주소(`...:8000/posts`)를 직접 입력하면 `200 OK`로 데이터가 잘 보였습니다.
    * 하지만 웹페이지(`...:8080`)에서 `fetch`로 API를 호출할 때만 실패했습니다.
    * 이는 네트워크나 서버의 문제가 아닌, **브라우저의 보안 정책(CORS)**이 원인임을 의미합니다.

* **해결책:**
    * **`api` 서버(FastAPI)**가 `web` 서버의 요청을 "허용"하도록 명시적으로 설정했습니다.
    * `api_app/main.py` 파일에 `CORSMiddleware`를 추가하고, `allow_origins` 리스트에 웹페이지의 출처(`http://121.162.95.145:8080`)를 정확히 포함시켰습니다.

    ```python
    # api_app/main.py
    from fastapi.middleware.cors import CORSMiddleware

    origins = [
        "[http://121.162.95.145:8080](http://121.162.95.145:8080)" # ⬅️ 이 출처를 허용
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    ```

