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
- **No cost-sensitive threshold tuning.** We report standard 0.5-style multi-class predictions;
  a real deployment should set the false-flag threshold on "Legitimate → Fraudulent Return" much
  higher than the reverse, since wrongly blocking a genuine customer's refund is a worse business
  outcome than a slow manual review — that threshold work is flagged as a next step in
  Recommendations, not done here.
