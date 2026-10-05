from pathlib import Path

from fastapi import HTTPException
from openai import OpenAI
from pydantic import ValidationError

from .schema import TriageResponse


PROMPT_VERSION = "triage-v1"


def load_prompt() -> str:
    prompt_path = (
        Path(__file__).resolve().parent.parent
        / "prompts"
        / "triage-v1.md"
    )

    return prompt_path.read_text(encoding="utf-8")


def triage_task(text: str) -> TriageResponse:
    prompt = load_prompt().replace("{{text}}", text)

    client = OpenAI(
        base_url="http://host.docker.internal:11434/v1",
        api_key="ollama",
    )

    response = client.chat.completions.create(
        model="gemma3:1b",
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    content = response.choices[0].message.content.strip()

    if content.startswith("```json"):
        content = content[7:]

    if content.endswith("```"):
        content = content[:-3]

    content = content.strip()

    try:
        return TriageResponse.model_validate_json(content)
    except ValidationError as exc:
        raise HTTPException(
            status_code=502,
            detail="LLM returned an invalid triage response.",
            ) from exc
