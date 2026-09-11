"""Export the consulting report and executive deck HTML deliverables to PDF.

Usage:
    source venv/bin/activate
    pip install playwright && python3 -m playwright install-deps chromium   # once
    python3 src/export_pdfs.py

Uses Playwright against the system-installed Google Chrome (channel="chrome") rather than
downloading a separate Chromium build. display_header_footer is explicitly False — Chrome's
`--print-to-pdf-no-header` CLI flag stopped being honored on recent Chrome versions, so the
DevTools Protocol print options (which Playwright wraps) are used instead.
"""
import pathlib
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent

JOBS = [
    {
        "src": ROOT / "deliverables/report/return-risk-intelligence-report.html",
        "dst": ROOT / "deliverables/report/return-risk-intelligence-report.pdf",
        "pdf_kwargs": {
            "format": "A4",
            "margin": {"top": "14mm", "bottom": "14mm", "left": "12mm", "right": "12mm"},
            "print_background": True,
        },
    },
    {
        "src": ROOT / "deliverables/presentation/return-risk-intelligence-deck.html",
        "dst": ROOT / "deliverables/presentation/return-risk-intelligence-deck.pdf",
        "pdf_kwargs": {
            "width": "297mm",
            "height": "167mm",
            "margin": {"top": "0", "bottom": "0", "left": "0", "right": "0"},
            "print_background": True,
        },
    },
]


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome")
        page = browser.new_page()
        for job in JOBS:
            page.goto(f"file://{job['src']}")
            page.pdf(path=str(job["dst"]), display_header_footer=False, **job["pdf_kwargs"])
            print(f"wrote {job['dst'].relative_to(ROOT)}")
        browser.close()


if __name__ == "__main__":
    main()
