from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",
)

response = client.chat.completions.create(
    model="gemma3:1b",
    messages=[
        {
            "role": "user",
            "content": "Reply with exactly the word: ready",
        }
    ],
)

print(response.choices[0].message.content)