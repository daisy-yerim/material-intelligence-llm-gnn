# Domain rule set

This document summarizes the lightweight domain rules used in the public sample pipeline.

## Rule categories

| Rule category | Purpose |
|---|---|
| Required field validation | Ensure message rows contain key identifiers and text |
| Entity consistency | Ensure graph edges reference valid source and target nodes |
| Relation typing | Ensure each edge type maps to an expected source and target node type |
| Public disclosure filtering | Ensure raw private fields are not included in public sample outputs |

## Relation type rules

| Edge type | Source node type | Target node type |
|---|---|---|
| `related_to_part_no` | `message` | `part_no` |
| `related_to_part_desc` | `message` | `part_desc` |
| `related_to_product` | `message` | `product` |
| `related_to_org` | `message` | `org` |
| `belongs_to_cluster` | `message` | `cluster` |
| `next_message_in_domain` | `message` | `message` |

A machine-readable version is provided in `config/domain_rules.yaml`.
