# Results — Product Quality & Customer Segmentation (Clustering)

**Model:** K-Means, k selected by silhouette score over k=2..6. Feature set: `return_rate_pct`,
`total_orders_lifetime`, `total_returns_lifetime`, `avg_order_value_usd`,
`refund_amount_requested_usd`, `days_to_return`, `account_age_years`,
`customer_support_contacts`, `is_quality_issue_reason` — **deliberately excludes** the fraud-flag
columns used by the classification model, so this is an independent analytical lens, not a
re-derivation of the fraud label. Standardized (`StandardScaler`, mean 0 / std 1) since K-Means is
distance-based. Trained and evaluated in `notebooks/02_ml_modeling.ipynb`, Section 3.

## Choosing k: the sweep, not just the winner

| k | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|
| Silhouette score | 0.512 | **0.560** | 0.217 | 0.296 | 0.273 |

k=3 is the genuine maximum across the sweep (`silhouette-selection-results.csv`), not a
business-convenience compromise — unlike some k-selection exercises where the silhouette-optimal k
gets overridden for interpretability, here they agree. The sharp cliff from k=3 (0.560) to k=4
(0.217) is itself worth noting: it suggests 3 clusters reflects real structure in this feature
space, and finer splits mostly divide noise rather than finding additional real segments — though
see the stability-check weakness below before treating that as fully confirmed.

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

## Quality deep-dive — closing the loop on our own recommendation

Rather than leaving "cross-reference category and reason" as a suggestion for someone else, we did
it: every quality-issue return in the full dataset, by product category (`quality-deep-dive-results.csv`):

| Product category | Quality-issue returns | Refund $ | % of category's own orders |
|---|---|---|---|
| **Clothing** | 3,951 | **$667,224** | 31.7% |
| Electronics | 2,907 | $463,754 | 34.2% |
| Shoes | 2,399 | $407,751 | 32.3% |
| Home & Kitchen | 1,971 | $322,774 | 33.8% |
| Tools | 813 | $129,884 | **35.2%** |

**The honest finding is a negative one:** quality-issue share is tightly banded (31.5%–35.2%)
across all 12 categories — no single category or vendor stands out as a disproportionate offender.
Clothing tops the dollar-exposure ranking simply because it's the largest category by volume, not
because it has an elevated defect rate. This is a **broad-based quality problem**, not a one-vendor
problem, and the recommendation is scoped accordingly (systemic QA audit, not a vendor hunt).

## Weaknesses

- **The quality deep-dive explains *what*, not *why*.** We now know the problem is broad-based
  rather than one vendor, but not *why* defect rates cluster around ~33% almost everywhere — that
  needs root-cause work (packaging audit, supplier QA sampling, description-accuracy review) this
  dataset can't answer on its own.
- **k was chosen purely by silhouette score**, which favors compact, well-separated clusters but
  says nothing about whether 3 segments are the *actionable* number for a fraud/ops team. A
  business stakeholder might prefer a coarser 2-segment split (fraud-risk vs. not) or a finer one
  that separates Cluster 0's Fraudulent-Return and Wardrobing customers, who plausibly need
  different interventions despite landing in the same cluster.
- **No stability check.** We did not re-run K-Means with different random seeds or bootstrap
  samples to confirm cluster assignments are stable; the sharp k=3→k=4 silhouette cliff above is
  suggestive of real structure but not confirmed against resampling. With real production data
  (which will drift over time) this should be re-validated periodically, not treated as a one-time
  labeling.
- **Excluding fraud-flag columns was a deliberate choice**, not a neutral default — it means this
  clustering cannot be used on its own to catch fraud; it is complementary to, not a substitute for,
  the classification model in `fraud-classification-results.md`.
