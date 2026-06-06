# Result summary

## Graph-based model comparison

The following table summarizes test split performance for the graph-based link prediction models.

`E-SGF-GAT` achieved the best overall performance **among the compared graph-based models**, with MRR 0.6627, AUC 0.9457, and AP 0.9523.

| Model | AUC | AP | MRR | Hits@1 | Hits@3 | Hits@5 | Hits@10 |
|---|---:|---:|---:|---:|---:|---:|---:|
| E-SGF-GAT | 0.9457 | 0.9523 | 0.6627 | 0.5476 | 0.7397 | 0.8041 | 0.8667 |
| SGF-GAT | 0.9275 | 0.9385 | 0.6351 | 0.5246 | 0.7065 | 0.7655 | 0.8347 |
| GATv2 | 0.9263 | 0.9396 | 0.6208 | 0.5036 | 0.6929 | 0.7611 | 0.8375 |
| RA-GAT | 0.9217 | 0.9380 | 0.6185 | 0.4948 | 0.7047 | 0.7685 | 0.8385 |
| R-GCN | 0.9254 | 0.9314 | 0.5648 | 0.4298 | 0.6467 | 0.7251 | 0.8077 |
| GraphSAGE | 0.8840 | 0.8988 | 0.4790 | 0.3281 | 0.5650 | 0.6551 | 0.7753 |
| GCN | 0.8967 | 0.9019 | 0.4581 | 0.2977 | 0.5400 | 0.6549 | 0.7865 |

## Auxiliary retrieval baselines

Text-only similarity methods such as TF-IDF are reported as auxiliary retrieval baselines. They are useful reference methods for simple text search, but they are not graph-based prediction models and are therefore separated from the main model comparison.

This distinction is important because the objective of the proposed models is not only to retrieve textually similar messages, but also to predict operational relations among messages, materials, products, organizations, and historical issues.

## Interpretation

The result suggests that incorporating semantic message representations and heterogeneous graph structure can improve link prediction among operational entities. In particular, E-SGF-GAT improves over SGF-GAT by using an enhanced fusion strategy for combining semantic and graph-level signals.

## Recommendation output

The recommendation output represents likely relations between an input message and candidate nodes.

| Input message | Recommended type | Recommended value | Relation |
|---|---|---|---|
| Excess PO may increase inventory | Material | PART_001 | `related_to_part_no` |
| Procurement delay may affect production | Similar issue | M004 | `next_message_in_domain` |

A higher score means the model assigns a higher likelihood to that relation.

## Included public sample

`results/recommendations/sample_recommendations.csv` provides a small synthetic example of the expected output format.
