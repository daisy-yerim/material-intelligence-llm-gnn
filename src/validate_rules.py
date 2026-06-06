#!/usr/bin/env python3
"""Validate public sample files against lightweight domain rules."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
import yaml


def load_rules(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def validate_messages(messages: pd.DataFrame, rules: dict) -> list[str]:
    errors: list[str] = []
    required = rules.get("required_message_columns", [])
    missing = [col for col in required if col not in messages.columns]
    if missing:
        errors.append(f"Missing required message columns: {missing}")

    if "message_id" in messages.columns and messages["message_id"].duplicated().any():
        errors.append("message_id contains duplicate values")

    if "message_text" in messages.columns and messages["message_text"].fillna("").str.strip().eq("").any():
        errors.append("message_text contains empty values")

    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate sample message file against domain rules.")
    parser.add_argument("--messages", required=True, type=Path, help="Message CSV path")
    parser.add_argument("--rules", required=True, type=Path, help="YAML rule file path")
    args = parser.parse_args()

    messages = pd.read_csv(args.messages)
    rules = load_rules(args.rules)
    errors = validate_messages(messages, rules)

    if errors:
        print("Validation failed:")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)

    print("Validation passed.")


if __name__ == "__main__":
    main()
