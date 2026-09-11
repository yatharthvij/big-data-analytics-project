# Return Risk Intelligence

**Big Data Analytics group project · NMIMS MBA · 2026**

An end-to-end PySpark/MLlib solution for an e-commerce retailer: triage every return request into
**legitimate**, **policy abuse**, **fraudulent return**, or **wardrobing**; price the refund dollar
exposure the moment a return is filed; and separately segment customers by behavior to surface
**product-quality** problems the fraud label alone can't see — so manual audit capacity goes where
it's actually needed instead of reviewing every return the same way.

---

## The business problem in one paragraph

A retailer's return-audit team reviews disputed returns manually, at spreadsheet speed, with
inconsistent criteria across reviewers. **29.9% of returns in this dataset are not genuine**
(Policy Abuser 12.0%, Fraudulent Return 10.2%, Wardrobing 7.7%) — and each of those needs a
*different* response: a fraud investigation, a policy fix, or nothing at all. Meanwhile, product
defects hide inside the 70% "legitimate" bucket, invisible to any fraud-only view, and never reach
the QA team that owns them. This is a **triage** problem, not a "reduce the return rate" problem.

**This is not hypothetical.** The National Retail Federation forecasts **$849.9B** in 2025 retail
merchandise returns, with online sales returned at **19.3%** — above the 15.8% all-channel average.
Appriss Retail's 2024 industry study (60+ retailers, with Deloitte) found **15.14%** of all returns
fraudulent, costing retailers **$103B** in 2024, and specifically flagged **wardrobing** — one of
this project's four target classes — as a top concern for 60% of retail executives. Our own
dataset's combined Fraudulent Return + Wardrobing rate (**17.9%**) sits close to that 15.14%
figure — the class *prevalence* here is realistically calibrated to real-world reporting. Full
citations in `deliverables/report/return-risk-intelligence-report.html` Appendix C.

## The data

| | |
|---|---|
| Source | `ecommerce_return_abuse_dataset.csv` (Kaggle) |
| Scale | 60,000 orders × 35 features |
| Quality | 0 missing values, 0 duplicate `order_id` — verified programmatically, not assumed (`notebooks/01_data_engineering.ipynb` §2) |
| Target | `abuse_type` — Legitimate 70.1% · Policy Abuser 12.0% · Fraudulent Return 10.2% · Wardrobing 7.7% |

> **Honest limitations** (stated up front, also in the report): this is a **Kaggle synthetic**
> dataset. The classification model scores 0.998–0.999 weighted F1 — unrealistically high for a
> live fraud operation. Feature importance is spread across ~15 features with no single dominant
> leak, so it isn't a one-column shortcut, but synthetic label generators typically compose the
> target from a fairly clean rule that real transactional data never gives you. We present the
> model as **proof of the pipeline and methodology**, not a production performance guarantee — see
> `docs/fraud-classification-results.md` for the full caveat and a realistic 80–90% F1 target.
> There is also **no temporal holdout** (random 75/25 split, not time-based), so concept drift is
> unmeasured here and must be built into any production rollout.

## Key findings

1. **Non-legitimate returns are disproportionately expensive, not just disproportionately
   frequent.** 29.9% of orders carry **43.8% of refund dollars ($4.64M of $10.57M)**; Fraudulent
   Return claims average **$434.73** vs. **$141.14** for legitimate returns — a 3.1× gap.
2. **The classifier earns its complexity.** Random Forest hits perfect precision/recall on the
   binary "needs a second look" framing where a free 4-flag heuristic tops out at F1 0.61.
3. **The quality problem is broad-based, not one bad vendor.** Quality-issue rates band tightly
   (31.5%–35.2%) across all 12 product categories — Cluster 1's 38% quality-issue share (73% of
   customers, near-zero fraud) is a systemic pattern, not a single vendor waiting to be found.
4. **A simpler model wins honestly on refund-exposure sizing.** Linear Regression beats both a
   naive "refund = order value" baseline (40% RMSE reduction) and a more complex GBTRegressor —
   refund amount is close to linear in order value, and forcing a non-linear model on doesn't help.
5. **$1.88M is reachable today with zero ML.** The "high-value item + no photo evidence" pattern
   alone (4,673 orders) is a policy fix, live independent of the classifier's rollout.

