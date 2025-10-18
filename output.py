import os
from dotenv import load_dotenv
from openai import OpenAI
from retriever import retrieve

# Load API key from .env file
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_answer(query: str):
    # Step 1: Retrieve relevant docs from Chroma
    results = retrieve(query)
    docs = results["docs"]

    # Step 2: Combine retrieved chunks as context
    context = "\n\n".join(docs)

    # Step 3: Ask the model to answer based on context
    prompt = f"""
You are an intelligent assistant that answers questions based on provided context.

Context:
{context}

Question:
{query}

Answer clearly and concisely based only on the context above.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",  # or gpt-4-turbo / gpt-3.5-turbo
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
    )

    return response.choices[0].message.content.strip()

if __name__ == "__main__":
    while True:
        q = input("Ask your question (or 'exit'): ")
        if q.lower() in ["exit", "quit"]:
            break
        ans = generate_answer(q)
        print("\nAnswer:\n", ans, "\n")
