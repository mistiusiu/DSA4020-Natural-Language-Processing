from pathlib import Path
import math
import pandas as pd

INPUT_FILE = "headings.csv"
OUTPUT_DIR = "split_csv"
NUM_PARTS = 5

# Read the CSV
df = pd.read_csv(INPUT_FILE)

# Create output directory
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

# Calculate chunk size
chunk_size = math.ceil(len(df) / NUM_PARTS)

# Write each chunk
for i in range(NUM_PARTS):
    start = i * chunk_size
    end = min((i + 1) * chunk_size, len(df))
    chunk = df.iloc[start:end]

    if not chunk.empty:
        output_file = Path(OUTPUT_DIR) / f"headings_part_{i+1}.csv"
        chunk.to_csv(output_file, index=False, encoding="utf-8")
        print(f"Saved {output_file} ({len(chunk)} rows)")

print("Done.")
