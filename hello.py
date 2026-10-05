import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

client = OpenAI(
    base_url=os.getenv(
        "LLM_BASE_URL",
        "http://localhost:11434/v1",
    ),
    api_key=os.getenv("LLM_API_KEY", "ollama"),
    timeout=min(float(os.getenv("LLM_TIMEOUT", "30")), 60.0),
    max_retries=0,
)

response = client.chat.completions.create(
    model=os.getenv("LLM_MODEL", "gemma3:1b"),
    temperature=0,
    messages=[
        {
            "role": "user",
            "content": "Reply with exactly the word: ready",
        }
    ],
)

print(response.choices[0].message.content)
