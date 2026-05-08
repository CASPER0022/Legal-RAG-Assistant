# ⚖️ LegalEase: Advanced RAG-Powered Legal Advisor

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react)](https://react.dev/)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-v3-38B2AC?logo=tailwind-css)](https://tailwindcss.com/)
[![Framework](https://img.shields.io/badge/Framework-RAG-orange)](https://github.com/langchain-ai/langchain)
[![VectorDB](https://img.shields.io/badge/VectorDB-ChromaDB-green)](https://www.trychroma.com/)
[![Reranker](https://img.shields.io/badge/Reranker-FlashRank-purple)](https://github.com/PrithivirajDamodaran/FlashRank)

**LegalEase** is a production-grade Retrieval-Augmented Generation (RAG) system designed to provide precise, grounded answers to complex legal queries. It has been transformed into a modern full-stack web application featuring a highly optimized **FastAPI** Python backend and a stunning **React + Vite + Tailwind CSS** frontend.

---

## 🚀 Key Features

- **Decoupled Architecture**: Independent, lightweight React frontend communicating seamlessly with a dedicated high-performance Python API.
- **Elite Trial-Advocate Persona**: Powered by local/custom Ollama models (`gpt-oss:120b`), generating rich, authoritative legal strategies formatted elegantly in Markdown.
- **Multi-Stage Retrieval Pipeline**:
  - **Dense Retrieval**: High-dimensional semantic search using `all-MiniLM-L6-v2`.
  - **Second-Stage Re-ranking**: Cross-encoder re-ranking via `FlashRank` to eliminate false positives and refine relevance.
- **Advanced Data Processing**:
  - **Semantic Chunking**: Large semantic chunks (1200 characters) to preserve entire articles, section numbers, and citation cohesiveness.
- **Premium UI/UX**: A dark-mode, responsive React interface with interactive legal term cards, scalable Lucide icons, and beautiful Markdown rendering.

---

## 🏗️ Architecture

```mermaid
graph TD
    A[Legal Documents .pdf, .txt] -->|Backend| B[Recursive Chunking]
    B --> C[Vector Store: ChromaDB]
    D[React Frontend] -->|POST /api/chat| E[FastAPI Backend]
    E --> F[Dense Search]
    F --> G[FlashRank Re-ranking]
    G --> H[Refined Context]
    H --> I[Ollama REST API]
    I --> J[Structured JSON Output]
    J -->|HTTP Response| D
    D --> K[Premium UI Markdown Render]
```

---

## 🛠️ Tech Stack

### Backend (`/backend`)
- **Core API**: Python, FastAPI, Uvicorn
- **Embeddings**: Sentence-Transformers (`all-MiniLM-L6-v2`)
- **Vector DB**: ChromaDB
- **Re-ranker**: FlashRank (Cross-Encoders)
- **LLM Engine**: Ollama REST API (`gpt-oss:120b`)
- **Evaluation**: Ragas, Pandas

### Frontend (`/frontend`)
- **Framework**: React 18, Vite
- **Styling**: Tailwind CSS v3, PostCSS
- **Icons**: Lucide React
- **Parsing**: React-Markdown

---

## 🏁 Getting Started

### 1. Backend Setup
Navigate into the backend directory and install the python dependencies.
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Or .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create a `.env` file in the `backend/` directory:
```env
OLLAMA_API_URL=https://ollama.com/api/generate
OLLAMA_API_KEY=your_api_key
OLLAMA_MODEL=gpt-oss:120b
```

Ingest your legal documents (place PDFs in `backend/kb/text/`):
```bash
python ingest.py
```

Start the API Server:
```bash
uvicorn api:app --reload --port 8000
```

### 2. Frontend Setup
Open a new terminal and navigate to the frontend directory.
```bash
cd frontend
npm install
```

Start the Vite development server:
```bash
npm run dev
```

### 3. Usage
Navigate to `http://localhost:5173` in your browser. Enter a legal query, and the application will instantly retrieve the appropriate laws and formulate a strategic trial-advocate response.

---

## 📂 Project Structure
- `/backend`: Python API, RAG logic, ChromaDB, and document ingestion.
- `/frontend`: React application, Tailwind configs, and chat components.

---

## 📜 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