## Repository layout

```
big-data-analytics-project/
├── docs/                      Guides and per-model results — each with its own weaknesses section
│   ├── fraud-classification-results.md   Classification results + honest limitations
│   ├── fraud-classification-results.csv  Model comparison metrics
│   ├── rf-feature-importance.csv         Random Forest feature importances
│   ├── baseline-comparison-results.csv   Free 4-flag rule vs. Random Forest
│   ├── threshold-analysis-results.csv    Precision/recall sweep on Fraudulent Return probability
│   ├── quality-clustering-results.md     Clustering results + honest limitations
│   ├── quality-clustering-results.csv    Cluster profile
│   ├── silhouette-selection-results.csv  k=2..6 silhouette sweep behind the k=3 choice
│   ├── quality-deep-dive-results.csv     Quality-issue $ by product category (all 12)
│   ├── regression-results.md             Regression results + honest limitations
│   ├── regression-results.csv            Linear Regression vs. GBTRegressor vs. naive baseline
│   ├── regression-feature-importance.csv GBTRegressor feature importances
│   └── ProjectGuideLines *.pdf           Course guidelines (project brief)
├── notebooks/                 The executable PySpark deliverable (Phases 2 & 3)
│   ├── 01_data_engineering.ipynb     Bronze → Silver → Gold: outliers, features, encoding, scaling
│   └── 02_ml_modeling.ipynb          Classification + clustering + regression, all evaluated
├── data/                       The data lake — raw + processed (Bronze/Silver/Gold). Gitignored.
├── deliverables/
│   ├── report/                       Consulting report — 17 pages, HTML + PDF
│   └── presentation/                 Executive deck — 10 slides (HTML + PDF), click-through nav
│       └── assets/                       Closing-slide video + poster fallback for the PDF export
├── src/
│   └── export_pdfs.py                Renders both deliverables' HTML to PDF (Playwright + Chrome)
├── venv/                       Local Python env (PySpark, Jupyter) — gitignored
├── CLAUDE.md                  Working context for AI-assisted development
└── README.md                  This file
```

## Architecture

Medallion (Bronze → Silver → Gold), designed for Databricks/HDFS-equivalent at production scale.
**This notebook runs directly on the static Kaggle CSV as a practical stand-in** — Sqoop/Flume/API
ingestion is not stood up against it; the diagram below is the production-scale design the
Silver→Gold transformation logic (implemented in full) is built to generalize to.

| Layer | What lives there | Why |
|---|---|---|
| **Bronze** | Raw CSV, explicit schema, untouched | Permanent replayable record |
| **Silver** | Outlier-capped, feature-engineered table | Cleaned once, reused by all three models |
| **Gold** | Encoded + scaled `features` vector, train/test split | Model-ready, consistent across classification, clustering, and regression |

Full diagram with ingestion tools (Sqoop batch / Flume streaming / API connectors) in
`deliverables/report/return-risk-intelligence-report.html`, Section 3.

## Models (Phase 3 — at least two required; we shipped three independent approaches)

1. **Multi-class classification** — Random Forest (200 trees, class-weighted) vs. multinomial
   Logistic Regression baseline, on `abuse_type`. Spark MLlib's `GBTClassifier` only supports
   binary classification, so Random Forest — which natively handles 4 classes — is the primary
   model. Weighted F1: **0.999** (Random Forest) vs. 0.998 (baseline) — see the honest-limitations
   caveat above before quoting this number as a production expectation. Also benchmarked against a
   free 4-flag rule-based baseline (F1 0.61) and a cost-sensitive threshold sweep on
   Fraudulent-Return probability (9 points, 0.1–0.9).
2. **K-Means clustering** — 3 behavioral segments (k=3 is the genuine silhouette maximum — 0.560,
   with a sharp cliff to 0.217 at k=4 — not a business-convenience choice) from customer/order
   features that deliberately **exclude** the fraud-flag columns used by the classifier. Finds a
   43,829-customer "core legitimate" segment that is still 38% quality-issue-driven, and a
   category-level deep-dive that found the quality problem is **broad-based** (31.5%–35.2% across
   all 12 categories) rather than one bad vendor.
