from retriever import retrieve

# result = retrieve("""sections 473 and 474""")
# print(result)

from output import generate_answer

ans = generate_answer("my neighbour is throwing waste in my area, what should I do?")
import json
print("Response from Ollama:")
print(json.dumps(ans, indent=2, ensure_ascii=True))
