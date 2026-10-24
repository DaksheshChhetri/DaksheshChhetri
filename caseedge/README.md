# CaseEdge workspace prototype

A single-page workspace for plaintiff personal injury firms with four products per case:
**Medical chronology, Case insights, Bills & liens and Demand draft**, plus a firm-level Review queue.
Every citation opens the real source PDF in a pane beside the work.

- Live artifact: https://claude.ai/artifact/NdpGhNPPrM4p4a7LBuUvMo (private; latest published is v21, layout A)
- Layout B artifact: https://claude.ai/artifact/3bJKW3LjgvhA7ufii9hy2m (publish `dist/casework-b.html` here)
- Saved snapshots: `../CaseEdge-Workspace-v*.html` at the repo root (v21a and v21b are the current ones)

## Layout of this folder

| Path | What it is |
|---|---|
| `src/template.html` | The whole page: CSS, markup and script. `/*__DATA__*/` is replaced at build time. All case data (encounters, injuries, providers, findings, ledger, review items, demand text) lives in the script near the top. |
| `src/index2.json` | Citation index for the case file: highlight rectangles per citation key, page metadata, itemized bills. |
| `src/make_pdf2.py` | Generates the fictional case file PDF and its index: `python3 src/make_pdf2.py assets/casefile.pdf src/index2.json` (reportlab, Liberation fonts). |
| `assets/casefile.pdf` | The 27-page fictional case file (exhibits 1 to 13, including pharmacy records, lien notices and the preservation letter) that citations open. |
| `build.py` | Embeds the index and PDF and writes two layouts: A, left-aligned (`dist/casework.html`, standalone `dist/CaseEdge-Workspace.html`) and B, a modest centred column (`dist/casework-b.html`, `dist/CaseEdge-Workspace-b.html`). |
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

- `smoke.js` loads the page, opens a citation, reports errors and the PDF pane width (expect 588 at 1440: two equal sheets).
- `interactions.js` opens an encounter, groups by provider, accepts the suggested demand edit (review count 5 to 4, survives reload), jumps from the review queue, opens a citation.
- `widths.js` checks for sideways scrolling in every view (all ten, read from `VIEWS`) at 1280, 1440, 1728 and 1920, sidebar open and collapsed (expect all 0).
- `split.js` checks the 50/50 source view and phone width (main 588 / pane 588, no page scroll).
- `typescan.js` lists the font size and family of all body text in every view (expect only `13px Inter`).
- `shoot.js <dir> <file> <name> <width> <views>` writes full-page screenshots to `<dir>/shots/`.

## Design rules the owner has set (keep these)

- **One colour.** Deep sky `#0369A1` for actions and links; bright sky `#0EA5E9` only for attention marks and highlights. Everything else is ink and greys, darkened to AA contrast or better.
- **Inter only. All body text 13px**, secondary text differs only in colour. Labels 12px, section titles 15px semibold, page title 24px. No monospace; codes use tabular figures.
- **Corners:** v18 and earlier use zero border radius everywhere. v19 is a softer pass after Legora and Wisedocs: a warm off-white canvas with white panels on it, 12px panel corners, 8px controls, 6px citations, round status dots, fainter rules and soft shadows. It is one block at the end of the CSS in `src/template.html`, so it is easy to remove.
- **Mostly white, structured, Harvey/Legora-like**, not iOS-style bubbles. Nothing extra beyond what is asked.
- **Layout:** sidebar 240px (folds to a 60px rail). Content is full width and left-aligned, with no centring and no empty space on the right. Each section is a box with its title at the top left and a short description beside it.
- **Text** is left to right, never justified or centred. Content is narrative and descriptive (full sentences), written for paralegals and attorneys.
- **Tables all follow the encounter table's pattern:** fixed lead columns, one descriptive column that takes the spare width, a fixed status column, Source last. Shared widths: date 144, name 232, status 176, money 10%, source 124.
- **Source PDF pane** takes exactly 50% of the space right of the sidebar, with a left shadow, and opens directly on the cited page with the passage highlighted. Every citation in every product opens it.
- **Demand Draft** has a premium editor; the original, the draft and the citations can all be on screen together.

- **Sheet (v21):** the work sits on one white sheet, inset 8px from the window and framed by the warm canvas; the source
  pane opens as a second sheet beside it, the same width. Layout B (`.v-center`) holds the page to a 1,320px column centred
  in the sheet on wide screens; layout A stays left-aligned. Contrast is raised on structure only (rules, tab labels, crumbs).
- **Structure:** every case page shares one header (crumbs and actions, a 28px title, facts with a stage stepper) and one tab bar.
  Each product opens with summary tiles, then stacked panels; long pages add an "On this page" row. Status is a soft pill with its dot.
  Charts are drawn in ink greys with the one accent for the figure that matters most.
- Bills & liens holds the settlement arithmetic (choose the gross and the fee), the liens, the lines to dispute, the lien screening
  (Medicare, Medi-Cal, ERISA, hospital, health plan, workers' comp, MedPay, provider) and the medical bills and specials.
  Case insights holds the valuation chart; the demand carries the time-limited demand checklist (CCP §999).
- v20 also had Litigation package, Negotiation, Case chat, Case tracker and Intake triage (`../CaseEdge-Workspace-v20.html`).

Directions tried and rejected: centred page column (v10), centred section headers or a centred reading column (v15),
justified three-column reading layout (v14), entry-style lists instead of tables (v13), and clipped, raw wording (v9 and v12).
Option B (rounded, softer shapes) exists in `../CaseEdge-Workspace-v14.html` and v15 if it is ever wanted again.