3. **Regression** — Linear Regression vs. GBTRegressor predicting refund dollar exposure, the
   honest analog of "return probability" on a dataset where every row is already a return. Linear
   Regression wins (R²=0.993, RMSE $11.11), beating a naive "refund = order value" baseline
   (RMSE $18.63) by 40% — a deliberate, disclosed contrast with Approach 1, where the more complex
   model won instead.

Full results, each with its own weaknesses section: `docs/fraud-classification-results.md`,
`docs/quality-clustering-results.md`, `docs/regression-results.md`.

## Strategic recommendations (full detail in the report, Section 7)

1. **Ship the photo-evidence policy rule first** — $1.88M of exposure, zero ML required.
2. **Deploy the classifier as a triage score**, not an auto-block; re-threshold asymmetrically
   using the Section 5.1 sweep once real cost estimates exist.
3. **Route Cluster 1's quality problem to QA as a systemic audit**, not a vendor hunt — the
   deep-dive found no single category responsible.
4. **Tighten policy, don't investigate, for Cluster 2** — a shorter return window fits its
   high-volume/low-value pattern better than a fraud review would.
5. **Feed the refund-exposure regressor to Finance**, not just Fraud & Risk — a reserve-accounting
   input independent of whether a return turns out to be fraud, abuse, or genuine.
6. **Re-validate quarterly** — no temporal holdout exists in this dataset, so drift is unmeasured
   until a rolling time-based validation window is built into production.

## Running it

```bash
# One-time setup
python3 -m venv venv
source venv/bin/activate
pip install pyspark==3.5.1 jupyter pandas numpy matplotlib seaborn playwright
python3 -m playwright install-deps chromium   # once, for PDF export

# Place the dataset (see data/README.md)
# data/ecommerce_return_abuse_dataset.csv

# Rebuild the pipeline, in order
jupyter nbconvert --to notebook --execute --inplace notebooks/01_data_engineering.ipynb
jupyter nbconvert --to notebook --execute --inplace notebooks/02_ml_modeling.ipynb
# or open them in Jupyter and run all cells — each is self-contained and prints its own results

# Rebuild the PDF deliverables from the HTML
python3 src/export_pdfs.py
```

Outputs land in `data/processed/` (Parquet tables + saved models) and `docs/*.csv` (metric CSVs
consumed by the report and deck). The deck (`deliverables/presentation/*.html`) is click-through —
`←`/`→`, Space, Page Up/Down, and Home/End all navigate; open it directly in a browser.

## Rubric coverage (20 marks)

| Criterion | Marks | Where it's addressed |
|---|---|---|
| Business Problem Definition & Executive Storytelling | 3 | This README · Report §1 (incl. Industry Background) · Deck slides 1–3 |
| Data Engineering & Architecture | 4 | `notebooks/01_data_engineering.ipynb` · Report §3–4 · Deck slides 4–6 |
| Feature Engineering & Data Preparation | 3 | `notebooks/01_data_engineering.ipynb` §4 · Report §4.3 · Deck slide 6 |
| Machine Learning Implementation | 4 | `notebooks/02_ml_modeling.ipynb` (3 approaches) · Report §5.1–5.3 · Deck slides 7–8 |
| Model Evaluation & Interpretation | 2 | `docs/*-results.md` weaknesses sections · baseline/threshold/silhouette analyses · Deck slide 7 |
| Business Recommendations & Strategic Value | 2 | Report §6–7 · Deck slide 9 |
| Professionalism, Documentation & Presentation | 2 | This README · `CLAUDE.md` · phased git history · HTML+PDF deliverables |

## Team

| Name | Roll no. | Workstream owned | Artifacts |
|---|---|---|---|
| Subham Ranjan | A017 | Data acquisition & Bronze/Silver pipeline | `notebooks/01_data_engineering.ipynb` |
| Shriya | A023 | Feature engineering & Gold layer | `notebooks/01_data_engineering.ipynb` §4 |
| Abhinav Kumar | A035 | Classification modeling & evaluation | `notebooks/02_ml_modeling.ipynb` §2 |
| Dev Vagrecha | A049 | Clustering, quality deep-dive & regression | `notebooks/02_ml_modeling.ipynb` §3–4 |
| Samruddhi Pradhan | A054 | Architecture & enterprise design | Report §3 |
| Yatharth Vij | A072 | Narrative, report & deck | The report; the deck |
