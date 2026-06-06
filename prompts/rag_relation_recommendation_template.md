# RAG relation recommendation template

## Purpose

Use retrieved context to explain or validate relation recommendations produced by the graph-based model.

## Template

```text
You are analyzing relation recommendations in a manufacturing material-intelligence graph.

Use only the retrieved context below. If the context is insufficient, say that the reason cannot be fully verified from the provided context.

Input message:
{input_message}

Predicted relation:
- relation_type: {relation_type}
- candidate_node_type: {candidate_node_type}
- candidate_value: {candidate_value}
- model_score: {model_score}

Retrieved context:
{retrieved_context}

Tasks:
1. Determine whether the predicted relation is operationally plausible.
2. Identify the strongest evidence from the retrieved context.
3. Explain the likely business meaning of the relation.
4. Suggest one follow-up action for the user.

Return JSON:
{
  "is_plausible": true/false,
  "evidence_summary": "...",
  "business_meaning": "...",
  "follow_up_action": "...",
  "limitations": "..."
}
```
