<script>
	import facts from '$data/global-mental-health-facts.json';

	const byId = Object.fromEntries(facts.facts.map((fact) => [fact.id, fact]));
	const source = (id) => facts.sources[id];
</script>

<svelte:head>
	<title>{facts.headline} · pudding-skill</title>
	<meta
		name="description"
		content="A Pudding-inspired data story about global mental-disorder burden and the unequal capacity to provide care."
	/>
</svelte:head>

<article class="story-shell">
	<section class="hero">
		<p class="kicker">GLOBAL MENTAL HEALTH · FIRST FIELD STORY</p>
		<h1>The world's <em>invisible burden</em></h1>
		<p class="dek">{facts.dek}</p>
		<div class="hero-number" aria-label="Global mental disorder prevalence in 2021">
			<strong>1.1</strong>
			<div>
				<span>billion people</span>
				<p>Nearly one in every seven people worldwide were living with a mental disorder in 2021.</p>
			</div>
		</div>
		<p class="source-line">
			Source:
			<a href={source('who-mental-disorders-2025').url}>{source('who-mental-disorders-2025').label}</a>
		</p>
	</section>

	<section class="turn" aria-labelledby="turn-title">
		<p class="eyebrow">THE TURN</p>
		<h2 id="turn-title">The question is not only how many people need care.</h2>
		<p class="lead">It is whether the systems around them have the money, people and community services to respond.</p>
		<div class="fact-grid">
			<article>
				<strong>{byId['mental-health-spending'].value}</strong>
				<h3>of government health spending</h3>
				<p>{byId['mental-health-spending'].detail}</p>
			</article>
			<article>
				<strong>{byId['mental-health-workforce'].value}</strong>
				<h3>specialized workers / 100k</h3>
				<p>{byId['mental-health-workforce'].detail}</p>
			</article>
			<article>
				<strong>{byId['community-transition'].value}</strong>
				<h3>fully community-based</h3>
				<p>{byId['community-transition'].detail}</p>
			</article>
		</div>
		<p class="source-line">
			Source:
			<a href={source('who-mental-health-atlas-2024').url}>{source('who-mental-health-atlas-2024').label}</a>
		</p>
	</section>

	<section class="workforce" aria-labelledby="workforce-title">
		<div class="section-copy">
			<p class="eyebrow">CAPACITY GAP</p>
			<h2 id="workforce-title">A global median can hide a very unequal workforce.</h2>
			<p>
				WHO's 2024 Atlas reports a global median of 13.5 specialized mental-health workers per 100,000 people.
				Across low- and lower-middle-income countries, the reported range is only 1.1–2.4. In high-income
				countries, the median reaches 67.2.
			</p>
		</div>
		<div class="workforce-scale" aria-label="Specialized mental-health workers per 100,000 people">
			<div class="scale-row">
				<div class="scale-label"><span>Low + lower-middle income</span><strong>1.1–2.4</strong></div>
				<div class="track"><i style="width: 4%"></i></div>
			</div>
			<div class="scale-row">
				<div class="scale-label"><span>Global median</span><strong>13.5</strong></div>
				<div class="track"><i style="width: 20%"></i></div>
			</div>
			<div class="scale-row featured">
				<div class="scale-label"><span>High income</span><strong>67.2</strong></div>
				<div class="track"><i style="width: 100%"></i></div>
			</div>
		</div>
	</section>

	<section class="burden" aria-labelledby="burden-title">
		<div class="burden-head">
			<p class="eyebrow">NEXT DATA LAYER · 1990–2023</p>
			<h2 id="burden-title">Where is the burden — and how has it changed?</h2>
		</div>
		<div class="map-placeholder" role="img" aria-label="Reserved panel for the IHME country burden map">
			<div class="globe" aria-hidden="true"><span></span><span></span><span></span></div>
			<div>
				<strong>IHME burden layer</strong>
				<p>
					This panel is intentionally not populated with copied GBD values. The latest country estimates are modeled
					1990–2023 data whose redistribution terms require using a user-supplied IHME export.
				</p>
				<code>python scripts/mental_health_story.py ihme-import YOUR_GBD_EXPORT.csv</code>
			</div>
		</div>
		<p class="note">
			When the export is present, this becomes the main analytical sequence: age-standardized prevalence map →
			1990–2023 change → condition mix → burden × workforce mismatch.
		</p>
	</section>

	<section class="method" aria-labelledby="method-title">
		<p class="eyebrow">READ THE MAP CAREFULLY</p>
		<h2 id="method-title">A modeled prevalence estimate is not a national scorecard.</h2>
		<div class="method-grid">
			<p>
				Diagnosis, survey coverage, health-system access and statistical modeling all affect what appears in global
				mental-health estimates. A higher modeled prevalence should not be read as proof that a population is
				"less mentally healthy."
			</p>
			<p>
				The final story will keep burden estimates and service-system measurements visibly separate, then join them
				only for a clearly labeled access/capacity comparison.
			</p>
		</div>
	</section>

	<footer class="story-footer">
		<span>{facts.status}</span>
		<p>Prototype story · WHO facts are sourced; country-level GBD burden data remains local-by-design until an IHME export is supplied.</p>
	</footer>
