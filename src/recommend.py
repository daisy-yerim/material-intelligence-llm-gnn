#!/usr/bin/env python3
"""Generate lightweight public recommendations from graph edges.

This script is a sample-data-compatible demonstration. The full GNN-based
recommendation experiment is documented in the notebooks and metrics files.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

RELATION_TO_TYPE = {
    "related_to_part_no": "Material",
    "related_to_part_desc": "Material description",
    "related_to_product": "Product",
    "related_to_org": "Organization",
    "belongs_to_cluster": "Issue cluster",
    "next_message_in_domain": "Similar issue",
}


def normalize_message_node(message_id: str) -> str:
    return f"message:{message_id}"


def direct_graph_recommendations(edges: pd.DataFrame, message_node: str) -> list[dict[str, object]]:
    recs: list[dict[str, object]] = []
    subset = edges[edges["source"].eq(message_node)].copy()
    for _, row in subset.iterrows():
        relation = row["edge_type"]
        recs.append(
            {
                "recommended_type": RELATION_TO_TYPE.get(relation, relation),
                "recommended_value": str(row["target"]).split(":", 1)[-1],
                "relation_type": relation,
                "score": float(row.get("weight", 1.0)),
                "evidence": "direct_graph_edge",
            }
        )
    return recs


def similar_message_recommendations(messages: pd.DataFrame, message_id: str, top_k: int = 3) -> list[dict[str, object]]:
    if len(messages) <= 1:
        return []

    if message_id not in set(messages["message_id"].astype(str)):
        return []

    texts = messages["message_text"].fillna("").astype(str).tolist()
    ids = messages["message_id"].astype(str).tolist()
    idx = ids.index(message_id)

    matrix = TfidfVectorizer().fit_transform(texts)
    sims = cosine_similarity(matrix[idx], matrix).ravel()

    candidates = []
    for j, score in sorted(enumerate(sims), key=lambda x: x[1], reverse=True):
        if j == idx:
            continue
        candidates.append(
            {
                "recommended_type": "Similar issue",
                "recommended_value": ids[j],
                "relation_type": "next_message_in_domain",
                "score": float(score),
                "evidence": "tfidf_text_similarity_public_demo",
            }
        )
        if len(candidates) >= top_k:
            break
    return candidates


def recommend(messages: pd.DataFrame, nodes: pd.DataFrame, edges: pd.DataFrame, message_id: str) -> pd.DataFrame:
    message_node = normalize_message_node(message_id)
    input_rows = messages[messages["message_id"].astype(str).eq(message_id)]
    if input_rows.empty:
        raise ValueError(f"message_id not found: {message_id}")

    input_message = input_rows.iloc[0]["message_text"]
    recs = direct_graph_recommendations(edges, message_node)
    recs.extend(similar_message_recommendations(messages, message_id))

    output = []
    for rec in recs:
        output.append(
            {
                "message_id": message_id,
                "input_message": input_message,
                **rec,
            }
        )
    return pd.DataFrame(output).sort_values("score", ascending=False).reset_index(drop=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate sample graph recommendations.")
    parser.add_argument("--messages", required=True, type=Path, help="Processed message CSV path")
    parser.add_argument("--nodes", required=True, type=Path, help="Node CSV path")
    parser.add_argument("--edges", required=True, type=Path, help="Edge CSV path")
    parser.add_argument("--message-id", required=True, help="Input message ID, e.g. M001")
    parser.add_argument("--output", required=True, type=Path, help="Recommendation output CSV path")
    args = parser.parse_args()

    messages = pd.read_csv(args.messages)
    nodes = pd.read_csv(args.nodes)
    edges = pd.read_csv(args.edges)

    rec_df = recommend(messages, nodes, edges, args.message_id)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    rec_df.to_csv(args.output, index=False, encoding="utf-8-sig")
    print(f"Wrote {len(rec_df):,} recommendations to {args.output}")


if __name__ == "__main__":
    main()
