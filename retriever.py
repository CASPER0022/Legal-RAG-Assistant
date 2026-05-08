import chromadb, os
from sentence_transformers import SentenceTransformer
from flashrank import Ranker, RerankRequest
import numpy as np

EMB_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
DB_DIR = "data/vec"
COLL = "kb_chunks"

client = chromadb.PersistentClient(path=DB_DIR)
coll = client.get_or_create_collection(COLL)
model = SentenceTransformer(EMB_MODEL)
# ms-marco-MiniLM-L-12-v2 is a good balance of speed and accuracy
ranker = Ranker(model_name="ms-marco-MiniLM-L-12-v2", cache_dir="data/flashrank")

def retrieve(query: str, k: int = 25, rerank_k: int = 8):
    """
    Hybrid-ready retrieval with re-ranking.
    1. Vector search for top-k candidates.
    2. Re-rank top candidates using a cross-encoder (FlashRank).
    """
    # 1. Vector Search (Dense)
    qv = model.encode([query], normalize_embeddings=True).tolist()[0]
    res = coll.query(query_embeddings=[qv], n_results=k)
    
    documents = res.get("documents", [[]])[0]
    metadatas = res.get("metadatas", [[]])[0]
    
    if not documents:
        return {"docs": [], "metadatas": [], "scores": []}

    # Prepare for FlashRank
    passages = []
    for i, doc in enumerate(documents):
        passages.append({
            "id": i,
            "text": doc,
            "meta": metadatas[i]
        })

    # 2. Re-ranking
    rerankrequest = RerankRequest(query=query, passages=passages)
    results = ranker.rerank(rerankrequest)
    
    # Take top rerank_k
    top_results = results[:rerank_k]
    
    return {
        "docs": [r["text"] for r in top_results],
        "metadatas": [r["meta"] for r in top_results],
        "scores": [float(r["score"]) for r in top_results]
    }