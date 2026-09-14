<script>
	import facts from '$data/global-mental-health-facts.json';

	const byId = Object.fromEntries(facts.facts.map((fact) => [fact.id, fact]));
	const source = (id) => facts.sources[id];

	const treatmentRows = [
		{
			label: 'Mental-health service use',
			high: 33,
			low: 8,
			highDetail: byId['mdd-service-hic'].detail,
			lowDetail: byId['mdd-service-low'].detail
		},
		{
			label: 'Minimally adequate treatment',
			high: 23,
			low: 3,
			highDetail: byId['mdd-mat-hic'].detail,
			lowDetail: byId['mdd-mat-low'].detail
		}
	];
</script>

<svelte:head>
	<title>{facts.headline} · pudding-skill</title>
	<meta
		name="description"
		content="An evidence-audited data story about the global mental-disorder burden and the unequal capacity to provide care."
	/>
</svelte:head>

<article class="story-shell">
	<section class="hero">
		<p class="kicker">GLOBAL MENTAL HEALTH · RESEARCH DOSSIER STORY</p>
		<h1>The world's <em>invisible burden</em></h1>
		<p class="dek">{facts.dek}</p>

		<div class="hero-number" aria-label="Global mental disorder prevalence in 2021">
			<strong>1.095</strong>
			<div>
				<span>billion people</span>
				<p>{byId['global-prevalence-2021'].detail}</p>
			</div>
		</div>

		<p class="source-line">
			Source:
			<a href={source('who-world-mental-health-2025').url}>{source('who-world-mental-health-2025').label}</a>
		</p>
	</section>

	<section class="conditions" aria-labelledby="conditions-title">
		<div class="section-copy narrow">
			<p class="eyebrow">WHAT SITS INSIDE 1.095 BILLION</p>
			<h2 id="conditions-title">The largest categories are familiar — but the scale is easy to miss.</h2>
		</div>
		<div class="condition-pair">
			<article>
				<p>Anxiety disorders</p>
				<strong>{byId['anxiety-2021'].value}</strong>
				<span>{byId['anxiety-2021'].detail}</span>
			</article>
			<article>
				<p>Depressive disorders</p>
				<strong>{byId['depression-2021'].value}</strong>
				<span>{byId['depression-2021'].detail}</span>
			</article>
		</div>
		<p class="source-line">
			Source:
			<a href={source('who-world-mental-health-2025').url}>{source('who-world-mental-health-2025').label}</a>
		</p>
	</section>

	<section class="burden" aria-labelledby="burden-title">
		<div class="burden-copy">
			<p class="eyebrow">WHY DEATHS MISS THE STORY</p>
			<h2 id="burden-title">Mental disorders take healthy years more often than they take lives directly.</h2>
			<p>
				GBD 2021 attributes <strong>155 million disability-adjusted life years</strong> to mental disorders — about
				<strong>5.4% of all global DALYs</strong>. The source says almost all of that burden came from years lived with
				disability rather than years of life lost.
			</p>
		</div>
		<div class="burden-stats" aria-label="Mental disorder disability burden in 2021">
			<div>
				<strong>{byId['mental-disorder-dalys'].value}</strong>
				<span>DALYs</span>
				<p>95% uncertainty interval: 117–198 million.</p>
			</div>
			<div>
				<strong>{byId['mental-disorder-daly-share'].value}</strong>
				<span>of global DALYs</span>
				<p>95% uncertainty interval: 4.3–6.5%.</p>
			</div>
		</div>
		<p class="source-line dark-source">
			Source:
			<a href={source('ihme-gbd-2021-mental-disorders').url}>{source('ihme-gbd-2021-mental-disorders').label}</a>
		</p>
	</section>

	<section class="turn" aria-labelledby="turn-title">
		<p class="eyebrow">THE TURN</p>
		<h2 id="turn-title">A billion-person need meets a system with very uneven capacity.</h2>
		<p class="lead">
			The next question is not which country can be labeled “more mentally healthy.” It is whether the systems
			around people have the money, workforce and community services to respond.
		</p>

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

	<section class="money" aria-labelledby="money-title">
		<div class="section-copy">
			<p class="eyebrow">FINANCING</p>
			<h2 id="money-title">“2.1%” is only the beginning of the funding gap.</h2>
			<p>
				Among 75 countries reporting expenditure data, WHO found a global median of just
				<strong>US$2.69 per person</strong> in government mental-health spending. Income-group medians stretch from
				<strong>US$0.04</strong> in low-income countries to <strong>US$65.89</strong> in high-income countries.
			</p>
		</div>
		<div class="money-gap" aria-label="Median government mental health spending per person by income group">
			<div class="money-end low-end">
				<span>Low income</span>
				<strong>{byId['mental-health-spend-lic'].value}</strong>
				<p>per person</p>
			</div>
			<div class="gap-line" aria-hidden="true"><i></i><b></b></div>
			<div class="money-end high-end">
				<span>High income</span>
				<strong>{byId['mental-health-spend-hic'].value}</strong>
				<p>per person</p>
			</div>
		</div>
		<p class="median-note">Global median among reporting countries: <strong>{byId['mental-health-spend-global'].value}</strong> per person.</p>
	</section>

	<section class="workforce" aria-labelledby="workforce-title">
		<div class="section-copy">
			<p class="eyebrow">WORKFORCE</p>
			<h2 id="workforce-title">A global median can hide an enormous staffing divide.</h2>
			<p>
				WHO reports a global median of 13.5 specialized mental-health workers per 100,000 people. Across low- and
				lower-middle-income settings, the summary range is only 1.1–2.4. In high-income settings, the median is 67.2.
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

	<section class="treatment" aria-labelledby="treatment-title">
		<div class="section-copy narrow">
			<p class="eyebrow">THE GAP REACHES THE PATIENT</p>
			<h2 id="treatment-title">For depression, access falls — and adequate treatment falls further.</h2>
			<p>
				A systematic review and Bayesian meta-regression covering 149 studies in 84 countries found stark income
				differences in treatment for major depressive disorder. The uncertainty is wide, especially in lower-resource
				settings, but the direction is consistent.
			</p>
		</div>

		<div class="treatment-chart" aria-label="Modeled depression treatment rates by income group">
			{#each treatmentRows as row}
				<div class="treatment-row">
					<h3>{row.label}</h3>
					<div class="treatment-series">
						<div class="treatment-item">
							<div class="treatment-label"><span>High income</span><strong>{row.high}%</strong></div>
							<div class="treatment-track"><i style={`width:${(row.high / 40) * 100}%`}></i></div>
						</div>
						<div class="treatment-item low-resource">
							<div class="treatment-label"><span>Low + lower-middle income</span><strong>{row.low}%</strong></div>
							<div class="treatment-track"><i style={`width:${(row.low / 40) * 100}%`}></i></div>
						</div>
					</div>
				</div>
			{/each}
		</div>
		<div class="caveat-box">
			<strong>Do not over-read the decimals.</strong>
			<p>
				The review reports wide uncertainty intervals and explicitly notes sparse evidence from low- and
				lower-middle-income countries. These estimates establish a treatment gap; they are not precise country scores.
			</p>
		</div>
		<p class="source-line">
			Source:
			<a href={source('plos-mdd-treatment-gap').url}>{source('plos-mdd-treatment-gap').label}</a>
		</p>
	</section>

	<section class="system" aria-labelledby="system-title">
		<div class="section-copy">
			<p class="eyebrow">SERVICE DESIGN</p>
			<h2 id="system-title">More money and staff are not the only transition still unfinished.</h2>
			<p>
				Fewer than 10% of responding countries had fully shifted from institution-based care to community-based
				models. WHO says 52.9% were still in the early stage of that transition.
			</p>
		</div>
		<div class="transition-block" aria-label="Community mental health service transition">
			<div class="transition-primary">
				<strong>&lt;10%</strong>
				<span>fully transitioned</span>
			</div>
			<div class="transition-secondary">
				<strong>52.9%</strong>
				<span>still at an early stage</span>
			</div>
		</div>
	</section>

	<section class="next-layer" aria-labelledby="next-title">
		<div>
			<p class="eyebrow">NEXT DATA LAYER · NOT A BLOCKER</p>
			<h2 id="next-title">The country burden map is now optional, not the thing holding the story hostage.</h2>
		</div>
		<div class="next-grid">
			<article>
				<span>AVAILABLE NOW</span>
				<h3>WHO capacity map</h3>
				<p>
					WHO GHO and Atlas country profiles expose workforce, financing and service-system indicators. Those can be
					extracted into a country map without waiting for IHME.
				</p>
				<code>python scripts/mental_health_story.py who</code>
			</article>
			<article>
				<span>OPTIONAL ENHANCEMENT</span>
				<h3>IHME 1990–2023 burden layer</h3>
				<p>
					If the final editorial question still needs country-level prevalence or YLD trends, submit a narrower IHME
					request and normalize the resulting export locally.
				</p>
				<code>python scripts/mental_health_story.py ihme-import YOUR_GBD_EXPORT.csv</code>
			</article>
		</div>
	</section>

	<section class="method" aria-labelledby="method-title">
		<p class="eyebrow">READ THE NUMBERS CAREFULLY</p>
		<h2 id="method-title">Burden, diagnosis, treatment and system capacity are different measurements.</h2>
		<div class="method-grid">
			<p>
				GBD prevalence is modeled from surveys, records and other evidence. It is not a registry of diagnosed cases,
				and a higher modeled prevalence should not be treated as proof that a country is simply “less mentally healthy.”
			</p>
			<p>
				WHO Atlas medians describe responding countries, not population-weighted global averages. Missing country
				responses are missing — never zero. Treatment estimates carry their own sampling and modeling uncertainty.
			</p>
			<p>
				The 2024 Atlas estimate of roughly 40% psychosis service coverage is based on only 22 countries with sufficient
				data. It is not directly comparable to the 29% figure in WHO's fact sheet based on the 2020 Atlas.
			</p>
			<p>
				The full source ledger, numeric evidence table, conflict note and acquisition plan are kept in the story's
				Research Dossier so every material number can be traced back to scope and source.
			</p>
		</div>
	</section>

	<section class="economic" aria-labelledby="economic-title">
		<p class="eyebrow">ONE LAST SCALE CHECK</p>
		<h2 id="economic-title">The burden also appears in lost time.</h2>
		<div class="economic-pair">
			<div>
				<strong>{byId['workdays-lost'].value}</strong>
				<span>productive work days lost each year</span>
			</div>
			<div>
				<strong>{byId['productivity-cost'].value}</strong>
				<span>estimated annual productivity cost</span>
			</div>
		</div>
		<p class="economic-note">
			WHO's 2025 report cites a 2016 analysis for these estimates. They are included as scale, not as a fresh 2025
			administrative count.
		</p>
	</section>

	<footer class="story-footer">
		<span>{facts.status}</span>
		<p>
			Research-backed field story · source ledger, numeric evidence and data-acquisition plan live under
			<code>stories/global-mental-health/research/</code>.
		</p>
	</footer>
</article>

<style>
	.story-shell {
		--ink: #171715;
		--muted: #68645d;
		--paper: #f5f0e7;
		--panel: #fffaf2;
		--accent: #a33f32;
		--deep: #1d211f;
		--line: #d7cfc2;
		color: var(--ink);
		background: var(--paper);
		min-height: 100vh;
	}
	.hero,
	.conditions,
	.turn,
	.money,
	.workforce,
	.treatment,
	.system,
	.next-layer,
	.method,
	.economic,
	.story-footer {
		max-width: 1180px;
		margin-inline: auto;
		padding-inline: clamp(1rem, 5vw, 5rem);
	}
	.hero { padding-top: clamp(5rem, 10vw, 10rem); padding-bottom: 8rem; }
	.kicker,
	.eyebrow { font: 800 0.76rem/1.2 var(--font-sans); letter-spacing: 0.14em; color: var(--accent); }
	h1,
	h2,
	h3 { font-family: var(--font-serif); }
	h1 { max-width: 960px; margin: 0.8rem 0 1.5rem; font-size: clamp(4rem, 11vw, 9.5rem); line-height: 0.86; letter-spacing: -0.065em; }
	h1 em { color: var(--accent); font-weight: 400; }
	.dek { max-width: 790px; margin: 0; font-size: clamp(1.15rem, 2vw, 1.55rem); line-height: 1.55; color: var(--muted); }
	.hero-number { margin-top: 6rem; padding-top: 2rem; border-top: 1px solid var(--line); display: grid; grid-template-columns: minmax(0, 1fr) minmax(280px, 0.75fr); gap: 2rem; align-items: end; }
	.hero-number > strong { font: 800 clamp(6rem, 18vw, 15rem)/0.72 var(--font-sans); letter-spacing: -0.08em; color: var(--accent); }
	.hero-number span { font: 800 clamp(1.4rem, 3vw, 2.4rem)/1 var(--font-sans); }
	.hero-number p { max-width: 42ch; margin: 1rem 0 0; color: var(--muted); line-height: 1.55; }
	.source-line { margin-top: 1.2rem; color: var(--muted); font: 600 0.8rem/1.4 var(--font-sans); }
	.source-line a { color: inherit; }
	.conditions,
	.turn,
	.money,
	.workforce,
	.treatment,
	.system,
	.next-layer,
	.method,
	.economic { padding-top: 7rem; padding-bottom: 7rem; border-top: 1px solid var(--line); }
	.section-copy.narrow { max-width: 880px; }
	.section-copy h2,
	.turn h2,
	.burden h2,
	.method h2,
	.economic h2,
	.next-layer h2 { max-width: 920px; margin: 0.8rem 0; font-size: clamp(2.6rem, 6vw, 5.8rem); line-height: 0.95; letter-spacing: -0.045em; }
	.section-copy > p:last-child,
	.burden-copy > p:last-child,
	.economic-note { color: var(--muted); line-height: 1.65; max-width: 68ch; }
	.condition-pair { margin-top: 4rem; display: grid; grid-template-columns: 1fr 1fr; border: 1px solid var(--line); background: var(--panel); }
	.condition-pair article { padding: clamp(1.5rem, 4vw, 3rem); }
	.condition-pair article + article { border-left: 1px solid var(--line); }
	.condition-pair p { margin: 0 0 1.3rem; color: var(--muted); font: 750 0.8rem/1.3 var(--font-sans); letter-spacing: 0.08em; text-transform: uppercase; }
	.condition-pair strong { display: block; font: 800 clamp(3.4rem, 8vw, 7rem)/0.9 var(--font-sans); color: var(--accent); letter-spacing: -0.055em; }
	.condition-pair span { display: block; margin-top: 1.4rem; max-width: 48ch; color: var(--muted); line-height: 1.55; }
	.burden { max-width: none; padding: 7rem max(1rem, calc((100vw - 1180px) / 2 + clamp(1rem, 5vw, 5rem))); background: var(--deep); color: #f7f3eb; }
	.burden-copy { max-width: 950px; }
	.burden-copy .eyebrow { color: #ef9986; }
	.burden-copy > p:last-child { color: #c6c9c2; font-size: 1.12rem; }
	.burden-stats { margin-top: 4rem; display: grid; grid-template-columns: 1.25fr 0.75fr; border-top: 1px solid #4a514d; border-bottom: 1px solid #4a514d; }
	.burden-stats > div { padding: 2.5rem 2rem 2.5rem 0; }
	.burden-stats > div + div { padding-left: 2rem; border-left: 1px solid #4a514d; }
	.burden-stats strong { display: block; font: 800 clamp(4rem, 10vw, 9rem)/0.85 var(--font-sans); letter-spacing: -0.07em; color: #ef9986; }
	.burden-stats span { display: block; margin-top: 1rem; font: 750 1rem/1.2 var(--font-sans); }
	.burden-stats p { color: #aeb5b0; line-height: 1.5; }
	.dark-source { color: #aeb5b0; }
	.lead { max-width: 760px; color: var(--muted); font-size: 1.25rem; line-height: 1.55; }
	.fact-grid { margin-top: 4rem; display: grid; grid-template-columns: repeat(3, 1fr); border: 1px solid var(--line); background: var(--panel); }
	.fact-grid article { padding: 1.6rem; border-right: 1px solid var(--line); }
	.fact-grid article:last-child { border-right: 0; }
	.fact-grid strong { font: 800 clamp(3rem, 7vw, 6rem)/1 var(--font-sans); color: var(--accent); }
	.fact-grid h3 { margin: 1rem 0 0.7rem; font-size: 1.35rem; }
	.fact-grid p { margin: 0; color: var(--muted); line-height: 1.5; }
	.money { display: grid; grid-template-columns: 0.9fr 1.1fr; gap: 5rem; align-items: center; }
	.money-gap { min-height: 300px; display: grid; grid-template-columns: 1fr minmax(100px, 0.45fr) 1fr; align-items: center; border: 1px solid var(--line); background: var(--panel); padding: clamp(1.5rem, 4vw, 3rem); }
	.money-end { text-align: center; }
	.money-end span { color: var(--muted); font: 750 0.8rem/1.2 var(--font-sans); text-transform: uppercase; letter-spacing: 0.08em; }
	.money-end strong { display: block; margin-top: 1rem; font: 800 clamp(3rem, 6vw, 6rem)/0.9 var(--font-sans); color: var(--accent); letter-spacing: -0.06em; }
	.money-end p { margin: 0.8rem 0 0; color: var(--muted); }
	.gap-line { height: 2px; background: var(--line); position: relative; }
	.gap-line i,
	.gap-line b { position: absolute; top: 50%; width: 12px; height: 12px; border-radius: 50%; background: var(--accent); transform: translateY(-50%); }
	.gap-line i { left: 0; }
	.gap-line b { right: 0; }
	.median-note { grid-column: 2; margin: -2rem 0 0; color: var(--muted); font-size: 0.9rem; text-align: right; }
	.workforce { display: grid; grid-template-columns: 0.85fr 1.15fr; gap: 5rem; align-items: center; }
	.workforce-scale { display: grid; gap: 1.8rem; }
	.scale-label { display: flex; justify-content: space-between; gap: 1rem; align-items: baseline; font-family: var(--font-sans); }
	.scale-label span { color: var(--muted); font-weight: 650; }
	.scale-label strong { font-size: 1.4rem; }
	.track { height: 18px; margin-top: 0.55rem; border-radius: 999px; overflow: hidden; background: #dfd7cb; }
	.track i { display: block; height: 100%; min-width: 10px; border-radius: inherit; background: var(--accent); }
	.treatment-chart { margin-top: 4rem; border: 1px solid var(--line); background: var(--panel); }
	.treatment-row { padding: 2rem; }
	.treatment-row + .treatment-row { border-top: 1px solid var(--line); }
	.treatment-row h3 { margin: 0 0 1.6rem; font-size: 1.4rem; }
	.treatment-series { display: grid; gap: 1.2rem; }
	.treatment-label { display: flex; justify-content: space-between; gap: 1rem; font: 650 0.92rem/1.3 var(--font-sans); }
	.treatment-label span { color: var(--muted); }
	.treatment-label strong { font-size: 1.25rem; }
	.treatment-track { height: 22px; margin-top: 0.45rem; background: #dfd7cb; border-radius: 999px; overflow: hidden; }
	.treatment-track i { display: block; height: 100%; background: var(--accent); border-radius: inherit; min-width: 6px; }
	.low-resource .treatment-track i { opacity: 0.48; }
	.caveat-box { margin: 1.5rem 0 0 auto; max-width: 720px; border-left: 4px solid var(--accent); padding: 1rem 0 1rem 1.4rem; }
	.caveat-box strong { font-family: var(--font-sans); }
	.caveat-box p { margin: 0.45rem 0 0; color: var(--muted); line-height: 1.55; }
	.system { display: grid; grid-template-columns: 1fr 0.85fr; gap: 5rem; align-items: center; }
	.transition-block { border: 1px solid var(--line); background: var(--panel); }
	.transition-primary,
	.transition-secondary { padding: 2rem; display: flex; justify-content: space-between; align-items: baseline; gap: 1.5rem; }
	.transition-primary { border-bottom: 1px solid var(--line); }
	.transition-block strong { font: 800 clamp(3rem, 7vw, 6rem)/0.9 var(--font-sans); color: var(--accent); }
	.transition-block span { max-width: 13ch; color: var(--muted); font: 700 0.9rem/1.35 var(--font-sans); text-align: right; }
	.next-layer { background: #ebe4d8; max-width: none; padding-left: max(1rem, calc((100vw - 1180px) / 2 + clamp(1rem, 5vw, 5rem))); padding-right: max(1rem, calc((100vw - 1180px) / 2 + clamp(1rem, 5vw, 5rem))); }
	.next-grid { margin-top: 3rem; display: grid; grid-template-columns: 1fr 1fr; gap: 1px; background: #cfc5b7; border: 1px solid #cfc5b7; }
	.next-grid article { background: var(--paper); padding: clamp(1.5rem, 4vw, 3rem); }
	.next-grid span { color: var(--accent); font: 800 0.72rem/1.2 var(--font-sans); letter-spacing: 0.1em; }
	.next-grid h3 { margin: 0.7rem 0; font-size: 2rem; }
	.next-grid p { color: var(--muted); line-height: 1.6; }
	.next-grid code { display: block; overflow-wrap: anywhere; color: var(--accent); font-size: 0.78rem; line-height: 1.5; }
	.method-grid { margin-top: 3rem; display: grid; grid-template-columns: 1fr 1fr; gap: 3rem 4rem; }
	.method-grid p { color: var(--muted); line-height: 1.7; font-size: 1.03rem; }
	.economic { border-top: 1px solid var(--line); }
	.economic-pair { margin-top: 3rem; display: grid; grid-template-columns: 1fr 1fr; border-top: 1px solid var(--line); border-bottom: 1px solid var(--line); }
	.economic-pair > div { padding: 2rem 2rem 2rem 0; }
	.economic-pair > div + div { padding-left: 2rem; border-left: 1px solid var(--line); }
	.economic-pair strong { display: block; font: 800 clamp(3.5rem, 8vw, 7rem)/0.9 var(--font-sans); letter-spacing: -0.06em; color: var(--accent); }
	.economic-pair span { display: block; margin-top: 1rem; color: var(--muted); font-weight: 650; }
	.economic-note { margin-top: 1.5rem; }
	.story-footer { padding-top: 2rem; padding-bottom: 5rem; border-top: 1px solid var(--line); display: flex; justify-content: space-between; gap: 2rem; color: var(--muted); font: 650 0.78rem/1.45 var(--font-sans); }
	.story-footer span { color: var(--accent); white-space: nowrap; }
	.story-footer p { margin: 0; max-width: 70ch; text-align: right; }
	.story-footer code { font-size: inherit; }
	@media (max-width: 760px) {
		.hero { padding-bottom: 5rem; }
		.hero-number,
		.condition-pair,
		.burden-stats,
		.money,
		.workforce,
		.system,
		.next-grid,
		.method-grid,
		.economic-pair { grid-template-columns: 1fr; }
		.hero-number { margin-top: 4rem; }
		.hero-number > strong { font-size: clamp(6.3rem, 31vw, 9rem); }
		.condition-pair article + article,
		.burden-stats > div + div,
		.economic-pair > div + div { border-left: 0; border-top: 1px solid var(--line); }
		.burden-stats > div + div { border-color: #4a514d; padding-left: 0; }
		.money { gap: 2.5rem; }
		.money-gap { grid-template-columns: 1fr; gap: 1.5rem; }
		.gap-line { width: 2px; height: 64px; margin: auto; }
		.gap-line i { top: 0; left: 50%; transform: translate(-50%, 0); }
		.gap-line b { top: auto; bottom: 0; right: auto; left: 50%; transform: translate(-50%, 0); }
		.median-note { grid-column: 1; margin: 0; text-align: left; }
		.workforce,
		.system { gap: 2.5rem; }
		.fact-grid { grid-template-columns: 1fr; }
		.fact-grid article { border-right: 0; border-bottom: 1px solid var(--line); }
		.fact-grid article:last-child { border-bottom: 0; }
		.transition-primary,
		.transition-secondary { align-items: flex-end; }
		.economic-pair > div { padding: 2rem 0; }
		.story-footer { flex-direction: column; }
		.story-footer p { text-align: left; }
	}
</style>
