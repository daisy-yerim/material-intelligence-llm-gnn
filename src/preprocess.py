#!/usr/bin/env python3
"""Preprocess public sample material-management messages.

This script is intentionally lightweight. It validates required columns,
normalizes empty values, and writes a public-format CSV that can be used by
`src/build_graph.py`.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

REQUIRED_COLUMNS = [
    "message_id",
    "message_text",
    "source_domain",
    "message_type",
    "part_no",
    "part_desc",
    "product",
    "org",
    "date",
    "cluster_id",
]


def validate_columns(df: pd.DataFrame) -> None:
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")


def clean_text(value: object) -> str:
    if pd.isna(value):
        return ""
    return " ".join(str(value).strip().split())


def preprocess(input_path: Path, output_path: Path) -> pd.DataFrame:
    df = pd.read_csv(input_path)
    validate_columns(df)

    for col in REQUIRED_COLUMNS:
        df[col] = df[col].map(clean_text)

    df = df[df["message_id"].ne("") & df["message_text"].ne("")].copy()
    df = df.drop_duplicates(subset=["message_id"]).reset_index(drop=True)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False, encoding="utf-8-sig")
    return df


def main() -> None:
    parser = argparse.ArgumentParser(description="Preprocess public sample messages.")
    parser.add_argument("--input", required=True, type=Path, help="Input message CSV path")
    parser.add_argument("--output", required=True, type=Path, help="Output processed CSV path")
    args = parser.parse_args()

    df = preprocess(args.input, args.output)
    print(f"Wrote {len(df):,} processed rows to {args.output}")


if __name__ == "__main__":
    main()
