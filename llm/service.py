import logging
from pathlib import Path

from fastapi import HTTPException
from openai import APIError, APITimeoutError, OpenAI
from pydantic import ValidationError

from .schema import TriageResponse


PROMPT_VERSION = "triage-v1"

CONFIDENCE_THRESHOLD = 0.6


logger = logging.getLogger("llm")
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    handler.setFormatter(formatter)
    logger.addHandler(handler)

logger.propagate = False


def load_prompt() -> str:
    prompt_path = (
        Path(__file__).resolve().parent.parent
        / "prompts"
        / "triage-v1.md"
    )

    return prompt_path.read_text(encoding="utf-8")


def triage_task(text: str) -> TriageResponse:
    logger.info("AI triage request started")

    prompt = load_prompt().replace("{{text}}", text)

    client = OpenAI(
        base_url="http://host.docker.internal:11434/v1",
        api_key="ollama",
        timeout=30.0,
        max_retries=1,
    )

    try:
        response = client.chat.completions.create(
            model="gemma3:1b",
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )

    except APITimeoutError as exc:
        logger.error("AI triage LLM request timed out")

        raise HTTPException(
            status_code=504,
            detail="LLM request timed out.",
        ) from exc

    except APIError as exc:
        logger.error("AI triage LLM provider request failed")

        raise HTTPException(
            status_code=502,
            detail="LLM provider request failed.",
        ) from exc

    logger.info("AI triage LLM response received")

    content = response.choices[0].message.content.strip()

    if content.startswith("```json"):
        content = content[7:]

    if content.endswith("```"):
        content = content[:-3]

    content = content.strip()

    try:
        result = TriageResponse.model_validate_json(content)

    except ValidationError as exc:
        logger.error("AI triage returned invalid structured output")

        raise HTTPException(
            status_code=502,
            detail="LLM returned an invalid triage response.",
        ) from exc

    logger.info(
        "AI triage response validated: category=%s priority=%s confidence=%.2f",
        result.category,
        result.priority,
        result.confidence,
    )

    if result.confidence < CONFIDENCE_THRESHOLD:
        logger.warning(
            "AI triage confidence below threshold: %.2f < %.2f",
            result.confidence,
            CONFIDENCE_THRESHOLD,
        )

        result.category = "other"
        result.priority = "normal"
        result.reason = (
            "The model was not confident enough to classify this request."
        )

    return result