import os

from dotenv import load_dotenv

load_dotenv()

PROMPT_VERSION = os.getenv("PROMPT_VERSION", "triage-v1")

LLM_ENABLED = os.getenv("LLM_ENABLED", "true").lower() == "true"
LLM_STUB = os.getenv("LLM_STUB", "0") == "1"

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama").lower()
LLM_BASE_URL = os.getenv(
    "LLM_BASE_URL",
    "http://host.docker.internal:11434/v1",
)
LLM_API_KEY = os.getenv("LLM_API_KEY", "ollama")
LLM_MODEL = os.getenv("LLM_MODEL", "gemma3:1b")

LLM_TIMEOUT = min(float(os.getenv("LLM_TIMEOUT", "30")), 60.0)
LLM_MAX_RETRIES = max(0, min(int(os.getenv("LLM_MAX_RETRIES", "3")), 3))

LLM_MAX_INPUT_TOKENS = max(
    1,
    int(os.getenv("LLM_MAX_INPUT_TOKENS", "4000")),
)

LLM_CACHE_ENABLED = os.getenv("LLM_CACHE_ENABLED", "false").lower() == "true"
LLM_STRUCTURED_OUTPUT = (
    os.getenv("LLM_STRUCTURED_OUTPUT", "false").lower() == "true"
)

LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.0"))

# Local and hosted OpenAI-compatible providers can have different prices.
# Ollama is local, so its cost is zero.
LLM_INPUT_COST_PER_1K = float(os.getenv("LLM_INPUT_COST_PER_1K", "0"))
LLM_OUTPUT_COST_PER_1K = float(os.getenv("LLM_OUTPUT_COST_PER_1K", "0"))

# Keep jitter bounded and testable.
RETRY_BASE_SECONDS = float(os.getenv("RETRY_BASE_SECONDS", "1.0"))
RETRY_MAX_JITTER_SECONDS = float(
    os.getenv("RETRY_MAX_JITTER_SECONDS", "0.25")
)
