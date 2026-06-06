# Model release plan

## Disclosure level

This project follows a limited model disclosure strategy due to the use of enterprise ERP/MES-derived operational data.

The public repository discloses model architecture, prompt templates, graph schema, sample data, metrics, and lightweight demonstration scripts. It does not include raw private data or full trained weights that may encode sensitive operational patterns.

## Released model-related assets

| Asset | Status | Notes |
|---|---|---|
| Graph-based model comparison results | Included | Results are provided in `results/metrics/` |
| GNN experimental workflow | Included | Main experimental workflow is in `notebooks/4_gnn_semantic_graph_fusion_gat.ipynb` |
| Public graph-building logic | Included | `src/build_graph.py` provides sample-data-compatible graph construction |
| Public recommendation logic | Included | `src/recommend.py` provides a lightweight recommendation demo |
| Prompt templates | Included | `prompts/` provides reusable templates |
| Ontology/rule artifacts | Included | Ontology prototype and domain validation rules are included |
| Full private training data | Not included | Excluded for data protection |
| Full trained private model weights | Not included | Excluded unless separately cleared for release |

## LLM and embedding components

The public prototype is structured around semantic message embeddings and LLM-assisted cluster interpretation. The current public description is model-provider neutral and can support different LLM backends if configured by the user.

The repository does not redistribute third-party foundation model weights. Users should follow the license terms of any embedding model or LLM backend they use.

## Adapter-only release option

If fine-tuned LLM components are added later, the recommended release strategy is to disclose lightweight adapter artifacts, such as LoRA adapter weights, instead of full model parameters. This supports reproducibility and extension while reducing the risk of exposing private data patterns.

## GNN checkpoint release option

If GNN checkpoints are released later, they should be trained only on public synthetic or fully anonymized graph data, or be cleared through internal privacy review.

Recommended checkpoint directory:

```text
checkpoints/public_demo/
├── model_config.json
├── model_state_dict.pt
├── node_type_mapping.json
├── edge_type_mapping.json
└── README.md
```

Checkpoints trained on private operational graph data should not be uploaded to the public repository by default.
