import argparse
import json
import os
import re
import sys
from typing import List, Optional

import pandas as pd
from anthropic import Anthropic

API_KEY_ENV = "ANTHROPIC_API_KEY"
INPUT_FILE = "review.xlsx"
OUTPUT_FILE = "labeled_reviews.xlsx"
TEST_OUTPUT_FILE = "labeled_reviews_test.xlsx"
MODEL = "claude-haiku-4-5-20251001"
BATCH_SIZE = 10
PROGRESS_INTERVAL = 100

LABEL_CATEGORIES = [
    "Product Quality",
    "Flavour Variety",
    "Service",
    "Wait Time",
    "Store Environment",
    "Price & Value",
    "General Positive",
    "General Negative",
]

SENTIMENTS = ["Positive", "Negative", "Neutral"]

RAW_RESPONSE_PRINTED = False


def get_client() -> Anthropic:
    api_key = os.getenv(API_KEY_ENV)
    if not api_key:
        raise RuntimeError(f"{API_KEY_ENV} is not set in the environment")
    return Anthropic(api_key=api_key)


def load_reviews(limit: Optional[int] = None) -> pd.DataFrame:
    if not os.path.exists(INPUT_FILE):
        raise FileNotFoundError(f"Input file not found: {INPUT_FILE}")

    df = pd.read_excel(INPUT_FILE)
    if "text" not in df.columns:
        candidates = [c for c in df.columns if "review" in c.lower() or "text" in c.lower()]
        if not candidates:
            raise ValueError("No text column found in input file")
        df = df.rename(columns={candidates[0]: "text"})

    df = df[df["text"].notna() & (df["text"].astype(str).str.strip() != "")].copy()

    if limit is not None:
        df = df.head(limit)

    return df


def build_messages(texts: List[str]) -> tuple[str, List[dict]]:
    system_content = (
        "You are a JSON-only classifier. For each review in the user message, return a JSON array of objects."
        " Each object must have exactly two keys: category and sentiment."
        " category must be exactly one of: " + ", ".join(LABEL_CATEGORIES) + "."
        " sentiment must be exactly one of: Positive, Negative, Neutral."
        " Return ONLY valid JSON; do not include any markdown, code fences, explanations, or extra keys."
    )

    user_content = "Classify the following reviews into a JSON list with exactly one object per review.\n"
    user_content += "\n".join([f"- {t}" for t in texts])
    user_content += (
        f"\nReturn exactly {len(texts)} objects, one per review, in the same order as the input."
    )

    messages = [{"role": "user", "content": user_content}]
    return system_content, messages


def extract_response_text(resp: object) -> str:
    content = None
    if isinstance(resp, dict):
        content = resp.get("content")
    else:
        content = getattr(resp, "content", None)

    texts: List[str] = []
    if isinstance(content, list):
        for block in content:
            if isinstance(block, str):
                texts.append(block)
            elif isinstance(block, dict) and "text" in block:
                texts.append(block["text"])
            elif hasattr(block, "text"):
                texts.append(getattr(block, "text"))
    elif isinstance(content, str):
        texts.append(content)

    if not texts:
        return str(resp)

    return "\n".join([t for t in texts if isinstance(t, str)])


def strip_json(text: str) -> str:
    text = re.sub(r"```json\n", "", text, flags=re.IGNORECASE)
    text = re.sub(r"```", "", text)
    return text.strip()


def parse_json_list(text: str) -> list:
    text = strip_json(text)
    match = re.search(r"(\[\s*\{.*\}\s*\])", text, re.S)
    if match:
        text = match.group(1)
    return json.loads(text)


def map_category_and_sentiment(candidate_category: Optional[str], candidate_sentiment: Optional[str]) -> tuple[str, str]:
    category = "Unclassified"
    sentiment = "Unclassified"

    if isinstance(candidate_category, str):
        normalized = candidate_category.strip()
        if normalized in LABEL_CATEGORIES:
            category = normalized
        else:
            lower = normalized.lower()
            if "positive" in lower and "general" in lower:
                category = "General Positive"
            elif "negative" in lower and "general" in lower:
                category = "General Negative"
            elif "flavour" in lower or "flavor" in lower or "taste" in lower:
                category = "Flavour Variety"
            elif "quality" in lower or "product" in lower or "taste" in lower or "fresh" in lower:
                category = "Product Quality"
            elif "wait" in lower or "queue" in lower or "line" in lower or "delay" in lower or "slow" in lower:
                category = "Wait Time"
            elif "store" in lower or "environment" in lower or "space" in lower or "seating" in lower or "clean" in lower:
                category = "Store Environment"
            elif "price" in lower or "value" in lower or "cost" in lower or "expensive" in lower or "cheap" in lower:
                category = "Price & Value"
            elif "service" in lower or "staff" in lower or "customer" in lower or "attitude" in lower:
                category = "Service"
            elif "general" in lower and "neutral" in lower:
                category = "General Negative"
            else:
                category = "Unclassified"

        if category == "Unclassified":
            sentiment = "Unclassified"
        elif category == "General Positive":
            sentiment = "Positive"
        elif category == "General Negative":
            sentiment = "Negative"

        if sentiment == "Unclassified" and isinstance(candidate_sentiment, str):
            normalized_sentiment = candidate_sentiment.strip().capitalize()
            if normalized_sentiment in SENTIMENTS:
                sentiment = normalized_sentiment

        # Derive sentiment from ambiguous category terms if sentiment not set
        if sentiment == "Unclassified" and isinstance(candidate_category, str):
            lower = candidate_category.lower()
            if any(word in lower for word in ["neutral", "mixed", "meh", "average", "okay", "ok"]):
                sentiment = "Neutral"
            elif "positive" in lower:
                sentiment = "Positive"
            elif "negative" in lower:
                sentiment = "Negative"

    if sentiment == "Unclassified" and isinstance(candidate_sentiment, str):
        normalized_sentiment = candidate_sentiment.strip().capitalize()
        if normalized_sentiment in SENTIMENTS:
            sentiment = normalized_sentiment

    return category, sentiment


