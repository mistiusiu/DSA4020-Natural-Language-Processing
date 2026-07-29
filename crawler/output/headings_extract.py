import json
import pandas as pd

INPUT_FILE = "ranked.json"
OUTPUT_FILE = "headings.csv"


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        text = f.read().strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return [json.loads(line) for line in text.splitlines() if line.strip()]


records = load_json(INPUT_FILE)

seen = set()
rows = []

for item in records:
    score = item.get("score", 0)

    for field in [
        "heading",
        "previous_heading",
        "following_text",
        "next_heading",
    ]:
        value = item.get(field, "").strip()

        if value and value not in seen:
            seen.add(value)
            rows.append({
                "score": score,
                "text": value
            })

df = pd.DataFrame(rows)
df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")

print(f"Saved {len(df)} unique rows to {OUTPUT_FILE}")
