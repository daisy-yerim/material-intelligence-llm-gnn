# Data and privacy notes

This public repository is organized to show the method and repository structure without exposing raw operational data.

## Included

- Notebook workflow
- Small synthetic sample data
- Lightweight public scripts for preprocessing, graph construction, validation, and recommendation
- Prompt templates
- Graph schema files
- Cluster interpretation summary
- Ontology prototype
- Model metric files
- Public-format recommendation sample

## Not included

- Raw ERP/MES files
- Full operational message logs
- Full graph node and edge tables containing original values
- Full recommendation outputs containing original message text
- Internal reports or proposal documents
- Full trained weights that may encode sensitive operational patterns

## Recommended public-release practice

Keep raw data and sensitive processed files in a private storage location. Use synthetic or anonymized data for public examples.

If model weights are released later, prefer a limited disclosure strategy such as adapter-only or checkpoint-without-private-embedding release, depending on legal and organizational review.
