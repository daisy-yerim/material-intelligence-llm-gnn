# Model card: E-SGF-GAT

## Model name

Enhanced Semantic Graph Fusion Graph Attention Network, abbreviated as E-SGF-GAT.

## Intended use

The model is designed for link prediction in a heterogeneous material-intelligence graph. It predicts likely relations between material-management messages and candidate nodes such as part numbers, products, organizations, clusters, and similar historical issues.

## Input

- message node representation
- candidate node representation
- semantic message embeddings
- heterogeneous graph edges
- relation type information

## Output

A relation likelihood score for a message-candidate pair.

## Compared models

The model is compared against GCN, GraphSAGE, R-GCN, GATv2, RA-GAT, and SGF-GAT.

## Reported public result

Among graph-based models, E-SGF-GAT achieved the best overall public test result in the included metric table.

| Metric | Value |
|---|---:|
| AUC | 0.9457 |
| AP | 0.9523 |
| MRR | 0.6627 |
| Hits@1 | 0.5476 |
| Hits@3 | 0.7397 |
| Hits@5 | 0.8041 |
| Hits@10 | 0.8667 |

## Limitations

- The public repository does not include private ERP/MES training data.
- Public sample data is intentionally small and synthetic.
- Full trained private weights are not released by default.
- Text-only retrieval baselines are reported separately and should not be interpreted as graph-based prediction models.

## Disclosure note

If model weights are released later, they should be trained on public or fully anonymized data, or cleared through privacy review.
