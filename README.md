# Return Risk Intelligence

**Big Data Analytics group project · NMIMS MBA · 2026**

An end-to-end PySpark/MLlib solution for an e-commerce retailer: triage every return request into
**legitimate**, **policy abuse**, **fraudulent return**, or **wardrobing**, and separately segment
customers by behavior to surface **product-quality** problems the fraud label alone can't see — so
manual audit capacity goes where it's actually needed instead of reviewing every return the same way.

---

## The business problem in one paragraph

A retailer's return-audit team reviews disputed returns manually, at spreadsheet speed, with
inconsistent criteria across reviewers. **29.9% of returns in this dataset are not genuine**
(Policy Abuser 12.0%, Fraudulent Return 10.2%, Wardrobing 7.7%) — and each of those needs a
*different* response: a fraud investigation, a policy fix, or nothing at all. Meanwhile, product
defects hide inside the 70% "legitimate" bucket, invisible to any fraud-only view, and never reach
the QA team that owns them. This is a **triage** problem, not a "reduce the return rate" problem.

## The data

| | |
|---|---|
| Source | `ecommerce_return_abuse_dataset.csv` (Kaggle) |
| Scale | 60,000 orders × 35 features |
| Quality | 0 missing values, 0 duplicate `order_id` — verified programmatically, not assumed (`notebooks/01_data_engineering.ipynb` §2) |
| Target | `abuse_type` — Legitimate 70.1% · Policy Abuser 12.0% · Fraudulent Return 10.2% · Wardrobing 7.7% |

> **Honest limitations** (stated up front, also in the report): this is a **Kaggle synthetic**
> dataset. Both classification models score 0.998–0.999 weighted F1 — unrealistically high for a
> live fraud operation. Feature importance is spread across ~15 features with no single dominant
> leak, so it isn't a one-column shortcut, but synthetic label generators typically compose the
> target from a fairly clean rule that real transactional data never gives you. We present the
> model as **proof of the pipeline and methodology**, not a production performance guarantee — see
> `docs/fraud-classification-results.md` for the full caveat and a realistic 80–90% F1 target.
> There is also **no temporal holdout** (random 75/25 split, not time-based), so concept drift is
> unmeasured here and must be built into any production rollout.

## Repository layout

```
big-data-analytics-project/
├── docs/                      Guides and per-model results — each with its own weaknesses section
│   ├── fraud-classification-results.md   Classification results + honest limitations
│   ├── fraud-classification-results.csv  Model comparison metrics (written by notebook 02)
│   ├── quality-clustering-results.md     Clustering results + honest limitations
│   ├── quality-clustering-results.csv    Cluster profile (written by notebook 02)
│   ├── rf-feature-importance.csv         Random Forest feature importances (written by notebook 02)
│   └── ProjectGuideLines *.pdf           Course guidelines (project brief)
├── notebooks/                 The executable PySpark deliverable (Phases 2 & 3)
│   ├── 01_data_engineering.ipynb     Bronze → Silver → Gold: outliers, features, encoding, scaling
│   └── 02_ml_modeling.ipynb          Random Forest + Logistic Regression, K-Means, evaluation
├── data/                       The data lake — raw + processed (Bronze/Silver/Gold). Gitignored.
├── deliverables/
│   ├── report/                       Consulting report — HTML + PDF
│   └── presentation/                 Executive deck — 10 slides, HTML + PDF
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
| **Silver** | Outlier-capped, feature-engineered table | Cleaned once, reused by both models |
| **Gold** | Encoded + scaled `features` vector, train/test split | Model-ready, consistent across classification and clustering |

Full diagram with ingestion tools (Sqoop batch / Flume streaming / API connectors) in
`deliverables/report/return-risk-intelligence-report.html`, Section 3.

## Models (Phase 3 — at least two required; we shipped two independent approaches)

1. **Multi-class classification** — Random Forest (200 trees, class-weighted) vs. multinomial
   Logistic Regression baseline, on `abuse_type`. Spark MLlib's `GBTClassifier` only supports
   binary classification, so Random Forest — which natively handles 4 classes — is the primary
   model. Weighted F1: **0.999** (Random Forest) vs. 0.998 (baseline) — see the honest-limitations
   caveat above before quoting this number as a production expectation.
2. **K-Means clustering** — 3 behavioral segments from customer/order features that deliberately
   **exclude** the fraud-flag columns used by the classifier, so it's an independent lens. Finds
   a 43,829-customer "core legitimate" segment that is still 38% quality-issue-driven — the
   headline insight for the QA/vendor recommendation.

Full results, each with its own weaknesses section: `docs/fraud-classification-results.md`,
`docs/quality-clustering-results.md`.

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
consumed by the report and deck).

## Timeline

| Date (2026) | Milestone |
|---|---|
| **8 Sept** | Submission (tentative, per guidelines) — deck, executable notebook, consulting report |
| 11–12 Sept | Presentations (tentative, per guidelines) |

## Team

<!-- TODO: fill in before submission. Max 6 members. The same split is a graded appendix
     requirement — Appendix B of the report carries this table and must match. -->

| Name | Roll no. | Workstream owned | Artifacts |
|---|---|---|---|
| _TBD_ | _TBD_ | Data acquisition & Bronze/Silver pipeline | `notebooks/01_data_engineering.ipynb` |
| _TBD_ | _TBD_ | Feature engineering & Gold layer | `notebooks/01_data_engineering.ipynb` §4 |
| _TBD_ | _TBD_ | Classification modeling & evaluation | `notebooks/02_ml_modeling.ipynb` §2 |
| _TBD_ | _TBD_ | Clustering & segmentation | `notebooks/02_ml_modeling.ipynb` §3 |
| _TBD_ | _TBD_ | Architecture & enterprise design | Report §3 |
| _TBD_ | _TBD_ | Narrative, report & deck | The report; the deck |

## AI usage disclosure

Claude (Anthropic) was used throughout as an AI pair-programmer and analyst: drafting the PySpark
notebooks, generating the report and deck, and proposing the feature-engineering rationale. All
code was executed end-to-end against the real 60,000-row dataset — every metric quoted anywhere in
this repo was read directly from that execution (`docs/*.csv`), not fabricated. Full disclosure
in the report's Appendix A.
