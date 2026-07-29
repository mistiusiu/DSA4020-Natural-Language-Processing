import argparse

from utils import (
    load_jsonl,
    save_json,
    save_csv,
    sort_by_score
)


def rank_headings(
    input_file: str,
    json_output: str,
    csv_output: str
):
    """
    Main ranking pipeline.
    """

    records = load_jsonl(input_file)

    ranked_records = sort_by_score(
        records,
        descending=True
    )

    save_json(
        ranked_records,
        json_output
    )

    save_csv(
        ranked_records,
        csv_output
    )

    print(
        f"Processed {len(ranked_records)} records"
    )

    print(
        f"JSON saved: {json_output}"
    )

    print(
        f"CSV saved: {csv_output}"
    )


def main():

    parser = argparse.ArgumentParser(
        description=(
            "Rank extracted headings by relevance score "
            "and export JSON/CSV"
        )
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Input JSONL file"
    )

    parser.add_argument(
        "--json",
        default="ranked_headings.json",
        help="JSON output file"
    )

    parser.add_argument(
        "--csv",
        default="ranked_headings.csv",
        help="CSV output file"
    )

    args = parser.parse_args()

    rank_headings(
        input_file=args.input,
        json_output=args.json,
        csv_output=args.csv
    )


if __name__ == "__main__":
    main()
