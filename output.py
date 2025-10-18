from retriever import retrieve

# result = retrieve("""sections 473 and 474""")
# print(result)

#CODE THAT SUMMARIZES EVERYTHING FOR ME, WE CAN USE IT LATER..

from openai import OpenAI
client = OpenAI()

result = retrieve("who is albin john")
context = "\n".join(result["docs"])

completion = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": f"Based on the following context, answer clearly: {context}\n\nWho is Albin John?"}
    ]
)

print(completion.choices[0].message.content)
