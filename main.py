import pandas as pd
import json
from skill_runner import run_skill

def load_store_data(filepath: str, store_name: str) -> str:
    df = pd.read_excel(filepath, sheet_name="Reviews")
    store_df = df[df["Store Short Name"] == store_name]
    return store_df.to_csv(index=False, sep="\t")

def extract_json(text: str) -> str:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[1]
        cleaned = cleaned.rsplit("```", 1)[0].strip()
        return cleaned
    # Find whichever container character appears first
    obj_start = text.find('{')
    arr_start = text.find('[')
    if arr_start != -1 and (obj_start == -1 or arr_start < obj_start):
        end = text.rfind(']')
        if end > arr_start:
            return text[arr_start:end + 1]
    if obj_start != -1:
        end = text.rfind('}')
        if end > obj_start:
            return text[obj_start:end + 1]
    return cleaned

def run_pipeline(store_name: str):
    print(f"\n🔍 Analysing: {store_name}\n")

    print("Step 1/3 — Parsing data...")
    raw_data = load_store_data("Messina_PowerBI_Data.xlsx", store_name)
    parsed_json = run_skill("parse_reviews", raw_data)

    print("Step 2/3 — Calculating stats...")
    reviews = json.loads(extract_json(parsed_json))
    store_reviews = reviews

    total = len(store_reviews)
    if total == 0:
        print(f"No data found for {store_name}")
        return

    pos = sum(1 for r in store_reviews if r["sentiment"] == "Positive")
    neg = sum(1 for r in store_reviews if r["sentiment"] == "Negative")
    avg_rating = sum(r["rating"] for r in store_reviews) / total
    neg_reviews = [r for r in store_reviews if r["sentiment"] == "Negative"]
    categories = [r["category"] for r in neg_reviews]
    top_neg_cat = max(set(categories), key=categories.count) if categories else "N/A"

    stats = {
        "scope": "store",
        "name": store_name,
        "avg_rating": round(avg_rating, 2),
        "total_reviews": total,
        "positive_rate": round(pos / total, 3),
        "negative_rate": round(neg / total, 3),
        "top_negative_category": top_neg_cat,
        "period": "2023-2026"
    }
    print(f"Stats: {stats}\n")

    print("Step 2.5/3 — Detecting anomalies...")
    timeseries = [
        {"date": r["date"], "sentiment": r["sentiment"], "category": r["category"]}
        for r in store_reviews
    ]
    anomaly_json = run_skill("detect_anomaly", json.dumps(timeseries, ensure_ascii=False))
    anomaly = json.loads(extract_json(anomaly_json))
    print(f"Anomaly report: {json.dumps(anomaly, indent=2)}\n")

    print("Step 3/3 — Generating insight...")
    insight_input = {
        "stats": stats,
        "anomaly": anomaly
    }
    insight = run_skill("write_insight", json.dumps(insight_input, ensure_ascii=False))

    print("\n" + "="*50)
    print(f"📊 {store_name} Insight:")
    print("="*50)
    print(insight)
    print("="*50)

if __name__ == "__main__":
    run_pipeline("Parramatta")
