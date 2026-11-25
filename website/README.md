# Presentation website

A 10-slide, full-screen executive presentation for the Austin Animal Center analysis. It is a storytelling
layer only; the Power BI report (`powerbi/Austin_Animal_Center_Analytics_Final.pbix`) is demonstrated
separately in Power BI Desktop.

## Launch

No build step, server or internet connection is needed. All files are local:

```text
website/
├── index.html              # the 10 slides
├── css/presentation.css    # layout, typography, responsive rules
└── js/presentation.js      # navigation, scaling, presenter notes
```

1. Open `website/index.html` in Chrome or Edge (double-click, or drag into the browser).
2. Press **F** (or the *Full screen* button) for full screen.
3. Optional local server, if a browser blocks local files:

```bash
python -m http.server 8000 --directory website
```

Then open http://localhost:8000.

## Presenting

| Key | Action |
|---|---|
| → · Space · Page Down | next slide |
| ← · Page Up | previous slide |
| Home / End | first / last slide |
| F | toggle full screen |
| N | toggle presenter notes (short cue per slide, bottom-right) |

* The bottom bar shows slide number, title and progress; dots jump to any slide.
* `index.html#6` opens a specific slide (useful for Q&A).
* Desktop: slides are a fixed 16:9 canvas scaled to the screen, so layout is identical on any monitor.
  Below 900 px wide the slides stack and scroll (tablet/phone review); swipe to change slide.
* Full speaking script: `presentation/PRESENTATION_SCRIPT.md`. Backup Q&A:
  `presentation/INTERVIEW_PREPARATION_KIT.md`. Live demo steps: `presentation/POWER_BI_DEMO_PLAN.md`.

## Content sources

All figures come from the validated repository outputs (`outputs/`) as documented in
`CLAUDE_PROJECT_KNOWLEDGE_KIT.md`. Slide 9 policy and public-health context was compiled on 25-11-2026 from
search summaries of the cited official sources; those pages could not be opened directly from the build
environment, so check the wording against each source before quoting it.

## Tested

Headless Chromium at 1920×1080, 1366×768 and 390×844: no console errors or failed asset loads; no content
overflow on desktop sizes; keyboard, button, dot and URL-hash navigation verified.
