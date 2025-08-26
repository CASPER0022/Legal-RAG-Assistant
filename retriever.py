import chromadb, os
from sentence_transformers import SentenceTransformer
from cache import get_or_set

EMB_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
DB_DIR = "data/vec"; COLL = "kb_chunks"

client = chromadb.PersistentClient(path=DB_DIR)
coll = client.get_or_create_collection(COLL)
model = SentenceTransformer(EMB_MODEL)

def retrieve(query:str, k:int=4):
    def _compute():
        qv = model.encode([query], normalize_embeddings=True).tolist()[0]
        res = coll.query(query_embeddings=[qv], n_results=k)
        docs = res.get("documents", [[]])[0]
        return {"docs": docs}
    #return get_or_set("retrieval", {"q":query, "k":k}, _compute) DO WHEN REDIS IS RUNNING
    return _compute()

# This code is your search layer:

# You give it a natural language query (like “what is Python?”).

# It converts that query into a vector embedding.

# It asks ChromaDB to find the most similar chunks in your knowledge base.

# It wraps the whole thing in a Redis cache so repeated queries are faster.