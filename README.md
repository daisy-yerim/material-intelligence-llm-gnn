# Material Intelligence with LLM-assisted Semantic Clustering and Heterogeneous GNN Link Prediction

A public-facing research prototype for **semantic relation prediction in manufacturing ERP/MES material-management messages**.

This project converts operational material-management messages into semantic embeddings, groups them into issue clusters, interprets the clusters with an LLM, constructs a heterogeneous graph, and performs graph-based link prediction to recommend related materials, products, organizations, and similar historical issues.

## Project summary

```text
Material-management messages
        ↓
Semantic embedding
        ↓
Issue clustering
        ↓
LLM-assisted cluster interpretation
        ↓
Heterogeneous graph construction
        ↓
Graph-based link prediction
        ↓
Related material / product / organization / similar issue recommendation
```

The goal is not simple message classification. The system predicts likely relations such as:

- `message → related_to_part_no → part_no`
- `message → related_to_product → product`
- `message → related_to_org → org`
- `message → next_message_in_domain → similar message`

## Key idea

The proposed framework combines two signals.

| Signal | Meaning |
|---|---|
| Semantic signal | Whether messages or entities are close in meaning |
| Graph signal | Whether nodes are likely to be connected in the heterogeneous graph |

The Semantic Graph Fusion models learn how to combine text-level semantic similarity and graph-level connectivity depending on the relation type.

## Repository structure

```text
.
├── notebooks/
│   ├── 1_embedding.ipynb
│   ├── 2_clustering.ipynb
│   ├── 3_cluster_interpretation_llm_semantic.ipynb
│   └── 4_gnn_semantic_graph_fusion_gat.ipynb
├── src/
│   ├── preprocess.py
│   ├── build_graph.py
│   ├── train_gnn.py
│   ├── recommend.py
│   └── validate_rules.py
├── prompts/
│   ├── cluster_interpretation_prompt.md
│   ├── recommendation_explanation_prompt.md
│   └── rag_relation_recommendation_template.md
├── config/
│   └── domain_rules.yaml
├── data_sample/
│   ├── sample_messages.csv
│   ├── sample_graph_nodes.csv
│   └── sample_graph_edges.csv
├── artifacts/
│   ├── cluster_interpretation/
│   ├── graph_schema/
│   └── ontology_prototype/
├── results/
│   ├── metrics/
│   └── recommendations/
├── docs/
├── model_cards/
├── ontology/
└── insight_engine/
```

## Notebooks

| Notebook | Description |
|---|---|
| `1_embedding.ipynb` | Builds semantic embeddings for material-management messages |
| `2_clustering.ipynb` | Groups messages into semantic issue clusters |
| `3_cluster_interpretation_llm_semantic.ipynb` | Interprets clusters with an LLM and prepares graph-ready outputs |
| `4_gnn_semantic_graph_fusion_gat.ipynb` | Trains and evaluates graph-based link prediction models |

## Public scripts

The `src/` folder provides lightweight, sample-data-compatible scripts so that external users can inspect the pipeline structure without access to private ERP/MES data.

```bash
python src/preprocess.py \
  --input data_sample/sample_messages.csv \
  --output outputs/processed_messages.csv

python src/build_graph.py \
  --messages outputs/processed_messages.csv \
  --nodes outputs/graph_nodes.csv \
  --edges outputs/graph_edges.csv

python src/validate_rules.py \
  --messages outputs/processed_messages.csv \
  --rules config/domain_rules.yaml

python src/recommend.py \
  --messages outputs/processed_messages.csv \
  --nodes outputs/graph_nodes.csv \
  --edges outputs/graph_edges.csv \
  --message-id M001 \
  --output outputs/recommendations.csv
```

The full experimental workflow remains in the notebooks because the original project was developed as a research prototype.

## Models

The graph-based models compared in this repository include:

- GCN
- GraphSAGE
- R-GCN
- GATv2
- Relation-aware GAT
- SGF-GAT
- E-SGF-GAT

Among the **graph-based models**, `E-SGF-GAT` achieved the best overall performance across the reported link prediction metrics.

TF-IDF text similarity is reported separately as an **auxiliary retrieval baseline**. It is not treated as a graph-based prediction model.

## Results

| Model | AUC | AP | MRR | Hits@1 | Hits@3 | Hits@5 | Hits@10 |
|---|---:|---:|---:|---:|---:|---:|---:|
| E-SGF-GAT | 0.9457 | 0.9523 | 0.6627 | 0.5476 | 0.7397 | 0.8041 | 0.8667 |
| SGF-GAT | 0.9275 | 0.9385 | 0.6351 | 0.5246 | 0.7065 | 0.7655 | 0.8347 |
| GATv2 | 0.9263 | 0.9396 | 0.6208 | 0.5036 | 0.6929 | 0.7611 | 0.8375 |
| RA-GAT | 0.9217 | 0.9380 | 0.6185 | 0.4948 | 0.7047 | 0.7685 | 0.8385 |
| R-GCN | 0.9254 | 0.9314 | 0.5648 | 0.4298 | 0.6467 | 0.7251 | 0.8077 |
| GraphSAGE | 0.8840 | 0.8988 | 0.4790 | 0.3281 | 0.5650 | 0.6551 | 0.7753 |
| GCN | 0.8967 | 0.9019 | 0.4581 | 0.2977 | 0.5400 | 0.6549 | 0.7865 |

See `docs/result_summary.md` and `results/metrics/` for detailed files.

## Open-source and disclosure policy

This repository follows a limited public disclosure strategy because the original experiments use enterprise ERP/MES-derived operational data.

Publicly included:

- Notebook workflow
- Sample anonymized data
- Data preprocessing and graph-building scripts
- Prompt templates
- Graph schema
- Ontology prototype
- Public-format model metrics
- Public-format recommendation examples
- Documentation, tutorial, and roadmap

Not publicly included:

- Raw ERP/MES files
- Full operational message logs
- Full private graph tables
- Proprietary business reports
- Full trained model weights containing private operational patterns

When lightweight fine-tuning artifacts such as LoRA adapters are applicable, they can be released separately from the full model parameters. See `docs/model_release_plan.md`.

## Installation

```bash
pip install -r requirements.txt
```

For PyTorch Geometric, install a wheel compatible with your local PyTorch and CUDA environment if needed.

## Quick start with sample data

```bash
mkdir -p outputs
python src/preprocess.py --input data_sample/sample_messages.csv --output outputs/processed_messages.csv
python src/build_graph.py --messages outputs/processed_messages.csv --nodes outputs/graph_nodes.csv --edges outputs/graph_edges.csv
python src/validate_rules.py --messages outputs/processed_messages.csv --rules config/domain_rules.yaml
python src/recommend.py --messages outputs/processed_messages.csv --nodes outputs/graph_nodes.csv --edges outputs/graph_edges.csv --message-id M001 --output outputs/recommendations.csv
```

## Documentation

- `docs/model_overview.md`: model and graph design
- `docs/pipeline.md`: end-to-end pipeline
- `docs/result_summary.md`: model comparison and output interpretation
- `docs/data_and_privacy.md`: data disclosure policy
- `docs/open_source_plan.md`: GitHub release plan
- `docs/model_release_plan.md`: model and weight disclosure plan
- `docs/tutorial.md`: sample-data tutorial
- `docs/roadmap.md`: future extension roadmap

## License

This project is released under the MIT License. See `LICENSE`.
