import weaviate
import weaviate.classes.query as wq
from fastapi import FastAPI, HTTPException

# 1. FastAPI 앱 및 Weaviate 클라이언트 초기화
app = FastAPI(title="Weaviate 실습 API")
client = weaviate.connect_to_local() # localhost:8080에 연결
articles_collection = client.collections.get("Article")

print("FastAPI 서버가 Weaviate에 연결되었습니다.")

# --- 2. API 엔드포인트 정의 ---

@app.get("/")
def read_root():
    return {"message": "Weaviate FastAPI 서버입니다. /docs 에서 API 문서를 확인하세요."}


# 엔드포인트 1: 벡터 검색 (Semantic Search)
@app.get("/search")
def search_vector(q: str):
    """
    입력된 쿼리(q)와 의미적으로 가장 유사한 문서를 2개 검색합니다.
    """
    try:
        response = articles_collection.query.near_text(
            query=q,
            limit=2,
            # (중요) 검색된 문서의 '유사도'도 함께 반환
            return_metadata=wq.MetadataQuery(distance=True) 
        )
        
        results = []
        for obj in response.objects:
            results.append({
                "title": obj.properties["title"],
                "content": obj.properties["content"],
                "distance": obj.metadata.distance
            })
        return {"query": q, "results": results}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 엔드포인트 2: 하이브리드 검색 (Vector + Filter)
@app.get("/filter")
def search_filter(q: str, category: str):
    """
    특정 'category'에 속하는 문서 중에서
    쿼리(q)와 의미적으로 가장 유사한 문서를 검색합니다.
    """
    try:
        response = articles_collection.query.near_text(
            query=q,
            limit=2,
            # (핵심) 'where' 필터를 사용하여 'category' 필드를 필터링
            filters=wq.Filter.by_property("category").equal(category)
        )
        
        results = []
        for obj in response.objects:
            results.append({
                "title": obj.properties["title"],
                "content": obj.properties["content"]
            })
        return {"query": q, "category_filter": category, "results": results}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 엔드포인트 3: RAG (Generative Search)
@app.get("/ask")
def ask_rag(q: str):
    """
    쿼리(q)와 관련된 문서를 Weaviate가 검색한 뒤,
    Ollama(LLM)가 검색된 내용을 기반으로 질문에 대한 답변을 '생성'합니다.
    """
    try:
        # (핵심) .with_generative() 사용
        response = articles_collection.generate.near_text(
            query=q,
            limit=2, # 답변의 근거로 삼을 문서를 2개 검색
            
            # Ollama에 전달할 프롬프트 템플릿
            grouped_task="""
            다음 문서를 참고하여 질문에 대한 답변을 한국어로 생성해줘.
            질문: {question}
            ---
            참고 문서:
            {content}
            """
        )
        
        # 'response.generated'에 생성된 답변이 담겨 있습니다.
        return {"question": q, "answer": response.generated}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 서버 종료 시 클라이언트 연결 해제
@app.on_event("shutdown")
def shutdown_event():
    client.close()
    print("Weaviate 연결이 해제되었습니다.")
