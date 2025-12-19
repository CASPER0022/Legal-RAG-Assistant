# Legal Ease

A lightweight, private, retrieval‑augmented legal Q&A system. It ingests your legal documents, performs semantic search via embeddings + ChromaDB, and uses an LLM to produce structured answers with legal terms and article numbers.

## Overview

- Grounded answers from your own corpus (stored under `kb/text/`).
- Fast semantic retrieval using `sentence-transformers/all-MiniLM-L6-v2`.
- Local vector store with ChromaDB (`data/vec`).
- Structured outputs (answer, legal_terms, relevant_articles, confidence).
- CLI (`output.py`) and web UI (`streamlit_app.py` using Streamlit).
- Safety: when no docs match, returns an explicit "no documents found" response (avoids hallucinations).

## Project Structure

```
legal-ease/
  app.py                # (empty placeholder)
  cache.py              # Optional Redis cache helper
  docker-compose.yml    # (if you later run Redis via Docker)
  graph_flow.py         # (empty placeholder)
  graphdb.py            # (empty placeholder)
  ingest.py             # Ingests text docs → embeddings → ChromaDB
  retriever.py          # Semantic retrieval from ChromaDB
  retriever_test.py     # Simple test driver
  schemas.py            # (empty placeholder)
  vlm.py                # (empty placeholder)
  output.py             # CLI Q&A; structured JSON; history persistence
  streamlit_app.py      # ChatGPT-like web interface (Streamlit)
  kb/
    images/             # (optional future image captions)
    text/               # Place your .txt/.md documents here
      Albin.txt         # Example doc
  data/vec/             # ChromaDB persistence directory (created at runtime)
```

## Prerequisites

- Python 3.10+
- Windows PowerShell (commands below use PowerShell syntax)
- An OpenAI API key (do NOT commit this to git)

## Quick Start (PowerShell)

From the repo root (`E:\\Legal Ease\\legal-ease`):

```powershell
# 1) Create and activate a virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2) Install dependencies
python -m pip install --upgrade pip
python -m pip install streamlit openai chromadb sentence-transformers redis python-dotenv

# 3) Configure your key (temp for current session)
$env:OPENAI_API_KEY = "sk-REPLACE_WITH_YOUR_KEY"
# Or create a local .env file (see Configuration below)

# 4) Add documents and ingest
# Place .txt/.md files under .\kb\text\
python .\ingest.py

# 5) Run the web app
streamlit run .\streamlit_app.py
# Open http://localhost:8501
```

## Configuration

- `.env` (do not commit):
  ```env
  OPENAI_API_KEY=sk-REPLACE_WITH_YOUR_KEY
  REDIS_HOST=localhost   # optional, if you enable cache.py
  ```
- Ensure `.env` is in `.gitignore`. If `.env` was committed previously, ROTATE your key and remove the file from history (see Safety Notes).

## Data Ingestion

- Add plain text files into `kb/text/` (`.txt` or `.md`).
- Run: `python ingest.py`
  - Chunks text (size=500, overlap=50)
  - Embeds with `all-MiniLM-L6-v2`
  - Upserts into ChromaDB under `data/vec`

## CLI Usage

Run the structured Q&A CLI:

```powershell
.\.venv\Scripts\Activate.ps1
python .\output.py
```

- Prompts for your question.
- Returns structured JSON (answer, `legal_terms`, `relevant_articles`, `confidence`).
- Stores recent conversation in `chat_history.json` (bounded size). New sessions can start fresh.
- If retrieval returns zero docs, it returns an explicit "no documents found" response instead of calling the LLM.

## Streamlit Web UI

```powershell
.\.venv\Scripts\Activate.ps1
streamlit run .\streamlit_app.py
```

Features:

- ChatGPT‑like interface (`st.chat_input` & `st.chat_message`).
- Sidebar: "New chat" (clears session history) and "Clear stored history file" (moves `chat_history.json` → `.bak`).
- Assistant answers render a readable, formatted view; raw JSON is available in an expander.
- Session‑only history in the web UI (no auto‑save to disk).

## How It Works

- `retriever.py`: initializes a persistent Chroma client and a SentenceTransformer model; encodes the query and retrieves top‑k chunks.
- `output.py`: builds a prompt with retrieved context and asks the OpenAI chat model for structured JSON (legal terms + article numbers). Includes safe fallback when no docs are found.
- `cache.py` (optional): Redis cache to speed repeated retrievals.

## Troubleshooting

- Streamlit warning "missing ScriptRunContext": run with `streamlit run .\streamlit_app.py` (do not use `python streamlit_app.py`).
- Slow installs on Windows (torch): `sentence-transformers` may install CPU‑only `torch` by default. For GPU, install a matching wheel from https://pytorch.org/get-started/locally/.
- No results from retrieval: ensure you ingested docs (`python ingest.py`) and the query matches your KB domain. Increase `k` or adjust chunk size/overlap if needed.

## Safety Notes (Secrets & Git)

- Never commit `.env` or any API keys.
- If a secret was committed:
  1. Rotate/revoke the key immediately in the provider dashboard.
  2. Stop tracking `.env`: `git rm --cached .env; git commit -m "Stop tracking .env"`.
  3. Rewrite history with `git-filter-repo` or BFG to remove `.env`, then force‑push.
  4. Verify push protection no longer blocks.
- Keep `.env` in `.gitignore` and use environment variables in CI/deploys.

## Roadmap / Ideas

- Add PDF/OCR ingestion support.
- Add metadata (jurisdiction, source, date) and surface in answers.
- Optional streaming responses in the UI for perceived speed.
- Swap hosted LLM for a local/open model for privacy.
- Evaluation harness (Precision@k, human correctness) and sample dataset.

## License

Add a license if you plan to share publicly (MIT/Apache‑2.0 recommended). Currently, no license file is included.
