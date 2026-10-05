# AI Rematch Prompt

Build a second implementation of the Week 7 A17 LLM triage feature in a separate `ai-version/` folder. Do not modify the hand-built implementation.

The endpoint is `POST /ai/triage`.

Requirements:

1. Validate `text` before any model call. Reject missing, wrong-type, whitespace-only, and over-limit input with HTTP 400 and the offending field.
2. Return exactly:
   - category: bug | feature | task | other
   - priority: low | normal | high
   - confidence: 0.0–1.0
   - reason: short sentence
3. Keep the prompt in a versioned file.
4. Send the system prompt separately from the untrusted user message.
5. Parse and validate all model output with Pydantic.
6. On parse/validation failure, perform exactly one repair attempt containing the broken output and validation error.
7. If repair fails, return 422 and append input, raw output, error, and prompt version to `logs/quarantine.jsonl`.
8. Set an explicit client timeout of 60 seconds or less.
9. Retry only timeouts, 429, and 5xx with exponential backoff and jitter. Never retry 400, 401, or 403. Honour Retry-After.
10. Emit one structured cost log per provider call with prompt version, model, input tokens, output tokens, duration, repair count, and estimated cost.
11. Implement `LLM_ENABLED=false` as a deterministic fallback with no provider call.
12. Put the provider behind an interface with a single `complete(prompt, input)`-style contract and provide Ollama and OpenRouter implementations.
13. Count input tokens before the provider call and reject requests over a configured limit.
14. Include five prompt-injection cases in the 25-case evaluation set.
15. Add caching keyed by input plus prompt version.
16. Include a prompt-v2 variant for an A/B comparison.
17. Handle model refusals as structured-output failures instead of crashing.
18. Keep the generated implementation quarantined under `ai-version/`.

After generating it, run the same API checkpoints and evaluation set. Then write an `AI vs me` README section with at least three named differences, including what the AI did better, what it got wrong, and what the original prompt failed to specify.