def call_claude(client: Anthropic, system_content: str, messages: List[dict]) -> object:
    try:
        return client.messages.create(
            model=MODEL,
            system=system_content,
            messages=messages,
            max_tokens=1500,
            temperature=0.0,
        )
    except Exception as exc:
        print("Anthropic API error:", exc, file=sys.stderr)
        raise


def classify_batch(client: Anthropic, texts: List[str]) -> List[dict]:
    global RAW_RESPONSE_PRINTED
    system_content, messages = build_messages(texts)
    response = call_claude(client, system_content, messages)
    raw_text = extract_response_text(response)

    if not RAW_RESPONSE_PRINTED:
        print("--- Raw API extracted response text ---")
        print(raw_text)
        print("--- End raw extracted response text ---")
        RAW_RESPONSE_PRINTED = True

    parsed = parse_json_list(raw_text)
    if not isinstance(parsed, list):
        raise ValueError("Expected a JSON list in the model response")

    if len(parsed) != len(texts):
        print(
            f"Warning: expected {len(texts)} classifications, got {len(parsed)} from the model. "
            "Truncating or padding to match input length.",
            file=sys.stderr,
        )

    if len(parsed) > len(texts):
        parsed = parsed[: len(texts)]
    elif len(parsed) < len(texts):
        parsed.extend([{}] * (len(texts) - len(parsed)))

    results: List[dict] = []
    warnings = []
    for idx, item in enumerate(parsed):
        category = "Unclassified"
        sentiment = "Unclassified"
        if isinstance(item, dict):
            candidate_category = item.get("category")
            candidate_sentiment = item.get("sentiment")
            category, sentiment = map_category_and_sentiment(candidate_category, candidate_sentiment)
            if category == "Unclassified":
                warnings.append(f"Invalid category at index {idx}: {candidate_category}")
            if sentiment == "Unclassified":
                warnings.append(f"Invalid sentiment at index {idx}: {candidate_sentiment}")
        else:
            warnings.append(f"Non-object item at index {idx}: {type(item)}")
        results.append({"category": category, "sentiment": sentiment})

    if warnings:
        for warning in warnings[:10]:
            print("Warning:", warning, file=sys.stderr)
        if len(warnings) > 10:
            print(f"Warning: {len(warnings)} total label warnings, showing first 10.", file=sys.stderr)

    return results


def process_reviews(client: Anthropic, df: pd.DataFrame, output_path: str) -> pd.DataFrame:
    texts = df["text"].astype(str).tolist()
    categories: List[str] = []
    sentiments: List[str] = []

    for i in range(0, len(texts), BATCH_SIZE):
        batch = texts[i : i + BATCH_SIZE]
        results = classify_batch(client, batch)
        for result in results:
            categories.append(result["category"])
            sentiments.append(result["sentiment"])

        processed = min(i + BATCH_SIZE, len(texts))
        if processed % PROGRESS_INTERVAL == 0 or processed == len(texts):
            print(f"Processed {processed}/{len(texts)} reviews")

    df["category"] = categories
    df["sentiment"] = sentiments
    df.to_excel(output_path, index=False)
    return df


def main() -> None:
    parser = argparse.ArgumentParser(description="Label review text with Anthropic Claude")
    parser.add_argument("--test", type=int, default=0, help="Test using the first N reviews only")
    args = parser.parse_args()

    if args.test > 0:
        print(f"Running in test mode with first {args.test} reviews")

    client = get_client()
    df = load_reviews(limit=args.test if args.test > 0 else None)
    print(f"Loaded {len(df)} reviews with text")

    if len(df) == 0:
        print("No reviews to process.")
        return

    output_path = TEST_OUTPUT_FILE if args.test > 0 else OUTPUT_FILE
    try:
        process_reviews(client, df, output_path)
    except Exception as exc:
        print("Failed to classify reviews:", exc, file=sys.stderr)
        sys.exit(1)

    print(f"Wrote labeled reviews to {output_path}")


if __name__ == "__main__":
    main()
