# Pipeline

## Step 1. Message embedding

The first notebook extracts message text and converts it into semantic embeddings.

Output concept:

```text
message_text → semantic vector
```

## Step 2. Semantic clustering

Messages are grouped into issue clusters based on semantic embeddings.

The current prototype uses an initial 10-cluster structure.  
After reviewing the interpreted meanings, similar clusters can be merged into a smaller set of business-level issue categories.

## Step 3. Cluster interpretation

Each cluster is summarized using representative keywords and messages.

| Cluster | Interpreted issue type | Representative signals |
|---:|---|---|
| 0 | 공정 재고 및 음수 자재 관리 | 공정 | 재고 | 음수 | 축소 | 관리 |
| 1 | 과잉 재고 및 PO 관리 필요 | 계획 대비 과잉 | 과잉 재고 | PO 발행 | 소요 계획 대비 과잉 PO 발행된 아이템 집중 관리 필요 |
| 2 | 과잉재고 대비 초과 PO 발행 검토 | po | 과잉으로 | 조정 검토 | over 비율이 | 대비 | 과잉으로 조정 | 여전히 over |
| 3 | 미소요 및 발주 과다 품목 조정 | po l/t 대비 | 주문 과다 | 발주 과다 | 조정 | 과다 품목 |
| 4 | 공정 및 음수율 관리 개선 필요 | 공정 Over율 관리는 양호 하며 음수 처리 지연일수 개선 필요함 | WIP 공정 Over율 관리는 양호 하며 음수 처리 지연일수 개선 필요함 | 공정 Ov... |
| 5 | 재고 및 과잉 재고 집중 관리 필요 | 재고 관리 | 과잉 재고 | 재고 금액 | 필요함 | 예상 | 관리 점수 |
| 6 | 과잉 재고 금액 집중 관리 필요 | 재고 | 과잉 | 과잉 재고 | 금액 | 재고 금액 | 금액 비중이 | 집중 관리 | 주요 Item |
| 7 | 예상 재고 및 과잉 재고 집중 관리 필요 | 재고, 관리, 재고 관리, 필요, item, 점수, 과잉, 예상, 점검, 관리 점수, 과잉 재고, 집중, 대비, 및, 금액, 재고 금액, 필요함, 비중, 주... |
| 8 | 부품 조달 차질 예상 | 차질 | 차질 예상 | po | 부족으로 | 조달 차질 | 조달 | 예상 | shortage | 부족으로 생산 |
| 9 | 재고 회전율(DIO) 증가에 따른 자재 관리 강화 필요 | 전주대비 당월 예상 DIO 수준이 52% 이상 증가로 관리 강화 필요 | DIO 과잉 예상 Item 관리 필요 : IPM Module, Resin 등 | 과... |


## Step 4. Graph construction

The graph connects messages to materials, products, organizations, dates, source domains, and issue clusters.

Example graph pattern:

```text
message:M001 ─ related_to_part_no ─ part_no:PART_001
message:M001 ─ related_to_product ─ product:Product_A
message:M001 ─ related_to_org ─ org:ORG_01
message:M001 ─ belongs_to_cluster ─ cluster:1
```

## Step 5. Link prediction

Some target edges are hidden during training.  
The model learns to recover those hidden relations.

Example task:

```text
Given a message node, predict the most likely related material, product, organization, or similar issue.
```

Evaluation metrics:

- AUC
- AP
- MRR
- Hits@1
- Hits@3
- Hits@5
- Hits@10
