from pathlib import Path
from sentence_transformers import SentenceTransformer
import chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter

EMB_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
DB_DIR = "data/vec" 
COLL = "kb_chunks"

def load_documents(p):
    documents = []
    for fp in Path(p).glob("**/*"):
        if fp.suffix.lower() in [".txt", ".md", ".pdf"]:
            try:
                content = ""
                if fp.suffix.lower() in [".txt", ".md"]:
                    content = fp.read_text(encoding="utf-8", errors="ignore")
                elif fp.suffix.lower() == ".pdf":
                    import PyPDF2
                    with open(fp, "rb") as f:
                        reader = PyPDF2.PdfReader(f)
                        pages = [pg.extract_text() or "" for pg in reader.pages]
                        content = "\n".join(pages)
                
                if content.strip():
                    documents.append({
                        "content": content,
                        "metadata": {"source": fp.name, "path": str(fp)}
                    })
            except Exception as e:
                print(f"failed to read {fp}: {e}")
    return documents

def main():
    Path(DB_DIR).mkdir(parents=True, exist_ok=True)
    model = SentenceTransformer(EMB_MODEL)
    client = chromadb.PersistentClient(path=DB_DIR)
    coll = client.get_or_create_collection(COLL)

    # Load docs
    docs = load_documents("kb/text")
    print(f"found {len(docs)} documents in kb/text")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,
        chunk_overlap=100,
        separators=["\n\n", "\n", " ", ""]
    )

    all_chunks = []
    all_metadatas = []
    
    for doc in docs:
        chunks = splitter.split_text(doc["content"])
        all_chunks.extend(chunks)
        for i, _ in enumerate(chunks):
            meta = doc["metadata"].copy()
            meta["chunk_id"] = i
            all_metadatas.append(meta)

    print(f"total chunks to ingest: {len(all_chunks)}")

    if all_chunks:
        embs = model.encode(all_chunks, normalize_embeddings=True).tolist()
        coll.upsert(
            ids=[f"{m['source']}-{m['chunk_id']}" for m in all_metadatas],
            documents=all_chunks,
            embeddings=embs,
            metadatas=all_metadatas,
        )
        print(f"ingested {len(all_chunks)} chunks.")
    else:
        print("no chunks found. add files to kb/ first.")

if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()