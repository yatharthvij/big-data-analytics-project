# Working context — Return Risk Intelligence

**NMIMS MBA Big Data Analytics group project.** Topic: predicting return probability, return fraud,
and product quality issues in e-commerce, on `ecommerce_return_abuse_dataset.csv` (Kaggle, 60,000
rows × 35 cols). Full narrative is in `README.md`; this file is working context for picking the
project back up.

## Status: Phases 2–4 complete, submission prep remaining

- **Phase 2 (data engineering)** — `notebooks/01_data_engineering.ipynb`. Executed end-to-end,
  0 errors. Bronze (explicit schema) → Silver (0 nulls/dupes verified, IQR-capped outliers, 7
  engineered features, sanity-checked) → Gold (StringIndexer+OHE for nominals, ordinal map for
  `customer_segment`, StandardScaler, 75/25 split seed=42). Writes to `data/processed/`.
- **Phase 3 (ML, PySpark MLlib)** — `notebooks/02_ml_modeling.ipynb`. Executed end-to-end, 0 errors,
  22 code cells. **Three independent approaches**, one per named sub-problem in the project's own
  title:
  1. Classification — Random Forest (class-weighted, primary) vs. Logistic Regression on
     `abuse_label` (weighted F1 0.999/0.998 — see honest-limitations note), benchmarked against a
     free 4-flag rule-based baseline (F1 0.61) and a cost-sensitive threshold sweep on Fraudulent
     Return probability.
  2. K-Means clustering (k=3, genuine silhouette maximum, not a business-convenience pick) on
     fraud-flag-excluded features, closed out with an actual category-level quality deep-dive
     (found the quality problem is broad-based 31.5–35.2% across all 12 categories, not one vendor).
  3. Regression — Linear Regression vs. GBTRegressor predicting refund dollar exposure, the honest
     analog of "return probability" on a dataset with no non-return population. Linear Regression
     wins (R²=0.993, beats naive "refund=order value" baseline by 40% RMSE) — the reverse of
     Approach 1, where the more complex model won; stated as a deliberate, disclosed contrast.
  Writes 9 metric CSVs to `docs/` and models to `data/processed/models/`.
- **Deliverables** — `deliverables/report/` (17-page HTML+PDF consulting report) and
  `deliverables/presentation/` (exactly 10 HTML+PDF slides) both built and rendered via
  `src/export_pdfs.py` (Playwright + system Chrome — `--print-to-pdf-no-header` CLI flag doesn't
  work on recent Chrome, use the DevTools Protocol path instead). Both visually QA'd at full
  resolution (rendered to PNG via PyMuPDF) — no overflow/collisions. Report follows the exact
  section spec from the guidelines PDF: Executive Summary, Business Context (incl. Industry
  Background with real NRF/Appriss Retail citations), Data Understanding, Enterprise Architecture,
  Data Engineering, Machine Learning (5.1/5.2/5.3 per approach), **Business Insights** (§6) and
  **Strategic Recommendations** (§7) as two separate sections (not combined), Appendix.
- **docs/** — per-model results write-ups (`fraud-classification-results.md`,
  `quality-clustering-results.md`, `regression-results.md`), each with an explicit **weaknesses**
  section. Structure mirrors a stronger reference project from the same course (see below).
- **Deck slide 10** ends with a short video (`deliverables/presentation/assets/thank-you.mp4`,
  ~13s) — live `<video controls>` in the HTML, falls back to a Playwright-captured poster frame
  (`thank-you-poster.jpg`) under `@media print` since it can't play inside a static PDF.
- **Deck is dark-themed** (screen and exported PDF both) — a full palette flip, not just a CSS
  variable swap, since the SVG charts and several inline styles use hardcoded hex rather than the
  `:root` custom properties. If you touch deck colors again, search for literal hex codes
  (`grep -oE '#[0-9A-Fa-f]{6}'`) as well as `var(--...)` — both exist in this file.
- **Deck slide 6** is "Key findings & Risks/roadmap" (two-column), not Feature Engineering —
  repurposed since Feature Engineering isn't one of the guidelines' 8 named exec-deck topics and
  is already covered in the notebook + Report §4.3. Slides 7 ("Approach 1 — Classification") and
  9 (recommendations) cross-reference slide 6 by number; keep those in sync if slides move again.
- **Team**: Subham Ranjan (A017), Shriya (A023), Abhinav Kumar (A035), Dev Vagrecha (A049),
  Samruddhi Pradhan (A054), Yatharth Vij (A072) — filled in identically in `README.md`, the
  report's Appendix B, and the deck's title/closing slides.

## Known caveat baked into every deliverable

Both classification models score 0.998–0.999 weighted F1 — unrealistically high. Feature importance
is spread across ~15 features (no single-column leak), but this is a **Kaggle synthetic dataset**
whose label generator likely composes `abuse_type` from a fairly clean rule. Every deliverable
(notebook, docs, report, deck, README) states this explicitly and gives 80–90% weighted F1 as the
realistic production target — do not remove or soften this caveat when editing any of them.

## Structure decision

Repo layout (`data/`, `docs/`, `notebooks/`, `deliverables/{report,presentation}/`, `src/`,
`CLAUDE.md`, `README.md`) was deliberately aligned to match a stronger example group project shared
by the user (`~/Desktop/BDA/Poker`), specifically: honest-limitations framing stated up front,
per-model `docs/*-results.md` with a weaknesses section, HTML+PDF deliverables via a checked-in
export script (not ad-hoc), and gitignored `data/` with a `README.md` explaining how to regenerate
it. Do not casually rename these top-level folders again without checking notebook path references
(`../data/...`, `../docs/...`) in both notebooks.

## Remaining before submission

1. ~~Fill in the team table~~ — done, see Team above.
2. ~~Push to GitHub with meaningful commit history~~ — done, pushed to
   `github.com/yatharthvij/big-data-analytics-project`.
3. ~~Deepen analysis vs. the reference project~~ — done: added baseline comparison, cost-sensitive
   threshold sweep, quality deep-dive, silhouette-sweep chart, a full third ML approach
   (regression), and a real-citation Industry Background section, closing the explicit rubric gaps
   found by re-reading the guidelines PDF (Business Insights/Recommendations were one combined
   section, should be two; "return probability" in the project's own title had no model behind it;
   Industry Background was entirely absent).
4. ~~Sqoop-box annotation overlap~~ — fixed (text shortened, dead overlapping path removed).
5. ~~Full project audit for broken/inconsistent content~~ — done. Found and fixed: a deck-only CSS
   bug (`.r` class zeroed `padding-right` unconditionally, collapsing the gap between adjacent
   right-aligned table headers whenever a `.r` column wasn't the last one — now scoped to
   `:last-child`); the deck's title-slide caption still said "two independent... approaches" and
   omitted regression entirely, after the rest of the project had moved to three; `data/README.md`
   didn't mention the two regression models now saved to `processed/models/`; a dead, unused
   `.todo` CSS rule (harmless, removed for cleanliness). Numbers were cross-checked against the
   underlying `docs/*.csv` files and all matched exactly — no data/reporting discrepancies found.

Note: timelines/submission dates are deliberately not mentioned anywhere in this repo (README,
report, deck) — user's instruction. Don't reintroduce specific dates without asking.
