import os
from dotenv import load_dotenv
from openai import OpenAI
from retriever import retrieve
import json
from typing import List, Dict, Any
import re
import datetime
import shutil

# Load API key from .env file
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
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
            # user chose not to continue -> back up the old history and start fresh
            try:
                stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
                backup_name = f"{HISTORY_PATH}.bak.{stamp}"
                shutil.move(HISTORY_PATH, backup_name)
                print(f"Backed up old history to {backup_name}")
            except Exception:
                # if backup fails, try to remove the file to avoid reloading it
                try:
                    os.remove(HISTORY_PATH)
                except Exception:
                    pass

    SESSION_HISTORY = []

def generate_answer(query: str):
    # Step 1: Retrieve relevant docs from Chroma
    results = retrieve(query)
    docs = results["docs"]

    # Step 2: Combine retrieved chunks as context
    context = "\n\n".join(docs)

    # Step 2.5: include recent exchanges from the in-memory session (if any)
    prev_context = get_recent_context(SESSION_HISTORY)
    if prev_context:
        context = prev_context + "\n\nPrevious retrieval context:\n" + context

    # Step 3: Ask the model to answer based on context. Request structured JSON
    # The assistant must ONLY use the provided context and must return a JSON object.
    prompt = f"""
You are a legal research assistant. Use ONLY the provided context (do not hallucinate new laws). ALWAYS REPLY LIKE HOW WE CAN DO? HOW MANY YEARS PENALTY, TALK LIKE AN ADVOCATE

Return a single JSON object (no surrounding explanation) with the following schema:

{{
  "answer": "Short, plain-language answer to the question (1-3 sentences)",
  "legal_terms": [
    {{"term": "Legal term or phrase found in context", "article": "Article number or citation (if found)", "quote": "Exact excerpt from the context proving this", "source": "source filename or id"}}
  ],
  "relevant_articles": [
    {{"article": "Article number or identifier", "reason": "Why this article is relevant (1-2 sentences)"}}
  ],
  "confidence": "low|medium|high (based on how directly the context proves the answer)"
}}

Context:
{context}

Question:
{query}

Important: If an article number or legal term is not present in the context, do NOT invent it — leave the field empty or omit that list item.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",  # or gpt-4-turbo / gpt-3.5-turbo
        messages=[
            {"role": "system", "content": "You are a legal assistant specialized in extracting laws and citations from provided text. Answer in JSON as requested."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.0,
        max_tokens=900,
    )

    answer_text = response.choices[0].message.content.strip()

    # Try to parse structured JSON from the assistant
    parsed: Any = None
    try:
        parsed = json.loads(answer_text)
    except Exception:
        # try to extract the first JSON object in the text
        m = re.search(r"\{[\s\S]*\}", answer_text)
        if m:
            try:
                parsed = json.loads(m.group(0))
            except Exception:
                parsed = None

    # persist this exchange in the session and on disk (store raw assistant text)
    try:
        SESSION_HISTORY.append({"user": query, "assistant": answer_text})
        if len(SESSION_HISTORY) > 50:
            SESSION_HISTORY[:] = SESSION_HISTORY[-50:]
        save_history(SESSION_HISTORY)
    except Exception:
        pass

    if parsed is not None:
        return parsed
    # fallback: return raw text under a key
    return {"answer_text": answer_text}

if __name__ == "__main__":
    def format_parsed_result(parsed: Dict[str, Any]) -> str:
        """Return a human-readable string for the parsed JSON result."""
        lines: List[str] = []
        # Answer
        answer = parsed.get("answer") or parsed.get("answer_text") or "(no answer)"
        lines.append("Answer:")
        lines.append(f"  {answer}")
        lines.append("")

        # Legal terms
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
                    # keep quote to one or two lines for readability
                    qshort = quote.strip().replace("\n", " ")
                    if len(qshort) > 200:
                        qshort = qshort[:197] + "..."
                    lines.append(f"    Quote: {qshort}")
                lines.append("")
        else:
            lines.append("  None found")
            lines.append("")

        # Relevant articles
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

        # Note: 'sources' intentionally omitted from CLI display per user request.
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
