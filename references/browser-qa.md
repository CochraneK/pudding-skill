# Browser delivery QA

Static validation and a successful Svelte build do not prove that the delivered page behaves correctly in a browser. The browser gate tests the built preview with Chromium through the Chrome DevTools Protocol and stores evidence for review.

## What it tests

For `/`, `/generated`, and `/lab`, at desktop (1440×900) and mobile (390×844), the gate checks:

- no uncaught JavaScript exceptions or console errors;
- no non-cancelled network load failures;
- exactly one `<main>` and at least one `<h1>`;
- a non-empty document title and visible body text;
- no material horizontal overflow before or after scrolling;
- no duplicate element IDs;
- all `<img>` elements have `alt` attributes;
- interactive elements have an accessible name;
- keyboard Tab can reach an interactive element when one exists;
- `prefers-reduced-motion: reduce` is actually active.

It captures one PNG for every route × viewport pair and writes a machine-readable `.qa/browser-qa.json` report.

## Run locally

Build and start the production preview first:

```bash
npm run build
npm run preview -- --host 127.0.0.1 --port 4173
```

Then, in another shell:

```bash
npm run qa:browser -- --base-url http://127.0.0.1:4173 --out .qa
```

Set `CHROME_BIN` or pass `--chrome` if Chrome/Chromium is not discoverable on `PATH`.

## CI evidence

The CI workflow uploads `.qa/` as a short-lived artifact even when browser QA fails. Inspect both `browser-qa.json` and the screenshots when diagnosing a failure or reviewing visual quality.

## What it does not prove

A PASS is mechanical, not aesthetic. It does not establish that the editorial hierarchy, annotation strategy, visual metaphor, pacing, color decisions, or mobile composition are excellent. Those remain review tasks for the agent/editor. The screenshots exist specifically to keep that human/agent review step visible rather than pretending it can be reduced to a single score.
