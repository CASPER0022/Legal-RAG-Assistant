import os
import pandas as pd
from retriever import retrieve
from output import generate_answer
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevance, context_precision, context_recall
from datasets import Dataset

# Note: In a real scenario, you'd have a manually curated golden dataset.
# For demonstration, we'll use a small set of queries and expected answers.

EVAL_DATA = [
    {
        "question": "What is the penalty for theft?",
        "ground_truth": "The penalty for theft varies by jurisdiction but typically involves imprisonment or fines depending on the value of the stolen goods."
    },
    {
        "question": "How many years is the sentence for fraud?",
        "ground_truth": "Sentences for fraud depend on the severity and scale, often ranging from 1 to 10 years or more."
    },
    {
        "question": "What are the legal requirements for a valid contract?",
        "ground_truth": "A valid contract requires offer, acceptance, consideration, and the intention to create legal relations."
    }
]

def run_evaluation():
    print("Starting RAG Evaluation...")
    
    questions = []
    answers = []
    contexts = []
    ground_truths = []
    
    for item in EVAL_DATA:
        q = item["question"]
        print(f"Evaluating query: {q}")
        
        # 1. Retrieve
        retrieval_res = retrieve(q)
        retrieved_docs = retrieval_res["docs"]
        
        # 2. Generate
        generation_res = generate_answer(q)
        ans = generation_res.get("answer") or generation_res.get("answer_text")
        
        questions.append(q)
        answers.append(ans)
        contexts.append(retrieved_docs)
        ground_truths.append(item["ground_truth"])
        
    # Create dataset for Ragas
    data_dict = {
        "question": questions,
        "answer": answers,
        "contexts": contexts,
        "ground_truth": ground_truths
    }
    
    dataset = Dataset.from_dict(data_dict)
    
    # Run Ragas evaluation
    # Note: Ragas usually requires an OpenAI API key for LLM-based metrics
    result = evaluate(
        dataset,
        metrics=[
            faithfulness,
            answer_relevance,
            context_precision,
            context_recall,
        ],
    )
    
    print("\n--- Evaluation Results ---")
    print(result)
    
    # Save to CSV for the portfolio
    df = result.to_pandas()
    df.to_csv("rag_evaluation_results.csv", index=False)
    print("\nResults saved to rag_evaluation_results.csv")

if __name__ == "__main__":
    if not os.getenv("OLLAMA_API_KEY") and not os.getenv("OPENAI_API_KEY"):
        print("Warning: OLLAMA_API_KEY or OPENAI_API_KEY not found. Ragas or Ollama calls may fail.")
    run_evaluation()
