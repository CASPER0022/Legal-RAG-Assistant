from pathlib import Path
from sentence_transformers import SentenceTransformer
import chromadb

EMB_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
DB_DIR = "data/vec" 
COLL = "kb_chunks"

def chunk_text(txt, size=500,overlap=50):
    out=[]
    i=0
    while i < len(txt):
        out.append(txt[i:i+size])
        i+=size-overlap
    return out
    
def load_text_dir(p):
    texts = []
    for fp in Path(p).glob("**/*"):
        if fp.suffix.lower() in [".txt", ".md", ".pdf"]:
            try:
                if fp.suffix.lower() in [".txt", ".md"]:
                    texts.append(fp.read_text(encoding="utf-8", errors="ignore"))
                elif fp.suffix.lower() == ".pdf":
                    # extract pdf text using PyPDF2
                    import PyPDF2
                    with open(fp, "rb") as f:
                        reader = PyPDF2.PdfReader(f)
                        pages = []
                        for pg in reader.pages:
                            pages.append(pg.extract_text() or "")
                        texts.append("\n".join(pages))
            except Exception as e:
                print(f"failed to read {fp}: {e}")
    return texts

def main():
    Path(DB_DIR).mkdir(parents=True, exist_ok=True)
    model = SentenceTransformer(EMB_MODEL)
    client = chromadb.PersistentClient(path=DB_DIR)
    coll = client.get_or_create_collection(COLL)

    # 1) text
    docs = load_text_dir("kb/text")
    print(f"found {len(docs)} documents in kb/text")
    for i,d in enumerate(docs):
        print(f" doc {i} length: {len(d)} chars")

    chunks = []
    for d in docs:
        chunks += chunk_text(d)

    print(f"total chunks to ingest: {len(chunks)}")

    # 2) images → TODO: caption later; for now, skip or store filenames as "captions"
    # for img in Path("kb/images").glob("*"):
    #     chunks.append(f"Image placeholder: {img.name} (caption TODO)")

    if chunks:
        embs = model.encode(chunks, normalize_embeddings=True).tolist()
        coll.upsert(
            ids=[f"id-{i}" for i in range(len(chunks))],
            documents=chunks,
            embeddings=embs,
            metadatas=[{"source": "kb"} for _ in chunks],  
        )

        print(f"ingested {len(chunks)} chunks.")
    else:
        print("no chunks found. add files to kb/ first.")

if __name__ == "__main__":
    main()