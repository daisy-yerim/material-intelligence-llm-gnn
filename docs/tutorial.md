# Tutorial: run the public sample pipeline

This tutorial runs a lightweight version of the pipeline using the anonymized sample data in `data_sample/`.

## 1. Install dependencies

```bash
pip install -r requirements.txt
```

If `torch-geometric` fails to install, follow the wheel installation guide for your PyTorch and CUDA environment. The public sample scripts do not require GPU execution.

## 2. Preprocess sample messages

```bash
mkdir -p outputs
python src/preprocess.py   --input data_sample/sample_messages.csv   --output outputs/processed_messages.csv
```

This validates required columns and normalizes text fields.

## 3. Build graph tables

```bash
python src/build_graph.py   --messages outputs/processed_messages.csv   --nodes outputs/graph_nodes.csv   --edges outputs/graph_edges.csv
```

The script creates public-format node and edge tables.

## 4. Validate domain rules

```bash
python src/validate_rules.py   --messages outputs/processed_messages.csv   --rules config/domain_rules.yaml
```

The rule validator checks minimal schema and domain consistency constraints for the public sample.

## 5. Generate a sample recommendation

```bash
python src/recommend.py   --messages outputs/processed_messages.csv   --nodes outputs/graph_nodes.csv   --edges outputs/graph_edges.csv   --message-id M001   --output outputs/recommendations.csv
```

This generates a lightweight public recommendation example. The full GNN experiments are documented in the notebooks.

## 6. Run research notebooks

Run the notebooks in order:

```text
1. notebooks/1_embedding.ipynb
2. notebooks/2_clustering.ipynb
3. notebooks/3_cluster_interpretation_llm_semantic.ipynb
4. notebooks/4_gnn_semantic_graph_fusion_gat.ipynb
```

The notebooks are intended for experiment tracking and explanation. Some cells may require private data paths if you reproduce the original enterprise-data experiment.
