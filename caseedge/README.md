# CaseEdge workspace prototype

A single-page workspace for plaintiff personal injury firms with four products:
**Medical Chronology, Case Insights, Bills & Ledger and Demand Draft**, plus a Review queue.
Every citation opens the real source PDF in a pane beside the work.

- Live artifact: https://claude.ai/artifact/NdpGhNPPrM4p4a7LBuUvMo (private; latest published is v18)
- Saved snapshots: `../CaseEdge-Workspace-v*.html` at the repo root (v18 is the current one)

## Layout of this folder

| Path | What it is |
|---|---|
| `src/template.html` | The whole page: CSS, markup and script. `/*__DATA__*/` is replaced at build time. All case data (encounters, injuries, providers, findings, ledger, review items, demand text) lives in the script near the top. |
| `src/index2.json` | Citation index for the case file: highlight rectangles per citation key, page metadata, itemized bills. |
| `src/make_pdf2.py` | Generates the fictional case file PDF and its index: `python3 src/make_pdf2.py assets/casefile.pdf src/index2.json` (reportlab, Liberation fonts). |
| `assets/casefile.pdf` | The 21-page fictional case file (exhibits 1 to 11) that citations open. |
| `build.py` | Embeds the index and PDF, writes `dist/casework.html` (publish this as the artifact) and `dist/CaseEdge-Workspace.html` (standalone). |
| `tests/*.js` | Playwright checks (see below). |

## Build, publish, test

```
python3 build.py
```

Publish `dist/casework.html` to the artifact URL above (Artifact tool, pass the URL as `url`, read it first).
Save a standalone copy at the repo root as `CaseEdge-Workspace-vNN.html` (copy `dist/CaseEdge-Workspace.html`).

The page loads PDF.js 3.11.174 from cdnjs. For local tests, fetch it into `vendor/` once:

```
mkdir -p vendor /tmp/pdfjs && cd /tmp/pdfjs && npm pack pdfjs-dist@3.11.174 && tar xzf pdfjs-dist-3.11.174.tgz \
  && cp package/build/pdf.min.js package/build/pdf.worker.min.js "$OLDPWD/vendor/" && cd -
```

Run each test as `NODE_PATH=$(npm root -g) node tests/<name>.js "$PWD" "$PWD/dist/casework.html"`
(Chromium is at `/opt/pw-browsers/chromium`):

- `smoke.js` loads the page, opens a citation, reports errors and the PDF pane width (expect 600 at 1440).
- `interactions.js` opens an encounter, groups by provider, accepts the suggested demand edit (review count 5 to 4, survives reload), jumps from the review queue, opens a citation.
- `widths.js` checks for sideways scrolling in every view at 1280, 1440, 1728 and 1920, sidebar open and collapsed (expect all 0).
- `split.js` checks the 50/50 source view and phone width (main 600 / pane 600, no page scroll).
- `typescan.js` lists the font size and family of all body text in every view (expect only `13px Inter`).
- `shoot.js <dir> <file> <name> <width> <views>` writes full-page screenshots to `<dir>/shots/`.

## Design rules the owner has set (keep these)

- **One colour.** Deep sky `#0369A1` for actions and links; bright sky `#0EA5E9` only for attention marks and highlights. Everything else is ink and greys, darkened to AA contrast or better.
- **Inter only. All body text 13px**, secondary text differs only in colour. Labels 12px, section titles 15px semibold, page title 24px. No monospace; codes use tabular figures.
- **Zero border radius everywhere**, straight lines; only meaningful data marks (round timeline markers) stay round.
- **Mostly white, structured, Harvey/Legora-like**, not iOS-style bubbles. Nothing extra beyond what is asked.
- **Layout:** sidebar 240px (folds to a 60px rail). Content is full width and left-aligned, with no centring and no empty space on the right. Each section is a box with its title at the top left and a short description beside it.
- **Text** is left to right, never justified or centred. Content is narrative and descriptive (full sentences), written for paralegals and attorneys.
- **Tables all follow the encounter table's pattern:** fixed lead columns, one descriptive column that takes the spare width, a fixed status column, Source last. Shared widths: date 144, name 232, status 176, money 10%, source 124.
- **Source PDF pane** takes exactly 50% of the space right of the sidebar, with a left shadow, and opens directly on the cited page with the passage highlighted. Every citation in every product opens it.
- **Demand Draft** has a premium editor; the original, the draft and the citations can all be on screen together.

Directions tried and rejected: centred page column (v10), centred section headers or a centred reading column (v15),
justified three-column reading layout (v14), entry-style lists instead of tables (v13), and clipped, raw wording (v9 and v12).
Option B (rounded, softer shapes) exists in `../CaseEdge-Workspace-v14.html` and v15 if it is ever wanted again.
