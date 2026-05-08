import os
import requests
from dotenv import load_dotenv
from retriever import retrieve
import json
from typing import List, Dict, Any
import re
import datetime
import shutil

#Load API key from .env file
load_dotenv()
OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY")
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "https://ollama.com/api/generate")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gpt-oss:120b")
HISTORY_PATH = "chat_history.json"
HISTORY_MAX_EXCHANGES = 3
SESSION_HISTORY: List[Dict[str, str]] = []


def load_history() -> List[Dict[str, str]]:
    """Load conversation history from HISTORY_PATH.

    Returns a list of dicts with keys: 'user' and 'assistant'.
    """
    if not os.path.exists(HISTORY_PATH):
        return []
    try:
        with open(HISTORY_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_history(history: List[Dict[str, str]]):
    try:
        with open(HISTORY_PATH, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def get_recent_context(history: List[Dict[str, str]], n: int = HISTORY_MAX_EXCHANGES) -> str:
    """Return a single string composed of the last n exchanges formatted for prompt context."""
    if not history:
        return ""
    recent = history[-n:]
    parts = []
    for ex in recent:
        user = ex.get("user", "")
        assistant = ex.get("assistant", "")
        parts.append(f"User: {user}\nAssistant: {assistant}")
    return "\n\n".join(parts)


def init_session():
    """Initialize the session history.

    Prompts the user whether to continue the previous conversation. If the user
    chooses to start a new chat, the existing `HISTORY_PATH` file is moved to a
    timestamped backup and the in-memory session starts empty.
    """
    global SESSION_HISTORY
    if os.path.exists(HISTORY_PATH):
        try:
            with open(HISTORY_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = []

        if data:
            ans = input("Previous chat history found. Continue previous conversation? [y/N]: ").strip().lower()
            if ans in ("y", "yes"):
                SESSION_HISTORY = data
                return
            #user chose not to continue -> back up the old history and start fresh
            try:
                stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
                backup_name = f"{HISTORY_PATH}.bak.{stamp}"
                shutil.move(HISTORY_PATH, backup_name) 
                print(f"Backed up old history to {backup_name}")
            except Exception:
                #if backup fails, try to remove the file to avoid reloading it
                try:
                    os.remove(HISTORY_PATH)
                except Exception:
                    pass

    SESSION_HISTORY = []

def generate_answer(query: str):
    #Retrieve relevant docs from Chroma
    results = retrieve(query)
    docs = results["docs"]

    #If retrieval returned no documents, don't call the model — avoid hallucination.
    if not docs:
        return {
            "answer": "No relevant documents were found in the knowledge base for your query. Please add documents to `kb/text` or rephrase your question.",
            "legal_terms": [],
            "relevant_articles": [],
            "sources": [],
            "confidence": "low",
        }

    #Combine retrieved chunks as context with source attribution
    context_parts = []
    metadatas = results.get("metadatas", [])
    for i, doc in enumerate(docs):
        source = metadatas[i].get("source", "Unknown") if i < len(metadatas) else "Unknown"
        context_parts.append(f"[Source: {source}]\n{doc}")
    
    context = "\n\n".join(context_parts)

    #include recent exchanges from the in-memory session (if any)
    prev_context = get_recent_context(SESSION_HISTORY)
    if prev_context:
        context = prev_context + "\n\nPrevious conversation history:\n" + context

    #Ask the model to answer based on context. Request structured JSON
    #The assistant must ONLY use the provided context and must return a JSON object.
    prompt = f"""
You are an elite, highly experienced Trial Advocate and Legal Counsel. Analyze the provided context and deliver authoritative, powerful legal advice directly to your client.

Speak with the voice, confidence, and dramatic flair of a seasoned courtroom attorney. Do not use generic or passive language. Speak directly to the client ("My dear client...", "We shall file...", "Under the law, we can...").

Your advice MUST:
1. State the exact, specific legal steps "we" will take on behalf of the client (e.g., filing a complaint before the Sub-divisional Magistrate).
2. Cite the exact Section/Article numbers found in the context (e.g., Section 152 of the Bharatiya Nagarik Suraksha Sanhita (BNSS), 2023).
3. State the exact consequences, jail time, or fines the offending party will face if they disobey or commit the offense, as detailed in the context (e.g., liability under Section 223 of the Bharatiya Nyaya Sanhita (BNS), 2023, or imprisonment up to 6 months under Section 293 of the BNS).
4. Be beautifully formatted in highly readable Markdown. Use clear paragraphs, bold sub-headers, and numbered/bulleted lists to organize our strategic plan. NEVER output a single giant wall of text.

Return a single JSON object (no surrounding explanation) matching this exact schema:

{{
  "answer": "Your detailed legal advice, written with the authoritative, assertive tone of an advocate. It MUST be beautifully formatted in structured, premium Markdown with clear line breaks, bold headings (e.g., ### Strategy), and clean bullet points. Outline our plan step-by-step, specify the relevant Sections, and clearly detail the penalties, jail time, or fines. Do NOT output a single wall of text.",
  "legal_terms": [
    {{"term": "Legal term or phrase found in context", "article": "Article number or citation (e.g., Section 152 of the BNSS)", "quote": "Exact excerpt from the context proving this", "source": "source filename or id"}}
  ],
  "relevant_articles": [
    {{"article": "Article number or identifier (e.g., Section 152 of the BNSS)", "reason": "Why this article is relevant to our case and what it empowers us to do"}}
  ],
  "confidence": "low|medium|high (based on how directly the context proves the answer)"
}}

Context:
{context}

Question:
{query}

Important: If an article number, section number, or penalty is not present in the provided context, do NOT invent or hallucinate it. Only extract and present what is in the text.
    """

    headers = {
        "Content-Type": "application/json"
    }
    if OLLAMA_API_KEY:
        headers["Authorization"] = f"Bearer {OLLAMA_API_KEY}"

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "system": "You are a legal assistant specialized in extracting laws and citations from provided text. Answer in JSON as requested.",
        "stream": False,
        "format": "json",
        "options": {
            "temperature": 0.0,
            "num_predict": 2048
        }
    }

    try:
        response = requests.post(OLLAMA_API_URL, json=payload, headers=headers, timeout=60)
        response.raise_for_status()
        res_json = response.json()
        answer_text = res_json.get("response", "").strip()
    except Exception as e:
        return {
            "answer": f"Error calling Ollama API: {e}",
            "legal_terms": [],
            "relevant_articles": [],
            "sources": [],
            "confidence": "low",
        }

    #Try to parse structured JSON from the assistant
    parsed: Any = None
    try:
        parsed = json.loads(answer_text)
    except Exception:
        #try to extract the first JSON object in the text
        m = re.search(r"\{[\s\S]*\}", answer_text)
        if m:
            try:
                parsed = json.loads(m.group(0))
            except Exception:
                parsed = None

    #persist this exchange in the session and on disk (store raw assistant text)
    try:
        SESSION_HISTORY.append({"user": query, "assistant": answer_text})
        if len(SESSION_HISTORY) > 50:
            SESSION_HISTORY[:] = SESSION_HISTORY[-50:]
        save_history(SESSION_HISTORY)
    except Exception:
        pass

    if parsed is not None:
        return parsed
    #fallback: return raw text under a key
    return {"answer_text": answer_text}

if __name__ == "__main__":
    def format_parsed_result(parsed: Dict[str, Any]) -> str:
        """Return a human-readable string for the parsed JSON result."""
        lines: List[str] = []
        #Answer
        answer = parsed.get("answer") or parsed.get("answer_text") or "(no answer)"
        lines.append("Answer:")
        lines.append(f"  {answer}")
        lines.append("")

        #Legal terms
        lterms = parsed.get("legal_terms") or []
        lines.append("Legal terms found:")
        if lterms:
            for lt in lterms:
                term = lt.get("term", "")
                article = lt.get("article", "")
                quote = lt.get("quote", "")
                source = lt.get("source", "")
                lines.append(f"- {term}")
                if article:
                    lines.append(f"    Article: {article}")
                if source:
                    lines.append(f"    Source: {source}")
                if quote:
                    #keep quote to one or two lines for readability
                    qshort = quote.strip().replace("\n", " ")
                    if len(qshort) > 200:
                        qshort = qshort[:197] + "..."
                    lines.append(f"    Quote: {qshort}")
                lines.append("")
        else:
            lines.append("  None found")
            lines.append("")

        #Relevant articles
        rarts = parsed.get("relevant_articles") or []
        lines.append("Relevant articles:")
        if rarts:
            for ra in rarts:
                art = ra.get("article", "")
                reason = ra.get("reason", "")
                lines.append(f"- {art}: {reason}")
            lines.append("")
        else:
            lines.append("  None found")
            lines.append("")

        #Note: 'sources' intentionally omitted from CLI display per user request.
        conf = parsed.get("confidence")
        if conf:
            lines.append(f"Confidence: {conf}")

        return "\n".join(lines)

    while True:
        q = input("Ask your question (or 'exit'): ")
        if q.lower() in ["exit", "quit"]:
            break
        ans = generate_answer(q)
        # If we received a parsed dict, pretty-print it; otherwise print raw
        if isinstance(ans, dict) and ("answer" in ans or "legal_terms" in ans or "answer_text" in ans):
            pretty = format_parsed_result(ans)
            print("\n" + pretty + "\n")
        else:
            print("\nAnswer:\n", ans, "\n")
