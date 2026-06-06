# Open-source release plan

## Release goal

This repository is designed as a public GitHub package for explaining and extending a manufacturing material-intelligence prototype.

The public release focuses on reproducible structure, sample-data execution, and reusable documentation while excluding sensitive ERP/MES-derived raw data.

## Publicly released components

| Component | Release status | Description |
|---|---|---|
| Data preprocessing scripts | Included | `src/preprocess.py` normalizes public sample messages |
| Structured graph pipeline code | Included | `src/build_graph.py` converts message rows into node/edge tables |
| Prompt set | Included | `prompts/` contains cluster interpretation, recommendation explanation, and RAG templates |
| Sample data | Included | `data_sample/` contains small anonymized examples |
| Graph schema | Included | `artifacts/graph_schema/` explains node and edge structures |
| Ontology prototype | Included | `artifacts/ontology_prototype/` provides a reference knowledge-structure artifact |
| Result metrics | Included | `results/metrics/` contains public-format model comparison files |
| Recommendation sample | Included | `results/recommendations/` contains sample outputs |
| Documentation | Included | `docs/` includes overview, pipeline, tutorial, roadmap, and disclosure plans |
| License | Included | MIT License |

## License policy

The public source code and documentation are released under the MIT License to allow reuse, modification, and secondary development.

The license does not grant rights to private ERP/MES data, internal business reports, or proprietary artifacts that are not included in this repository.

## Public-release boundary

The following items are intentionally excluded from the public repository:

- raw ERP/MES spreadsheets
- full internal message logs
- full private graph tables
- sensitive enterprise identifiers
- proprietary reports
- full trained model weights when they may contain private operational patterns

## Expected use

This repository can be used to:

1. Understand the LLM-GNN hybrid pipeline.
2. Recreate the public sample-data workflow.
3. Adapt the graph schema to other manufacturing domains.
4. Extend prompt templates and ontology rules.
5. Re-run graph-based link prediction experiments with private or synthetic data.
