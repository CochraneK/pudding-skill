<script>
	import corpus from '../../../benchmarks/corpus.json';
	import baseline from '../../../benchmarks/baseline.json';

	const weights = [
		['Story selection', 35, 'Expected evidence operation + fixture-specific claim signal'],
		['Visual grammar', 20, 'Recommended publication visual matches the evidence operation'],
		['Claim audit', 25, 'Selected quantitative evidence recomputes from raw rows'],
		['Editorial gate', 10, 'Story spec, evaluation, and renderer compatibility remain viable'],
		['Provenance', 10, 'Draft claim_ref mappings remain complete and verified']
	];
</script>

<svelte:head>
	<title>Editorial benchmark · pudding-skill</title>
	<meta name="description" content="The deterministic v2.6 regression corpus for pudding-skill." />
</svelte:head>

<main class="benchmark-shell">
	<header class="hero">
		<p class="eyebrow">EDITORIAL BENCHMARK · V2.6</p>
		<h1>Can the pipeline find the <em>right kind of story</em> repeatedly?</h1>
		<p class="dek">
			A green demo proves one path works. This corpus asks the same system to survive {corpus.cases.length}
			different structured-data tasks, file formats, missing values, and semantic contracts without losing
			claim verification or provenance.
		</p>
		<div class="status-row" aria-label="Benchmark regression floor">
			<span>overall ≥ {baseline.minimum_overall_score}/100</span>
			<span>case pass rate {Math.round(baseline.minimum_case_pass_rate * 100)}%</span>
			<span>hard failures ≤ {baseline.max_hard_failures}</span>
		</div>
	</header>

	<section class="scorecard" aria-labelledby="scorecard-title">
		<div class="section-head">
			<p class="eyebrow">WHAT IS SCORED</p>
			<h2 id="scorecard-title">Five checks, deliberately separated.</h2>
			<p>A single high average cannot hide a broken claim audit or a missed story operation.</p>
		</div>
		<div class="weights">
			{#each weights as [label, weight, note]}
				<article>
					<strong>{weight}</strong>
					<h3>{label}</h3>
					<p>{note}</p>
				</article>
			{/each}
		</div>
	</section>

	<section class="corpus" aria-labelledby="corpus-title">
		<div class="section-head">
			<p class="eyebrow">CURATED CORPUS</p>
			<h2 id="corpus-title">{corpus.cases.length} regression cases</h2>
			<p>Expectations are explicit and reviewable. Changing one is an editorial/test-contract change, not a hidden score adjustment.</p>
		</div>
		<div class="case-grid">
			{#each corpus.cases as item, index}
				<article class="case-card">
					<div class="case-meta"><span>{String(index + 1).padStart(2, '0')}</span><code>{item.format}</code></div>
					<h3>{item.id}</h3>
					<p class="question">{item.question}</p>
					<dl>
						<div><dt>Expected operation</dt><dd>{item.expect.pattern}</dd></div>
						<div><dt>Visual grammar</dt><dd>{item.expect.visual}</dd></div>
					</dl>
				</article>
			{/each}
		</div>
	</section>

	<section class="boundary" aria-labelledby="boundary-title">
		<p class="eyebrow">BOUNDARY</p>
		<h2 id="boundary-title">This is a regression instrument, not an oracle.</h2>
		<p>
			The suite measures deterministic behavior on curated fixtures. It does not decide newsworthiness, domain importance,
			causal validity, prose craft, or whether a visual is aesthetically successful. Those remain separate editorial and screenshot-review steps.
		</p>
	</section>
</main>

<style>
	.benchmark-shell { --ink: #171717; --muted: #6b665f; --paper: #f7f3eb; --line: #d8d1c7; color: var(--ink); background: var(--paper); min-height: 100vh; padding: clamp(2rem, 5vw, 5rem) clamp(1.1rem, 5vw, 6rem) 7rem; }
	.hero, .scorecard, .corpus, .boundary { max-width: 1180px; margin-inline: auto; }
	.hero { padding: 5rem 0 6rem; border-bottom: 1px solid var(--line); }
	.eyebrow { margin: 0 0 1rem; font-family: var(--font-sans); font-size: .75rem; font-weight: 800; letter-spacing: .12em; color: #8d3d26; }
	h1, h2, h3 { font-family: var(--font-serif); }
	h1 { max-width: 900px; margin: 0; font-size: clamp(3rem, 8vw, 7.5rem); line-height: .92; letter-spacing: -.055em; }
	h1 em { font-weight: 400; color: #8d3d26; }
	.dek { max-width: 760px; margin: 2rem 0 0; font-size: clamp(1.05rem, 2vw, 1.35rem); line-height: 1.55; color: var(--muted); }
	.status-row { display: flex; flex-wrap: wrap; gap: .7rem; margin-top: 2.4rem; }
	.status-row span { border: 1px solid var(--line); border-radius: 999px; background: #fffdf8; padding: .65rem .9rem; font: 700 .82rem/1 var(--font-sans); }
	.scorecard, .corpus { padding: 6rem 0; border-bottom: 1px solid var(--line); }
	.section-head { display: grid; grid-template-columns: minmax(0, 1.1fr) minmax(260px, .9fr); gap: 2rem 4rem; align-items: end; margin-bottom: 2.5rem; }
	.section-head .eyebrow { grid-column: 1 / -1; margin-bottom: -1rem; }
	.section-head h2, .boundary h2 { margin: 0; font-size: clamp(2rem, 5vw, 4.2rem); line-height: .98; letter-spacing: -.035em; }
	.section-head > p:last-child, .boundary > p:last-child { margin: 0; color: var(--muted); line-height: 1.6; max-width: 64ch; }
	.weights { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); border: 1px solid var(--line); background: #fffdf8; }
	.weights article { padding: 1.3rem; border-right: 1px solid var(--line); }
	.weights article:last-child { border-right: 0; }
	.weights strong { display: block; font: 800 clamp(2rem, 4vw, 3.4rem)/1 var(--font-sans); color: #8d3d26; }
	.weights h3 { margin: 1rem 0 .55rem; font-size: 1.15rem; }
	.weights p, .question { margin: 0; color: var(--muted); line-height: 1.5; font-size: .92rem; }
	.case-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 1rem; }
	.case-card { min-width: 0; background: #fffdf8; border: 1px solid var(--line); border-radius: 16px; padding: 1.25rem; }
	.case-meta { display: flex; justify-content: space-between; align-items: center; font: 700 .78rem/1 var(--font-sans); color: var(--muted); }
	.case-meta code { padding: .35rem .5rem; border-radius: 6px; background: #eee8dc; color: var(--ink); }
	.case-card h3 { margin: 1.1rem 0 .65rem; font-size: 1.35rem; overflow-wrap: anywhere; }
	.case-card dl { margin: 1.1rem 0 0; padding-top: 1rem; border-top: 1px solid var(--line); }
	.case-card dl div { display: grid; grid-template-columns: 1fr 1.1fr; gap: .6rem; margin-top: .55rem; }
	dt { color: var(--muted); font: 600 .78rem/1.35 var(--font-sans); }
	dd { margin: 0; text-align: right; font: 750 .78rem/1.35 var(--font-sans); overflow-wrap: anywhere; }
	.boundary { padding: 6rem 0 0; display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem 4rem; }
	.boundary .eyebrow { grid-column: 1 / -1; margin-bottom: -.5rem; }
	@media (max-width: 900px) { .weights { grid-template-columns: repeat(2, 1fr); } .weights article { border-bottom: 1px solid var(--line); } .case-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
	@media (max-width: 620px) { .benchmark-shell { padding-inline: 1rem; } .hero { padding-top: 3rem; } .section-head, .boundary { grid-template-columns: 1fr; } .section-head .eyebrow, .boundary .eyebrow { grid-column: auto; } .weights, .case-grid { grid-template-columns: 1fr; } .weights article { border-right: 0; } .case-card dl div { grid-template-columns: 1fr; } dd { text-align: left; } }
</style>