</article>

<style>
	.story-shell { --ink:#171715; --muted:#68645d; --paper:#f5f0e7; --accent:#a33f32; --line:#d7cfc2; color:var(--ink); background:var(--paper); min-height:100vh; }
	.hero,.turn,.workforce,.burden,.method,.story-footer { max-width:1180px; margin-inline:auto; padding-inline:clamp(1rem,5vw,5rem); }
	.hero { padding-top:clamp(5rem,10vw,10rem); padding-bottom:8rem; }
	.kicker,.eyebrow { font:800 .76rem/1.2 var(--font-sans); letter-spacing:.14em; color:var(--accent); }
	h1,h2,h3 { font-family:var(--font-serif); }
	h1 { max-width:960px; margin:.8rem 0 1.5rem; font-size:clamp(4rem,11vw,9.5rem); line-height:.86; letter-spacing:-.065em; }
	h1 em { color:var(--accent); font-weight:400; }
	.dek { max-width:760px; margin:0; font-size:clamp(1.15rem,2vw,1.55rem); line-height:1.55; color:var(--muted); }
	.hero-number { margin-top:6rem; padding-top:2rem; border-top:1px solid var(--line); display:grid; grid-template-columns:minmax(0,1fr) minmax(280px,.75fr); gap:2rem; align-items:end; }
	.hero-number > strong { font:800 clamp(7rem,20vw,17rem)/.72 var(--font-sans); letter-spacing:-.08em; color:var(--accent); }
	.hero-number span { font:800 clamp(1.4rem,3vw,2.4rem)/1 var(--font-sans); }
	.hero-number p { max-width:42ch; margin:1rem 0 0; color:var(--muted); line-height:1.55; }
	.source-line { margin-top:1.2rem; color:var(--muted); font:600 .8rem/1.4 var(--font-sans); }
	.source-line a { color:inherit; }
	.turn { padding-top:7rem; padding-bottom:7rem; border-top:1px solid var(--line); }
	.turn h2,.workforce h2,.burden h2,.method h2 { max-width:900px; margin:.8rem 0; font-size:clamp(2.6rem,6vw,5.8rem); line-height:.95; letter-spacing:-.045em; }
	.lead { max-width:720px; color:var(--muted); font-size:1.25rem; line-height:1.55; }
	.fact-grid { margin-top:4rem; display:grid; grid-template-columns:repeat(3,1fr); border:1px solid var(--line); background:#fffaf2; }
	.fact-grid article { padding:1.6rem; border-right:1px solid var(--line); }
	.fact-grid article:last-child { border-right:0; }
	.fact-grid strong { font:800 clamp(3rem,7vw,6rem)/1 var(--font-sans); color:var(--accent); }
	.fact-grid h3 { margin:1rem 0 .7rem; font-size:1.35rem; }
	.fact-grid p { margin:0; color:var(--muted); line-height:1.5; }
	.workforce { padding-top:7rem; padding-bottom:7rem; border-top:1px solid var(--line); display:grid; grid-template-columns:.85fr 1.15fr; gap:5rem; align-items:center; }
	.section-copy > p:last-child { color:var(--muted); line-height:1.65; max-width:58ch; }
	.workforce-scale { display:grid; gap:1.8rem; }
	.scale-label { display:flex; justify-content:space-between; gap:1rem; align-items:baseline; font-family:var(--font-sans); }
	.scale-label span { color:var(--muted); font-weight:650; }
	.scale-label strong { font-size:1.4rem; }
	.track { height:18px; margin-top:.55rem; border-radius:999px; overflow:hidden; background:#dfd7cb; }
	.track i { display:block; height:100%; min-width:10px; border-radius:inherit; background:var(--accent); }
	.burden { padding-top:7rem; padding-bottom:7rem; border-top:1px solid var(--line); }
	.map-placeholder { margin-top:3rem; min-height:420px; border:1px solid var(--line); background:#1d211f; color:#f7f3eb; display:grid; grid-template-columns:.7fr 1fr; gap:3rem; align-items:center; padding:clamp(1.5rem,5vw,4rem); }
	.map-placeholder strong { font:700 clamp(2rem,4vw,4rem)/1 var(--font-serif); }
	.map-placeholder p { max-width:52ch; color:#c6c9c2; line-height:1.6; }
	.map-placeholder code { display:block; overflow-wrap:anywhere; color:#f0b6a9; font-size:.78rem; line-height:1.5; }
	.globe { width:min(100%,320px); aspect-ratio:1; border:1px solid #5d6962; border-radius:50%; position:relative; margin:auto; opacity:.9; }
	.globe::before,.globe::after,.globe span { content:''; position:absolute; inset:12%; border:1px solid #536059; border-radius:50%; }
	.globe::after { inset:0 35%; }
	.globe span:nth-child(1) { inset:35% 0; }
	.globe span:nth-child(2) { inset:12% 22%; }
	.globe span:nth-child(3) { inset:22% 12%; transform:rotate(90deg); }
	.note { max-width:760px; margin:1.6rem 0 0 auto; color:var(--muted); line-height:1.6; }
	.method { padding-top:7rem; padding-bottom:7rem; border-top:1px solid var(--line); }
	.method-grid { margin-top:3rem; display:grid; grid-template-columns:1fr 1fr; gap:4rem; }
	.method-grid p { color:var(--muted); line-height:1.7; font-size:1.05rem; }
	.story-footer { padding-top:2rem; padding-bottom:5rem; border-top:1px solid var(--line); display:flex; justify-content:space-between; gap:2rem; color:var(--muted); font:650 .78rem/1.45 var(--font-sans); }
	.story-footer span { color:var(--accent); white-space:nowrap; }
	.story-footer p { margin:0; max-width:70ch; text-align:right; }
	@media (max-width:760px) {
		.hero { padding-bottom:5rem; }
		.hero-number,.workforce,.map-placeholder,.method-grid { grid-template-columns:1fr; }
		.hero-number { margin-top:4rem; }
		.hero-number > strong { font-size:clamp(7rem,38vw,11rem); }
		.fact-grid { grid-template-columns:1fr; }
		.fact-grid article { border-right:0; border-bottom:1px solid var(--line); }
		.fact-grid article:last-child { border-bottom:0; }
		.workforce { gap:2.5rem; }
		.map-placeholder { min-height:0; }
		.globe { width:min(70vw,260px); }
		.story-footer { flex-direction:column; }
		.story-footer p { text-align:left; }
	}
</style>
