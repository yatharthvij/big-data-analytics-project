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
- **Phase 3 (ML, PySpark MLlib)** — `notebooks/02_ml_modeling.ipynb`. Executed end-to-end, 0 errors.
  Two independent approaches: Random Forest (class-weighted, primary) vs. Logistic Regression
  baseline on `abuse_label` (weighted F1 0.999 / 0.998 — see the honest-limitations note below
  before quoting this), and K-Means clustering (k=3 by silhouette) on features that deliberately
  exclude fraud flags, for quality/customer segmentation. Writes metric CSVs to `docs/` and models
  to `data/processed/models/`.
- **Deliverables** — `deliverables/report/` (11-page HTML+PDF consulting report) and
  `deliverables/presentation/` (exactly 10 HTML+PDF slides) both built and rendered via
  `src/export_pdfs.py` (Playwright + system Chrome — `--print-to-pdf-no-header` CLI flag doesn't
  work on recent Chrome, use the DevTools Protocol path instead). Both visually QA'd at full
  resolution (rendered to PNG via PyMuPDF) — no overflow/collisions.
- **docs/** — per-model results write-ups (`fraud-classification-results.md`,
  `quality-clustering-results.md`), each with an explicit **weaknesses** section. Structure mirrors
  a stronger reference project from the same course (see below).
- **Deck slide 10** ends with a short video (`deliverables/presentation/assets/thank-you.mp4`,
  ~13s) — live `<video controls>` in the HTML, falls back to a Playwright-captured poster frame
  (`thank-you-poster.jpg`) under `@media print` since it can't play inside a static PDF.
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
3. Optional polish: the architecture diagram's Sqoop-box annotation slightly touches its connector
   line in the report SVG (cosmetic only, still legible) — revisit if there's time.

Note: timelines/submission dates are deliberately not mentioned anywhere in this repo (README,
report, deck) — user's instruction. Don't reintroduce specific dates without asking.
