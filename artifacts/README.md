# Artifacts

This folder contains public-facing artifacts that help explain and reproduce the workflow.

## Contents

* `cluster_interpretation/`: interpreted issue clusters
* `graph_schema/`: node and edge schema for graph construction
* `ontology_prototype/`: ontology and SHACL-style knowledge-structure examples
* `model_weights/`: released PyTorch checkpoints for the trained GNN link-prediction model

## Released Model Weights

The released model weights are provided as PyTorch checkpoint files under:

```text
artifacts/model_weights/
```

The checkpoint files contain trained parameters under:

```python
checkpoint["model_state_dict"]
```

Recommended released checkpoint:

```text
artifacts/model_weights/enhanced_semantic_graph_fusion_gat_seed44_link_predictor.pt
```

The non-seed filename may be provided as a final-model alias:

```text
artifacts/model_weights/enhanced_semantic_graph_fusion_gat_link_predictor.pt
```

To use these weights, the corresponding model architecture code in `src/` is required.

## Excluded Files

Large raw processed tables are not included in this public release.
