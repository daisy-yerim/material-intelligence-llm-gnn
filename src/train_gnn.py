#!/usr/bin/env python3
"""Lightweight public entry point for graph experiment inspection.

The full GNN experiments are implemented in
`notebooks/4_gnn_semantic_graph_fusion_gat.ipynb`. This script provides a
sample-data-compatible command-line entry point that summarizes graph size and
prepares a simple train/validation/test edge split manifest.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def split_edges(edges: pd.DataFrame, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    out = edges.copy().reset_index(drop=True)
    order = rng.permutation(len(out))
    n = len(out)
    train_end = int(n * 0.7)
    valid_end = int(n * 0.85)

    split = np.array(["train"] * n, dtype=object)
    split[order[train_end:valid_end]] = "valid"
    split[order[valid_end:]] = "test"
    out["split"] = split
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare a public graph experiment manifest.")
    parser.add_argument("--nodes", required=True, type=Path, help="Node CSV path")
    parser.add_argument("--edges", required=True, type=Path, help="Edge CSV path")
    parser.add_argument("--output", required=True, type=Path, help="Output split manifest CSV path")
    parser.add_argument("--seed", default=42, type=int, help="Random seed")
    args = parser.parse_args()

    nodes = pd.read_csv(args.nodes)
    edges = pd.read_csv(args.edges)
    split_df = split_edges(edges, args.seed)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    split_df.to_csv(args.output, index=False, encoding="utf-8-sig")

    print("Graph experiment manifest prepared.")
    print(f"Nodes: {len(nodes):,}")
    print(f"Edges: {len(edges):,}")
    print(split_df["split"].value_counts().to_string())
    print(f"Wrote split manifest to {args.output}")


if __name__ == "__main__":
    main()
