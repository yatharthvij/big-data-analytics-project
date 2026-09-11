# Results — Regression (Refund Dollar Exposure)

**Model:** Linear Regression vs. GBTRegressor, predicting `refund_amount_requested_usd`. Trained
and evaluated in `notebooks/02_ml_modeling.ipynb`, Section 4.

## Reframing "return probability" honestly

The project's own scope names "return probability" as a sub-problem, but every row in this dataset
is already a return — there is no non-returning-order population to compare against, so
"P(this order gets returned)" is not answerable from this data without fabricating a negative class
we don't have. The operationally useful analog **is** answerable: predict the **dollar size of the
refund exposure** the moment a return is filed, before any manual audit happens. This is directly
useful for finance/reserve accounting and for prioritizing high-dollar returns for review regardless
of fraud status, and it gives the project a genuine third analytical approach rather than leaving
the naming gap unaddressed.

**Leakage guard:** `refund_to_order_value_ratio` (an engineered Phase 2 feature) is algebraically
`refund_amount_requested_usd / avg_order_value_usd` — an exact derivative of the target — so it is
excluded from this model's features, along with the target itself (which was a legitimate feature
for the *classification* model, predicting abuse type, but would be pure leakage here).

## Headline numbers

| Model | RMSE ($) | MAE ($) | R² |
|---|---|---|---|
| Naive: refund = order value (no ML) | 18.63 | 13.88 | — |
| **Linear Regression (final)** | **11.11** | **8.62** | **0.993** |
| Gradient-Boosted Trees (GBTRegressor) | 18.39 | 10.64 | 0.982 |

**Linear Regression wins**, cutting RMSE by 40% versus the naive baseline and clearly beating
GBTRegressor, which barely clears the naive bar. This is the reverse of the classification result
(Section 5.1 of the report), where the more complex Random Forest won — a deliberate, disclosed
contrast: model complexity should match the problem's actual shape, not default to "more complex is
better."

**Why Linear Regression wins:** `avg_order_value_usd` alone drives **92.5%** of GBTRegressor's
feature importance (`docs/regression-feature-importance.csv`) — refund amount is close to linear in
order value, so a linear model fits that shape more efficiently than a tree ensemble tuned for
non-linear interactions and feature crosses that mostly aren't present here.

## Weaknesses

- **This is not literally "return probability."** We are explicit about the reframing above — a
  reader expecting a P(return) model will not find one, because this dataset structurally cannot
  support one. If a future iteration adds a non-returning-order population (e.g. joining against the
  full order book, not just the returns), a true return-probability classifier becomes possible and
  should replace this regression's business framing, not sit alongside it.
- **The extremely high R² (0.993) is a near-mechanical relationship, not evidence of a subtle model.**
  Refund amount is fundamentally close to order value by construction in this dataset; the model is
  mostly learning "refund ≈ order value, adjusted slightly," not uncovering complex behavioral
  drivers of refund size. The naive-baseline comparison above exists specifically to prevent this R²
  from being read as more impressive than it is — Linear Regression's real contribution is the 40%
  error reduction over that naive baseline, not the R² figure in isolation.
- **GBTRegressor's underperformance may be a default-hyperparameter artifact, not a fundamental
  result.** We used `maxDepth=6, maxIter=100` without tuning; a properly cross-validated GBT might
  close some of the gap to Linear Regression. We did not run that search here (time-boxed scope) and
  are not claiming GBT is categorically worse for this kind of problem — only that, as configured, it
  under-delivers relative to the simpler model on this dataset.
- **Same synthetic-data caveat as the classifier applies in spirit**, though less severely: a
  near-linear relationship this clean is more plausible in a synthetic dataset (with a
  formula-based `refund_amount_requested_usd` generator) than in noisy real-world refund data, where
  partial refunds, restocking fees, and store-credit-vs-cash distinctions would add real-world noise
  this dataset doesn't have.
- **No temporal validation**, same limitation as the classifier — the 75/25 split is random, not
  time-based, so drift in the relationship between order value and refund amount over time (e.g. a
  policy change to partial refunds) is unmeasured here.
