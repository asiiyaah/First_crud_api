import logging
import random
import time
from dataclasses import dataclass
from email.utils import parsedate_to_datetime
from datetime import datetime, timezone
from typing import Any, Protocol

from openai import (
    APIError,
    APIStatusError,
    APITimeoutError,
    AuthenticationError,
    BadRequestError,
    InternalServerError,
    OpenAI,
    PermissionDeniedError,
    RateLimitError,
)

from . import config


logger = logging.getLogger("llm")


class ProviderTimeoutError(Exception):
    """The provider did not respond within the configured timeout."""


class ProviderRequestError(Exception):
    """A provider request failed and should be surfaced to the API."""


@dataclass
class ProviderResult:
    content: str
    input_tokens: int
    output_tokens: int
    duration_ms: int
    refusal: str | None = None


class LLMProvider(Protocol):
    name: str
    model: str

    def complete(
        self,
        *,
        system_prompt: str,
        user_input: str,
    ) -> ProviderResult:
        ...


def _retry_after_seconds(exc: Exception) -> float | None:
    response = getattr(exc, "response", None)
    headers = getattr(response, "headers", None)
    if not headers:
        return None

    value = headers.get("retry-after") or headers.get("Retry-After")
    if not value:
        return None

    try:
        return max(0.0, float(value))
    except ValueError:
        pass

    try:
        target = parsedate_to_datetime(value)
        if target.tzinfo is None:
            target = target.replace(tzinfo=timezone.utc)
        return max(0.0, (target - datetime.now(timezone.utc)).total_seconds())
    except (TypeError, ValueError, OverflowError):
        return None


def _status_code(exc: Exception) -> int | None:
    response = getattr(exc, "response", None)
    return getattr(response, "status_code", None)


def _is_retryable(exc: Exception) -> bool:
    if isinstance(exc, APITimeoutError):
        return True

    status = _status_code(exc)

    if isinstance(exc, RateLimitError) or status == 429:
        return True

    if status is not None and 500 <= status <= 599:
        return True

    if isinstance(exc, InternalServerError):
        return True

    return False


class OpenAICompatibleProvider:
    """OpenAI-compatible provider with explicit bounded retry policy."""

    name = "openai-compatible"

    def __init__(
        self,
        *,
        base_url: str,
        api_key: str,
        model: str,
        timeout: float,
        max_retries: int,
        structured_output: bool,
        temperature: float,
    ) -> None:
        self.base_url = base_url
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self.max_retries = max_retries
        self.structured_output = structured_output
        self.temperature = temperature

        # Disable SDK retries. Retry policy is owned by this module so that
        # 400/401/403 are never silently retried.
        self.client = OpenAI(
            base_url=base_url,
            api_key=api_key,
            timeout=timeout,
            max_retries=0,
        )

    def complete(
        self,
        *,
        system_prompt: str,
        user_input: str,
    ) -> ProviderResult:
        return self._request(system_prompt=system_prompt, user_input=user_input)

    def _request(
        self,
        *,
        system_prompt: str,
        user_input: str,
    ) -> ProviderResult:
        last_error: Exception | None = None

        for attempt in range(self.max_retries + 1):
            started = time.perf_counter()

            try:
                kwargs: dict[str, Any] = {
                    "model": self.model,
                    "temperature": self.temperature,
                    "messages": [
                        {
                            "role": "system",
                            "content": system_prompt,
                        },
                        {
                            "role": "user",
                            "content": user_input,
                        },
                    ],
                }

                if self.structured_output:
                    kwargs["response_format"] = {"type": "json_object"}

                response = self.client.chat.completions.create(**kwargs)

                duration_ms = int(
                    (time.perf_counter() - started) * 1000
                )

                choice = response.choices[0]
                message = choice.message

                usage = response.usage
                input_tokens = int(
                    getattr(usage, "prompt_tokens", 0) or 0
                )
                output_tokens = int(
                    getattr(usage, "completion_tokens", 0) or 0
                )

                refusal = getattr(message, "refusal", None)
                content = message.content or ""

                return ProviderResult(
                    content=content,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    duration_ms=duration_ms,
                    refusal=refusal,
                )

            except (AuthenticationError, PermissionDeniedError) as exc:
                # Explicitly non-retryable.
                raise ProviderRequestError(
                    f"LLM provider rejected authentication/permission "
                    f"(HTTP {_status_code(exc) or 401})."
                ) from exc

            except BadRequestError as exc:
                # Explicitly non-retryable.
                raise ProviderRequestError(
                    f"LLM provider rejected the request "
                    f"(HTTP {_status_code(exc) or 400})."
                ) from exc

            except (
                APITimeoutError,
                RateLimitError,
                InternalServerError,
                APIStatusError,
                APIError,
            ) as exc:
                last_error = exc

                if not _is_retryable(exc):
                    raise ProviderRequestError(
                        "LLM provider request failed."
                    ) from exc

                if attempt >= self.max_retries:
                    if isinstance(exc, APITimeoutError):
                        raise ProviderTimeoutError(
                            "LLM provider request timed out."
                        ) from exc
                    raise ProviderRequestError(
                        "LLM provider request failed after retries."
                    ) from exc

                retry_after = _retry_after_seconds(exc)

                if retry_after is not None:
                    delay = retry_after
                else:
                    # 1s, 2s, 4s plus small jitter.
                    delay = config.RETRY_BASE_SECONDS * (2**attempt)
                    delay += random.uniform(
                        0.0,
                        config.RETRY_MAX_JITTER_SECONDS,
                    )

                logger.warning(
                    "LLM provider retry: attempt=%d/%d delay=%.2fs status=%s",
                    attempt + 1,
                    self.max_retries,
                    delay,
                    _status_code(exc),
                )
                time.sleep(delay)

        raise ProviderRequestError("LLM provider request failed.") from last_error


class OllamaProvider(OpenAICompatibleProvider):
    name = "ollama"


class OpenRouterProvider(OpenAICompatibleProvider):
    name = "openrouter"


def get_provider() -> LLMProvider:
    common = {
        "base_url": config.LLM_BASE_URL,
        "api_key": config.LLM_API_KEY,
        "model": config.LLM_MODEL,
        "timeout": config.LLM_TIMEOUT,
        "max_retries": config.LLM_MAX_RETRIES,
        "structured_output": config.LLM_STRUCTURED_OUTPUT,
        "temperature": config.LLM_TEMPERATURE,
    }

    if config.LLM_PROVIDER == "ollama":
        return OllamaProvider(**common)

    if config.LLM_PROVIDER == "openrouter":
        return OpenRouterProvider(**common)

    raise ValueError(
        f"Unsupported LLM_PROVIDER: {config.LLM_PROVIDER}. "
        "Use 'ollama' or 'openrouter'."
    )
