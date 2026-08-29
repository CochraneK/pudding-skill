# pudding-skill — Scrollytelling Data Visualization Starter

[![Svelte](https://img.shields.io/badge/Svelte-5-FF3E00?logo=svelte)](https://svelte.dev/)
[![LayerCake](https://img.shields.io/badge/LayerCake-0.19-3B82F6)](https://layercake.graphics/)
[![Vite](https://img.shields.io/badge/Vite-8-646CFF?logo=vite)](https://vitejs.dev/)

A **WorkBuddy Skill + SvelteKit starter** for creating [Pudding.cool](https://pudding.cool)-style scrollytelling data visualizations.

> ⚠️ This project is a **fork/derivative** of [the-pudding/svelte-starter](https://github.com/the-pudding/svelte-starter) v6.25.1 (MIT License). The original's brand assets (logos, wordmarks) have been removed. See [License & Attribution](#license--attribution).

---

## Quick Start

```bash
git clone https://github.com/cochranek/pudding-skill.git
cd pudding-skill
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) to see the demo.

---

## What Is This?

This project provides:

1. **A SvelteKit starter** — ready-to-run scrollytelling project based on the-pudding's production template
2. **A WorkBuddy Skill** (`pudding-scrolly`) — an AI-powered pipeline that automates the entire scrollytelling creation workflow

### Skill: 6-Stage Workflow

When invoked via WorkBuddy, the `pudding-scrolly` skill follows:

```
Stage 1: Requirements Gathering
Stage 2: Data Analysis (analyze_data.py)
Stage 3: Narrative Design  
Stage 4: Project Scaffold (jsDelivr CDN)
Stage 5: Component Generation (generate_components.py)
Stage 6: Build & Preview (npm run dev)
```

---

## Project Structure

```
pudding-skill/
├── src/
│   ├── actions/          # Svelte actions (focusTrap, inView, etc.)
│   ├── components/       # Svelte components
│   │   ├── demo/         # Demo components (Scrolly, Map, etc.)
│   │   ├── layercake/    # Chart components (Area, Bar, Scatter)
│   │   └── helpers/      # Utility components
│   ├── routes/           # SvelteKit routes
│   ├── styles/           # CSS (variables, normalize, app.css)
│   ├── svg/              # SVG assets (generic icons only)
│   └── data/             # Data files (copy.json, etc.)
├── scripts/              # Skill generation scripts
│   ├── analyze_data.py
│   └── generate_components.py
├── svelte.config.js
├── vite.config.js
└── package.json
```

### Chart Types

| Type | Component | Description |
|------|-----------|-------------|
| Line | `LineChart.svelte` | Time-series / trend lines |
| Bar  | `BarChart.svelte`  | Categorical comparisons |
| Scatter | `ScatterPlot.svelte` | Correlation / distribution |
| Area | `AreaChart.svelte` | Volume / cumulative trends |
| Text | `TextHighlight.svelte` | Annotated text highlights |

---

## Design Language

The starter follows Pudding.cool's design principles:

- **Scroll-driven narrative** — sticky chart on left/center, text steps scroll over it
- **Minimalist typography** — serif for body, monospace/sans for UI
- **Data-first** — charts are the hero, annotations are sparse
- **Mobile-first responsive** — built for all screen sizes

---

## Network Compatibility

Since `github.com` and `raw.githubusercontent.com` may be unreachable in certain network environments (e.g., mainland China), the Skill scaffolding uses **jsDelivr CDN** (`cdn.jsdelivr.net`) as the primary download source for the template files.

---

## License & Attribution

- **Code**: MIT License (same as the original [the-pudding/svelte-starter](https://github.com/the-pudding/svelte-starter))
- **The Pudding brand assets**: All original logos, wordmarks, and brand SVGs have been removed from this fork. Refer to [pudding.cool](https://pudding.cool) for usage rights.
- **This fork's additions** (scripts, customization, Skill integration): MIT License
