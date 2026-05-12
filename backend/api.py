from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from output import generate_answer

app = FastAPI(title="LegalEase API", description="Backend API for LegalEase application")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow any origin for development, ideally localhost:5173
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    query: str

@app.post("/api/chat")
def chat_endpoint(request: ChatRequest):
    result = generate_answer(request.query)
    return result

@app.post("/api/clear")
def clear_endpoint():
    from output import reset_session
    reset_session()
    return {"status": "success", "message": "History cleared"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
