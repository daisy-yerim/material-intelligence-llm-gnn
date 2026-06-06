# Model overview

## Purpose

This project builds a relation prediction model for manufacturing material-management messages.

Instead of assigning only one class label to a message, the model predicts related entities and issues:

- related material number
- related material description
- related product
- related organization
- similar past issue

## Input representation

The graph contains several node types.

| Node type | Example meaning |
|---|---|
| `message` | Material-management message |
| `part_no` | Material or component identifier |
| `part_desc` | Material description |
| `product` | Product group |
| `org` | Organization, site, or operating unit |
| `cluster` | Semantic issue cluster |
| `source_domain` | Data source category |
| `message_type` | Message type |
| `date` | Event date |

Edges describe relationships between these nodes.

| Edge type | Meaning |
|---|---|
| `related_to_part_no` | Message is related to a material number |
| `related_to_part_desc` | Message is related to a material description |
| `related_to_product` | Message is related to a product |
| `related_to_org` | Message is related to an organization |
| `belongs_to_cluster` | Message belongs to a semantic issue cluster |
| `next_message_in_domain` | Message is sequentially or semantically related to another issue in the same domain |

## Semantic Graph Fusion GAT

The model uses two perspectives.

### 1. Semantic perspective

The semantic branch checks whether the message and candidate are similar in meaning.

Example:

```text
"Excess PO may increase inventory"
"Order quantity is high compared with demand"
```

These messages may be semantically close even if the wording is different.

### 2. Graph perspective

The graph branch checks whether two nodes are likely to be connected based on graph structure.

Example:

```text
message → material
message → product
message → organization
message → cluster
```

### 3. Fusion layer

The fusion layer combines semantic and graph scores.

It learns when to rely more on text meaning and when to rely more on graph structure. For example, a similar-issue relation may rely more on semantic similarity, while a material-number relation may rely more on graph structure.

## Compared graph-based models

The experiment compares several graph-based models.

- GCN
- GraphSAGE
- R-GCN
- GATv2
- Relation-aware GAT
- SGF-GAT
- E-SGF-GAT

## Auxiliary baselines

TF-IDF text similarity and other text-only retrieval methods are treated as auxiliary baselines. They are not included in the graph-based model ranking because they do not learn heterogeneous message-material-product-organization relations.

## Performance summary

Among the graph-based models, `E-SGF-GAT` achieved the best overall performance with MRR 0.6627, AUC 0.9457, and AP 0.9523.

| Model | AUC | AP | MRR | Hits@1 | Hits@3 | Hits@5 | Hits@10 |
|---|---:|---:|---:|---:|---:|---:|---:|
| E-SGF-GAT | 0.9457 | 0.9523 | 0.6627 | 0.5476 | 0.7397 | 0.8041 | 0.8667 |
| SGF-GAT | 0.9275 | 0.9385 | 0.6351 | 0.5246 | 0.7065 | 0.7655 | 0.8347 |
| GATv2 | 0.9263 | 0.9396 | 0.6208 | 0.5036 | 0.6929 | 0.7611 | 0.8375 |
| RA-GAT | 0.9217 | 0.9380 | 0.6185 | 0.4948 | 0.7047 | 0.7685 | 0.8385 |
| R-GCN | 0.9254 | 0.9314 | 0.5648 | 0.4298 | 0.6467 | 0.7251 | 0.8077 |
| GraphSAGE | 0.8840 | 0.8988 | 0.4790 | 0.3281 | 0.5650 | 0.6551 | 0.7753 |
| GCN | 0.8967 | 0.9019 | 0.4581 | 0.2977 | 0.5400 | 0.6549 | 0.7865 |
