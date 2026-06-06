#!/usr/bin/env python3
"""Build public-format heterogeneous graph node and edge tables.

The generated graph is compatible with the repository schema and sample
recommendation script. It is not intended to replace the full research notebook
workflow; it provides a transparent public pipeline for GitHub users.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable

import pandas as pd

ENTITY_COLUMNS = {
    "part_no": "related_to_part_no",
    "part_desc": "related_to_part_desc",
    "product": "related_to_product",
    "org": "related_to_org",
    "cluster_id": "belongs_to_cluster",
    "source_domain": "from_source_domain",
    "message_type": "has_message_type",
    "date": "occurred_on_date",
}

NODE_TYPE_BY_COLUMN = {
    "cluster_id": "cluster",
    **{col: col for col in ENTITY_COLUMNS if col != "cluster_id"},
}


def safe_node_id(node_type: str, value: object) -> str:
    cleaned = "_".join(str(value).strip().split())
    cleaned = cleaned.replace("/", "_").replace("\\", "_")
    return f"{node_type}:{cleaned}"


def add_node(nodes: dict[str, dict[str, str]], node_id: str, node_type: str, node_name: str, source_value: str) -> None:
    nodes[node_id] = {
        "node_id": node_id,
        "node_type": node_type,
        "node_name": node_name,
        "source_value": source_value,
    }


def build_graph(messages: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    nodes: dict[str, dict[str, str]] = {}
    edges: list[dict[str, object]] = []

    for _, row in messages.iterrows():
        message_id = str(row["message_id"])
        message_node_id = safe_node_id("message", message_id)
        add_node(nodes, message_node_id, "message", message_id, row.get("message_text", ""))

        for column, edge_type in ENTITY_COLUMNS.items():
            value = row.get(column, "")
            if pd.isna(value) or str(value).strip() == "":
                continue

            node_type = NODE_TYPE_BY_COLUMN[column]
            node_id = safe_node_id(node_type, value)
            add_node(nodes, node_id, node_type, str(value), str(value))
            edges.append(
                {
                    "source": message_node_id,
                    "target": node_id,
                    "edge_type": edge_type,
                    "weight": 1.0,
                    "meta": "public_sample_pipeline",
                }
            )

    node_df = pd.DataFrame(nodes.values()).sort_values(["node_type", "node_id"]).reset_index(drop=True)
    edge_df = pd.DataFrame(edges).sort_values(["edge_type", "source", "target"]).reset_index(drop=True)
    return node_df, edge_df


def main() -> None:
    parser = argparse.ArgumentParser(description="Build public graph node and edge tables.")
    parser.add_argument("--messages", required=True, type=Path, help="Processed message CSV path")
    parser.add_argument("--nodes", required=True, type=Path, help="Output node CSV path")
    parser.add_argument("--edges", required=True, type=Path, help="Output edge CSV path")
    args = parser.parse_args()

    messages = pd.read_csv(args.messages)
    node_df, edge_df = build_graph(messages)

    args.nodes.parent.mkdir(parents=True, exist_ok=True)
    args.edges.parent.mkdir(parents=True, exist_ok=True)
    node_df.to_csv(args.nodes, index=False, encoding="utf-8-sig")
    edge_df.to_csv(args.edges, index=False, encoding="utf-8-sig")

    print(f"Wrote {len(node_df):,} nodes to {args.nodes}")
    print(f"Wrote {len(edge_df):,} edges to {args.edges}")


if __name__ == "__main__":
    main()
