# Roadmap

## Near-term

- Keep README, notebook names, file manifest, and result files synchronized.
- Expand sample-data execution so the full public pipeline can run end-to-end without private files.
- Separate more notebook logic into reusable modules under `src/`.
- Add unit tests for preprocessing, graph construction, and rule validation.

## Model and evaluation

- Provide a public synthetic-data training example for GCN, GraphSAGE, R-GCN, GATv2, SGF-GAT, and E-SGF-GAT.
- Add clearer metric tables using `mean ± std` across seeds.
- Maintain auxiliary text baselines separately from graph-based model comparison.
- Add ablation studies for semantic-only, graph-only, and fusion-based scoring.

## Knowledge structure

- Expand ontology classes and properties for material, product, organization, issue, and process status.
- Add SHACL validation examples for graph consistency checks.
- Add SWRL-like rule descriptions for domain inference where applicable.
- Align prompt templates with ontology concepts.

## Deployment and reuse

- Add a small Streamlit or Gradio demo for relation recommendation.
- Add model card templates and release notes for public checkpoints or adapter weights.
- Provide an integration guide for private ERP/MES data owners.
- Add privacy review checklist for data and model artifact release.
