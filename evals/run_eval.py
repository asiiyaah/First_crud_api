import argparse
import json
import os
from pathlib import Path

import httpx


DEFAULT_URL = os.getenv(
    "EVAL_URL",
    "http://localhost:3000/ai/triage",
)


def load_cases() -> list[dict]:
    path = Path(__file__).with_name("cases.json")
    return json.loads(path.read_text(encoding="utf-8"))


def run_case(
    client: httpx.Client,
    url: str,
    case: dict,
) -> tuple[bool, dict | None, str | None]:
    try:
        response = client.post(
            url,
            json={"text": case["text"]},
            timeout=45.0,
        )
    except httpx.RequestError as exc:
        return False, None, f"request error: {exc}"

    if response.status_code != 200:
        return False, None, (
            f"HTTP {response.status_code}: "
            f"{response.text[:200]}"
        )

    try:
        result = response.json()
    except ValueError as exc:
        return False, None, f"invalid JSON response: {exc}"

    expected = case["expected"]
    matched = (
        result.get("category") == expected["category"]
        and result.get("priority") == expected["priority"]
    )

    if matched:
        return True, result, None

    return False, result, (
        "expected "
        f"{expected['category']}/{expected['priority']}, "
        "got "
        f"{result.get('category')}/{result.get('priority')}"
    )


def score(results: list[tuple[dict, bool, dict | None, str | None]]) -> None:
    def section(items):
        if not items:
            return 0, 0
        return sum(1 for _, ok, _, _ in items if ok), len(items)

    overall = section(results)
    easy = section([r for r in results if r[0]["difficulty"] == "easy"])
    hard = section([r for r in results if r[0]["difficulty"] == "hard"])

    def pct(pair):
        return (pair[0] / pair[1] * 100) if pair[1] else 0.0

    print(
        f"Overall: {overall[0]}/{overall[1]} "
        f"({pct(overall):.1f}%)"
    )
    print(
        f"Easy: {easy[0]}/{easy[1]} "
        f"({pct(easy):.1f}%)"
    )
    print(
        f"Hard: {hard[0]}/{hard[1]} "
        f"({pct(hard):.1f}%)"
    )

    failures = [r for r in results if not r[1]]
    if failures:
        print("\nFailed cases:")
        for case, _, result, error in failures:
            print(f"- {case['id']}: {error}")
            if result is not None:
                print(f"  response={result}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the triage evaluation set."
    )
    parser.add_argument(
        "--url",
        default=DEFAULT_URL,
        help="Triage endpoint URL.",
    )
    args = parser.parse_args()

    cases = load_cases()
    results = []

    with httpx.Client() as client:
        for case in cases:
            ok, result, error = run_case(
                client,
                args.url,
                case,
            )
            results.append((case, ok, result, error))

    score(results)


if __name__ == "__main__":
    main()
