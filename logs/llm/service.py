import hashlib
import json
import logging
import time
from pathlib import Path
from typing import Any

from fastapi import HTTPException
from pydantic import ValidationError

from . import config
from .providers import (
    ProviderRequestError,
    ProviderTimeoutError,
    get_provider,
)
from .schema import TriageResponse


CONFIDENCE_THRESHOLD = 0.6

logger = logging.getLogger("llm")


class _ResponseCache:
    def __init__(self) -> None:
        self._data: dict[str, TriageResponse] = {}

    def get(self, key: str) -> TriageResponse | None:
        result = self._data.get(key)
        if result is None:
            return None
        return result.model_copy(deep=True)

    def set(self, key: str, value: TriageResponse) -> None:
        self._data[key] = value.model_copy(deep=True)


_CACHE = _ResponseCache()


def load_prompt(version: str | None = None) -> str:
    version = version or config.PROMPT_VERSION
    prompt_path = (
        Path(__file__).resolve().parent.parent
        / "prompts"
        / f"{version}.md"
    )

    if not prompt_path.exists():
        raise HTTPException(
            status_code=500,
            detail=f"Prompt version '{version}' is not available.",
        )

    return prompt_path.read_text(encoding="utf-8")


def _user_message(text: str) -> str:
    # Keep untrusted data in the user role and JSON-encode it so quotes and
    # prompt-like content cannot alter the system prompt.
    return json.dumps(
        {"task": text},
        ensure_ascii=False,
    )


def _extract_json(content: str) -> str:
    content = content.strip()

    if content.startswith("```"):
        first_newline = content.find("\n")
        if first_newline != -1:
            content = content[first_newline + 1 :]
        if content.endswith("```"):
            content = content[:-3].strip()

    # Some providers prepend a sentence. Extract the first JSON object.
    start = content.find("{")
    end = content.rfind("}")
    if start == -1 or end <= start:
        raise ValueError("No JSON object found in model output.")

    return content[start : end + 1]


def _parse_response(content: str) -> TriageResponse:
    cleaned = _extract_json(content)
    return TriageResponse.model_validate_json(cleaned)


