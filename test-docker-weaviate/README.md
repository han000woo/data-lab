# 🐳 Docker + Weaviate + Ollama RAG API 프로젝트

이 프로젝트는 **Docker Compose**를 사용하여 벡터 데이터베이스(**Weaviate**), 로컬 LLM(**Ollama**), 그리고 **FastAPI** 서버를 연동하여 완전한 RAG(검색 증강 생성) 파이프라인을 구축하는 실습입니다.

---

## 🚀 아키텍처

이 프로젝트는 3개의 도커 컨테이너와 호스트(Host)에서 실행되는 2개의 파이썬 스크립트로 구성됩니다.

### Docker 서비스 (`docker-compose.yml`)

1.  **`weaviate`**: 핵심 벡터 데이터베이스입니다. 데이터를 저장하고, 벡터 검색을 수행하며, 다른 두 서비스와 통신하여 RAG 프로세스를 조율합니다.
2.  **`text2vec-transformers`**: 텍스트를 벡터로 변환하는 모듈입니다. `import_data.py`가 데이터를 삽입할 때 텍스트를 벡터로 임베딩하는 역할을 합니다.
3.  **`ollama`**: `llama3:8b` 모델을 호스팅하는 로컬 LLM 서버입니다. `weaviate`로부터 RAG 요청을 받아 답변을 생성합니다.

### 호스트(Host) 스크립트 (가상 환경)

1.  **`import_data.py`**:
    * `ollama` 컨테이너에 접속하여 `llama3:8b` 모델을 다운로드합니다.
    * `weaviate` 컨테이너에 접속하여 데이터 스키마("Article" 컬렉션)를 정의합니다.
    * `data.json` 파일을 읽어 Weaviate에 데이터를 적재합니다. (이때 `text2vec-transformers`가 벡터화를 수행합니다.)
2.  **`api.py`**:
    * 사용자가 쉽게 RAG를 테스트할 수 있도록 3가지 엔드포인트(`/search`, `/filter`, `/ask`)를 제공하는 FastAPI 서버입니다.

### RAG 데이터 흐름

1.  사용자가 `http://<서버_IP>:8000/ask?q=...` (FastAPI)로 질문을 보냅니다.
2.  FastAPI(`api.py`)가 `weaviate`에게 "생성형 검색"을 요청합니다.
3.  **Weaviate**는 DB에서 질문과 관련된 문서를 **검색(Retrieve)**합니다.
4.  **Weaviate**는 (질문 + 검색된 문서)를 **Ollama** 컨테이너(`:11434`)로 전송합니다.
5.  **Ollama**는 전달받은 문서를 기반으로 답변을 **생성(Generate)**합니다.
6.  생성된 답변이 Weaviate를 거쳐 FastAPI, 그리고 사용자에게 최종 반환됩니다.

---

## 📁 프로젝트 구조

```bash 
weaviate-api-lab/ 
├── docker-compose.yml # 3개의 도커 서비스 (weaviate, text2vec, ollama) 정의 
├── data.json # Weaviate에 적재할 샘플 데이터 
├── import_data.py # 데이터 적재 및 LLM 다운로드 스크립트 
├── api.py # FastAPI 서버 스크립트 
└── requirements.txt # 파이썬 라이브러리 목록
```

## ⚙️ 실행 방법

### 1. 도커 컨테이너 시작

프로젝트 루트 폴더(서버)에서 다음 명령어를 실행합니다.

```bash
docker compose up -d
```

