# Results — Product Quality & Customer Segmentation (Clustering)

**Model:** K-Means, k selected by silhouette score over k=2..6. Feature set: `return_rate_pct`,
`total_orders_lifetime`, `total_returns_lifetime`, `avg_order_value_usd`,
`refund_amount_requested_usd`, `days_to_return`, `account_age_years`,
`customer_support_contacts`, `is_quality_issue_reason` — **deliberately excludes** the fraud-flag
columns used by the classification model, so this is an independent analytical lens, not a
re-derivation of the fraud label. Standardized (`StandardScaler`, mean 0 / std 1) since K-Means is
distance-based. Trained and evaluated in `notebooks/02_ml_modeling.ipynb`, Section 3.

## Result: k=3

| Cluster | n | Avg return rate | Avg orders lifetime | Avg order value | Avg account age (yrs) | % quality-issue returns | Dominant abuse mix |
|---|---|---|---|---|---|---|---|
| 0 | 6,646 | 44.8% | 27.2 | $484.01 | 3.43 | 22% | Fraudulent Return-heavy (69%), Wardrobing (31%) |
| 1 | 43,829 | 6.8% | 39.6 | $157.25 | 3.42 | **38%** | Legitimate-dominant (96%) |
| 2 | 9,525 | 57.7% | 58.8 | $129.18 | 3.42 | 19% | Policy Abuser-heavy (72%), Wardrobing (18%) |

Suggested business-facing names (used in the deck/report):
- **Cluster 0 — "High-value fraud-risk returners"**: fewer, high-value orders, elevated return
  rate, skews toward Fraudulent Return / Wardrobing. Route to manual fraud review.
- **Cluster 1 — "Core legitimate base"**: 73% of customers, low return rate, almost entirely
  Legitimate — but carries the *highest* quality-issue-return share (38%). This is the segment
  where product-quality fixes (not fraud controls) move the needle.
- **Cluster 2 — "Frequent policy-abuse returners"**: high order and return volume, low order value,
  dominated by Policy Abuser. Candidate for return-policy tightening (e.g. return windows, restocking
  fees) rather than fraud escalation.

## Weaknesses

- **Clusters are behaviorally, not causally, defined.** K-Means groups by distance in the scaled
  feature space; it does not explain *why* Cluster 1 carries the highest quality-issue-return share.
  Follow-up analysis (e.g. `return_reason` × `product_category` crosstabs, already available in the
  `silver` table) is needed before recommending a specific vendor/QA fix — this notebook stops at
  segmentation, not root-cause diagnosis.
- **k was chosen purely by silhouette score**, which favors compact, well-separated clusters but
  says nothing about whether 3 segments are the *actionable* number for a fraud/ops team. A
  business stakeholder might prefer a coarser 2-segment split (fraud-risk vs. not) or a finer one
  that separates Cluster 0's Fraudulent-Return and Wardrobing customers, who plausibly need
  different interventions despite landing in the same cluster.
- **No stability check.** We did not re-run K-Means with different random seeds or bootstrap
  samples to confirm cluster assignments are stable; with real production data (which will drift
  over time) this should be re-validated periodically, not treated as a one-time labeling.
- **Silhouette scores in absolute terms were modest** (see the notebook's k=2..6 sweep) — the
  clusters are real but not sharply separated, consistent with continuous behavioral spectra rather
  than natural discrete groups. Treat cluster boundaries as decision thresholds for operational
  routing, not as claims about distinct customer "types."
- **Excluding fraud-flag columns was a deliberate choice**, not a neutral default — it means this
  clustering cannot be used on its own to catch fraud; it is complementary to, not a substitute for,
  the classification model in `fraud-classification-results.md`.
