import argparse
import json
from pathlib import Path

import httpx


def load_cases():
    return json.loads(
        (Path(__file__).with_name("cases.json")).read_text(
            encoding="utf-8"
        )
    )


def score_url(client, url, cases):
    matched = 0
    for case in cases:
        try:
            response = client.post(
                url,
                json={"text": case["text"]},
                timeout=45,
            )
            if response.status_code != 200:
                continue
            result = response.json()
            expected = case["expected"]
            matched += (
                result.get("category") == expected["category"]
                and result.get("priority") == expected["priority"]
            )
        except httpx.RequestError:
            continue
    return matched


def main():
    parser = argparse.ArgumentParser(
        description="Compare two running model-backed triage endpoints."
    )
    parser.add_argument("--url-a", required=True)
    parser.add_argument("--url-b", required=True)
    args = parser.parse_args()

    cases = load_cases()

    with httpx.Client() as client:
        score_a = score_url(client, args.url_a, cases)
        score_b = score_url(client, args.url_b, cases)

    print(f"Model A: {score_a}/{len(cases)}")
    print(f"Model B: {score_b}/{len(cases)}")


if __name__ == "__main__":
    main()
