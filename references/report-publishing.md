# Public report publishing

The public site is designed around one stable entry point:

`https://cochranek.github.io/pudding-skill/`

The homepage is a report shelf. Long-form stories keep their own routes, while the homepage is the single discovery surface for current and future reports.

## Add a report

1. Build the story under `src/routes/stories/<slug>/`.
2. Add one record to `src/data/report-index.json` with title, dek, status, publication date, primary route, optional secondary modules, tags, and key figures.
3. Keep all internal Svelte links base-aware with `$app/paths` so project-site hosting under `/pudding-skill` works.
4. Run the normal skill checks, benchmark, build, browser QA, and visual QA.
5. Merge to `main`. `.github/workflows/pages.yml` builds the static SvelteKit site with the repository base path and deploys it to GitHub Pages.

## Architecture

The public homepage is intentionally separate from the developer surfaces (`/demo`, `/lab`, `/generated`, `/benchmark`). That keeps the public URL stable even as the internal tooling evolves.

Each report may still have secondary modules such as an atlas, methodology appendix, or explorable. Those are exposed from the report card without turning the public homepage into a developer dashboard.

## GitHub Pages note

The deployment workflow expects GitHub Pages to use the GitHub Actions publishing source. If Pages has never been enabled for this repository, enable it once in **Settings → Pages → Build and deployment → Source → GitHub Actions**. After that, every push to `main` publishes automatically.
