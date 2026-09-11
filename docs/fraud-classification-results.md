# Results — Return Fraud Classification

**Model:** Random Forest (200 trees, maxDepth=10, class-weighted) vs. multinomial Logistic
Regression baseline. Target: `abuse_label` (Legitimate / Policy Abuser / Fraudulent Return /
Wardrobing). Trained and evaluated in `notebooks/02_ml_modeling.ipynb`, Section 2.

## Headline numbers

| Model | Weighted Precision | Weighted Recall | Weighted F1 |
|---|---|---|---|
| Logistic Regression (baseline) | 0.998 | 0.998 | 0.998 |
| **Random Forest (final)** | **0.999** | **0.999** | **0.999** |

Per-class F1 (Random Forest): Legitimate 1.000 · Policy Abuser 0.997 · Fraudulent Return 0.998 ·
Wardrobing 0.998. Full confusion matrix and per-class breakdown in the notebook, Sections 2c-2d.
Accuracy is reported in the notebook for completeness but was **not** used to pick the winner,
given the 70/12/10/8 class imbalance — a model that always predicts "Legitimate" scores ~70%
accuracy while catching zero fraud.

**Top drivers (feature importance):** `days_to_return`, `wishlist_to_cart_time_hrs`,
`return_rate_pct`, `return_to_order_ratio`, `tracking_number_valid` — the engineered ratio features
from Phase 2 rank alongside the raw behavioral fields, validating that feature engineering step.

## Does the model earn its complexity?

Benchmarked against a free 4-flag OR-rule baseline (`tracking_number_valid`,
`refund_to_different_account`, `multiple_accounts_flag`, `address_change_before_delivery`) on the
same binary "does this return deserve a second look" framing (Section 2e):

| Approach | Precision | Recall | F1 | Orders flagged |
|---|---|---|---|---|
| Baseline: 4-flag OR rule (no ML) | 0.811 | 0.489 | 0.610 | 2,652 |
| **Random Forest (any non-Legitimate prediction)** | **1.000** | **1.000** | **1.000** | 4,401 |

The free rule catches only 49% of non-legitimate returns and still misfires on 501 legitimate
orders — the model is not solving a problem a spreadsheet formula already solved.

## Cost-sensitive threshold analysis

Sweeping the decision threshold on Random Forest's Fraudulent Return probability (Section 2f, full
9-point sweep in `threshold-analysis-results.csv`):

| Threshold | Orders flagged | Precision | Recall |
|---|---|---|---|
| 0.1 | 1,577 | 0.944 | 1.000 |
| 0.3 | 1,493 | 0.997 | 1.000 |
| 0.5 | 1,487 | 0.999 | 0.998 |
| 0.7 | 1,454 | 1.000 | 0.977 |
| 0.9 | 1,320 | 1.000 | 0.887 |

Precision stays high throughout; recall degrades past ~0.7. The sweep, not a single chosen
threshold, is what should carry over to production, since real data will sit at a different point
on this curve.

## Why Random Forest over Gradient-Boosted Trees

Spark MLlib's `GBTClassifier` only supports **binary** classification. `abuse_label` has 4 classes,
so GBT was not usable without an artificial one-vs-rest decomposition; Random Forest natively
supports multi-class and was used instead, benchmarked against Logistic Regression.

## Weaknesses

- **The headline F1 (0.998–0.999) is unrealistically high and should not be quoted as a production
  expectation.** This is a Kaggle **synthetic** dataset; synthetic fraud-label generators typically
  compose the label from a fairly clean rule over a handful of provided columns, producing
  near-perfectly separable classes that real transactional data never gives you. Feature importance
  is spread across ~15 features with no single dominant leak, so it isn't a one-column shortcut —
  but the underlying data-generating process is still almost certainly rule-based, not organically
  noisy. **A realistic target on live data is 80–90% weighted F1**, not 99.9%.
- **No temporal validation.** The train/test split (Phase 2, `randomSplit` seed=42) is a random
  75/25 split, not a time-based holdout. A production deployment needs to validate on orders placed
  *after* the training window to catch concept drift (fraud patterns adapting to whatever the model
  learns) — this notebook does not test for that because the dataset has no reliable temporal
  ordering signal beyond `order_date`/`return_date`, and validating drift needs multiple time
  periods of labeled data we don't have.
- **Class-weighting, not resampling.** Inverse-frequency weights address the imbalance during
  training but don't change what the test set looks like; if the true production traffic mix
  differs meaningfully from 70/12/10/8 (e.g. a fraud crackdown changes the abuse rate), precision
  will shift and the model should be re-calibrated, not assumed stable.
- **Policy Abuser vs. Wardrobing overlap.** These two classes share the most behavioral similarity
  (both are non-fraudulent policy exploitation rather than deception), and the small number of
  cross-errors in the confusion matrix land almost entirely between this pair — expect this
  boundary to be the first place performance degrades on new data.
- **The threshold sweep maps the trade-off but doesn't pick a production number.** Section 2f shows
  precision/recall across nine thresholds, but choosing where to actually operate needs real cost
  estimates (dollar cost of a false fraud flag vs. a missed fraud case) that this project doesn't
  have — the sweep is the deliverable, not a specific recommended cutoff.
- **The baseline comparison uses only 4 of the available red-flag columns.** A slightly richer
  free heuristic (e.g. adding `previous_dispute_count` or `customer_support_contacts` thresholds)
  might close some of the gap to the model — we picked four clearly-known flags rather than
  exhaustively searching heuristic rule space, so "the model wins by this much" is a lower bound on
  how much a naive rule-builder could close the gap, not an upper one.
