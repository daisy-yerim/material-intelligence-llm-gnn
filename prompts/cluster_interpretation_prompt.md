# Cluster interpretation prompt

## Purpose

Convert a semantic message cluster into a concise business issue label and operational explanation.

## Template

```text
You are analyzing manufacturing ERP/MES material-management messages.

Given the representative messages and keywords below, identify the operational issue represented by this cluster.

Return the result in JSON with the following keys:
- cluster_name: concise Korean business label
- problem_type: one of [inventory, procurement, production, planning, quality, logistics, other]
- summary: 2-3 sentence explanation
- representative_signals: key terms or patterns that support the interpretation
- risk_level: one of [low, medium, high]
- recommended_action: practical action for material-management staff

Cluster ID: {cluster_id}
Representative keywords: {keywords}
Representative messages:
{messages}
```

## Output example

```json
{
  "cluster_name": "과잉 재고 및 PO 과다 관리",
  "problem_type": "inventory",
  "summary": "해당 클러스터는 수요 대비 발주 또는 재고가 과다한 품목을 중심으로 구성된다. PO 발행량과 예상 재고 금액을 함께 점검할 필요가 있다.",
  "representative_signals": ["과잉 재고", "PO", "수요 대비", "재고 금액"],
  "risk_level": "high",
  "recommended_action": "초과 PO와 고재고 품목을 우선 검토하고 발주 조정 여부를 판단한다."
}
```