def _quarantine(
    *,
    text: str,
    raw_output: str,
    error: str,
    prompt_version: str,
) -> None:
    path = (
        Path(__file__).resolve().parent.parent
        / "logs"
        / "quarantine.jsonl"
    )
    path.parent.mkdir(parents=True, exist_ok=True)

    record = {
        "timestamp": time.time(),
        "input": text,
        "raw_output": raw_output,
        "error": error,
        "prompt_version": prompt_version,
    }

    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def _token_count(text: str) -> int:
    try:
        import tiktoken

        encoder = tiktoken.get_encoding("cl100k_base")
        return len(encoder.encode(text))
    except Exception:
        # Safe fallback for environments where the optional tokenizer cannot
        # load. It intentionally overestimates instead of underestimating.
        return max(1, (len(text) + 2) // 3)


def _preflight_token_count(system_prompt: str, user_message: str) -> int:
    # Count both messages before the provider call.
    return _token_count(system_prompt) + _token_count(user_message)


def _estimated_cost_usd(input_tokens: int, output_tokens: int) -> float:
    return (
        input_tokens / 1000 * config.LLM_INPUT_COST_PER_1K
        + output_tokens / 1000 * config.LLM_OUTPUT_COST_PER_1K
    )


def _log_call(
    *,
    prompt_version: str,
    model: str,
    input_tokens: int | None,
    output_tokens: int | None,
    duration_ms: int | None,
    repair_count: int,
    status: str,
    estimated_cost_usd: float = 0.0,
) -> None:
    event = {
        "event": "llm_call",
        "prompt_version": prompt_version,
        "model": model,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "duration_ms": duration_ms,
        "repair_count": repair_count,
        "estimated_cost_usd": round(estimated_cost_usd, 8),
        "status": status,
    }
    logger.info(json.dumps(event, separators=(",", ":")))


def _fallback() -> TriageResponse:
    return TriageResponse(
        category="other",
        priority="normal",
        confidence=0.0,
        reason="AI triage is disabled; using the deterministic fallback.",
    )


def _apply_confidence_fallback(result: TriageResponse) -> TriageResponse:
    if result.confidence < CONFIDENCE_THRESHOLD:
        logger.warning(
            "AI triage confidence below threshold: %.2f < %.2f",
            result.confidence,
            CONFIDENCE_THRESHOLD,
        )

        return result.model_copy(
            update={
                "category": "other",
                "priority": "normal",
                "reason": (
                    "The model was not confident enough to classify this request."
                ),
            }
        )

    return result


def triage_task(text: str) -> TriageResponse:
    logger.info("AI triage request started")

    if not config.LLM_ENABLED:
        logger.info("AI triage kill switch active; no provider call made")
        return _fallback()

    if config.LLM_STUB:
        logger.info("AI triage stub mode active; no provider call made")
        return TriageResponse(
            category="feature",
            priority="normal",
            confidence=0.99,
            reason="Deterministic stub response.",
        )

    prompt_version = config.PROMPT_VERSION
    system_prompt = load_prompt(prompt_version)
    user_message = _user_message(text)

    cache_key = hashlib.sha256(
        f"{prompt_version}\0{text}".encode("utf-8")
    ).hexdigest()

    if config.LLM_CACHE_ENABLED:
        cached = _CACHE.get(cache_key)
        if cached is not None:
            logger.info("AI triage cache hit")
            return cached

    estimated_input_tokens = _preflight_token_count(
        system_prompt,
        user_message,
    )

    if estimated_input_tokens > config.LLM_MAX_INPUT_TOKENS:
        logger.warning(
            "AI triage request rejected before provider call: "
            "estimated_input_tokens=%d limit=%d",
            estimated_input_tokens,
            config.LLM_MAX_INPUT_TOKENS,
        )
        raise HTTPException(
            status_code=413,
            detail=(
                "Input exceeds the configured token limit "
                f"({config.LLM_MAX_INPUT_TOKENS})."
            ),
        )

    provider = get_provider()

    try:
        response = provider.complete(
            system_prompt=system_prompt,
            user_input=user_message,
        )

        _log_call(
            prompt_version=prompt_version,
            model=provider.model,
            input_tokens=response.input_tokens or estimated_input_tokens,
            output_tokens=response.output_tokens,
            duration_ms=response.duration_ms,
            repair_count=0,
            status="success",
            estimated_cost_usd=_estimated_cost_usd(
                response.input_tokens or estimated_input_tokens,
                response.output_tokens,
            ),
        )

    except ProviderTimeoutError as exc:
        logger.error("AI triage provider timed out")
        _log_call(
            prompt_version=prompt_version,
            model=provider.model,
            input_tokens=estimated_input_tokens,
            output_tokens=None,
            duration_ms=None,
            repair_count=0,
            status="timeout",
        )
        raise HTTPException(
            status_code=504,
            detail="LLM request timed out.",
        ) from exc

    except ProviderRequestError as exc:
        logger.error("AI triage provider request failed: %s", exc)
        _log_call(
            prompt_version=prompt_version,
            model=provider.model,
            input_tokens=estimated_input_tokens,
            output_tokens=None,
            duration_ms=None,
            repair_count=0,
            status="provider_error",
        )
        raise HTTPException(
            status_code=502,
            detail="LLM provider request failed.",
        ) from exc

    logger.info("AI triage LLM response received")

    if response.refusal:
        first_error = f"Model refusal: {response.refusal}"
    else:
        try:
            result = _parse_response(response.content)
            result = _apply_confidence_fallback(result)

            logger.info(
                "AI triage response validated: category=%s priority=%s confidence=%.2f",
                result.category,
                result.priority,
                result.confidence,
            )

            if config.LLM_CACHE_ENABLED:
                _CACHE.set(cache_key, result)

            return result

        except (ValidationError, ValueError, json.JSONDecodeError) as exc:
            first_error = str(exc)

    logger.warning(
        "AI triage response failed validation. Starting one repair attempt."
    )

    repair_message = json.dumps(
        {
            "task": text,
            "previous_output": response.content,
            "validation_error": first_error,
            "instruction": (
                "Your previous answer was rejected for this reason. "
                "Return only corrected JSON matching the schema."
            ),
        },
        ensure_ascii=False,
    )

    repair_input_tokens = _preflight_token_count(
        system_prompt,
        repair_message,
    )
    if repair_input_tokens > config.LLM_MAX_INPUT_TOKENS:
        logger.warning(
            "AI triage repair rejected before provider call: "
            "estimated_input_tokens=%d limit=%d",
            repair_input_tokens,
            config.LLM_MAX_INPUT_TOKENS,
        )
        raise HTTPException(
            status_code=413,
            detail=(
                "Repair request exceeds the configured token limit "
                f"({config.LLM_MAX_INPUT_TOKENS})."
            ),
        )

    try:
        repair_response = provider.complete(
            system_prompt=system_prompt,
            user_input=repair_message,
        )

        _log_call(
            prompt_version=prompt_version,
            model=provider.model,
            input_tokens=repair_response.input_tokens,
            output_tokens=repair_response.output_tokens,
            duration_ms=repair_response.duration_ms,
            repair_count=1,
            status="repair_success",
            estimated_cost_usd=_estimated_cost_usd(
                repair_response.input_tokens,
                repair_response.output_tokens,
            ),
        )

        logger.info("AI triage repair response received")

    except ProviderTimeoutError as exc:
        logger.error("AI triage repair request timed out")
        raise HTTPException(
            status_code=504,
            detail="LLM request timed out.",
        ) from exc

    except ProviderRequestError as exc:
        logger.error("AI triage repair provider request failed: %s", exc)
        raise HTTPException(
            status_code=502,
            detail="LLM provider request failed.",
        ) from exc

    try:
        if repair_response.refusal:
            raise ValueError(
                f"Model refusal: {repair_response.refusal}"
            )

        result = _parse_response(repair_response.content)
        result = _apply_confidence_fallback(result)

        logger.info(
            "AI triage response validated: category=%s priority=%s confidence=%.2f",
            result.category,
            result.priority,
            result.confidence,
        )

        if config.LLM_CACHE_ENABLED:
            _CACHE.set(cache_key, result)

        return result

    except (ValidationError, ValueError, json.JSONDecodeError) as exc:
        logger.error(
            "AI triage repair failed validation; quarantining response"
        )

        _quarantine(
            text=text,
            raw_output=repair_response.content,
            error=str(exc),
            prompt_version=prompt_version,
        )

        raise HTTPException(
            status_code=422,
            detail="LLM response could not be repaired.",
        ) from exc
