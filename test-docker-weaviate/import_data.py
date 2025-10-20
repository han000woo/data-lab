import weaviate
import weaviate.classes.config as wvc
import json
import ollama
import time

print("Ollama가 LLM(llama3:8b) 모델을 다운로드합니다. 몇 분 정도 걸릴 수 있습니다...")
# (참고: docker-compose.yml의 ollama 서비스가 아닌, 
#  호스트의 ollama 라이브러리를 통해 ollama 컨테이너에 모델 다운로드 요청)
time.sleep(5)

try:
    # stream=True로 설정하여 로그를 실시간으로 받습니다.
    stream = ollama.pull('llama3:8b', stream=True)

    print("Ollama가 LLM(llama3:8b) 모델을 다운로드합니다...")

    # pull()이 반환하는 로그 스트림(generator)을 순회합니다.
    for chunk in stream:
        if 'status' in chunk:
            # 'pulling manifest', 'downloading...' 등의 상태를 출력
            print(f"상태: {chunk['status']}", end='', flush=True)

            # 'total'과 'completed' 키가 있으면 다운로드 진행률을 계산
            if 'total' in chunk and 'completed' in chunk:
                total = chunk['total']
                completed = chunk['completed']
                percentage = (completed / total) * 100
                # 같은 줄에 진행률을 덮어쓰기 위해 \r 사용
                print(f" -> {percentage:.2f}% ({completed} / {total})", end='\r')
            else:
                # 상태 메시지만 있는 경우 줄바꿈
                print() # 줄바꿈

    # 다운로드 완료 후 줄바꿈
    print("\n✅ Ollama 모델 다운로드 완료!")
except Exception as e:
    print(f"❌ Ollama 모델 다운로드 실패 (Ollama 컨테이너가 실행 중인지 확인하세요): {e}")
    # (이미 다운로드된 경우 무시하고 진행)
    pass 

# 1. Weaviate 클라이언트 연결
try:
    client = weaviate.connect_to_local() # localhost:8080에 연결
    print("✅ Weaviate 연결 성공!")
except Exception as e:
    print(f"❌ Weaviate 연결 실패: {e}")
    exit()

collection_name = "Article"

# 2. 기존 컬렉션 삭제
if client.collections.exists(collection_name):
    client.collections.delete(collection_name)
    print("기존 'Article' 컬렉션 삭제 완료.")

# 3. 신규 컬렉션 (스키마) 생성
print("새 'Article' 컬렉션 생성 중...")
articles_collection = client.collections.create(
    name=collection_name,
    
    # 1) 벡터화 설정
    vectorizer_config=wvc.Configure.Vectorizer.text2vec_transformers(),
    
    # 2) (신규) 생성형 AI 설정
    generative_config=wvc.Configure.Generative.ollama(
        api_endpoint="http://localhost:11434", # 호스트에서 바라보는 Ollama 주소
        model="llama3:8b" # 사용할 LLM 모델
    ),

    # 3) 데이터 속성(필드) 정의
    properties=[
        wvc.Property(
            name="title",
            data_type=wvc.DataType.TEXT
        ),
        wvc.Property(
            name="content",
            data_type=wvc.DataType.TEXT
        ),
        wvc.Property(
            name="category",
            data_type=wvc.DataType.TEXT,
            # (중요) category 필드는 필터링에 사용할 것이므로, 
            # 벡터화(vectorize) 대상에서 제외하여 리소스를 절약합니다.
            vectorize_property_name=False, 
            skip_vectorization=True
        ),
    ]
)

print(f"✅ '{collection_name}' 컬렉션 생성 완료!")

# 4. 데이터 적재
print("데이터 적재 시작...")
with open('data.json', 'r') as f:
    data = json.load(f)

# 배치(Batch) 모드로 데이터 삽입
with articles_collection.batch.dynamic() as batch:
    for item in data:
        batch.add_object(
            properties={
                "title": item["title"],
                "content": item["content"],
                "category": item["category"]
            }
        )

print(f"✅ 데이터 {len(data)}개 적재 완료!")
client.close()
